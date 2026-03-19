import re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import (LoginManager, UserMixin, login_user,
                         login_required, logout_user, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from db import get_db, close_db, init_db

app = Flask(__name__)
app.config.from_object(Config)
application = app

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.teardown_appcontext(close_db)



# Права по ролям


ROLE_PERMISSIONS = {
    'Администратор': [
        'create_user', 'edit_user', 'view_user',
        'delete_user', 'view_logs'
    ],
    'Пользователь': [
        'edit_own_user', 'view_own_user', 'view_own_logs'
    ]
}

def get_user_role_name(user): #Получаем название роли пользователя из бд по role_id
    if not user or not user.is_authenticated or not user.role_id:
        return None
    db = get_db()
    row = db.execute('SELECT name FROM roles WHERE id = ?',
                     (user.role_id,)).fetchone()
    return row['name'] if row else None

def has_permission(user, permission, target_user_id=None): #Проверка есть ли право
    role_name = get_user_role_name(user)
    if role_name is None:
        return False
    perms = ROLE_PERMISSIONS.get(role_name, [])

    # Прямое право — сразу разрешаем
    if permission in perms:
        return True

    # Обычный пользователь редактирует только себя
    if permission == 'edit_user' and 'edit_own_user' in perms:
        return target_user_id is not None and str(target_user_id) == str(user.id)

    # Обычный пользователь просматривает только себя
    if permission == 'view_user' and 'view_own_user' in perms:
        return target_user_id is not None and str(target_user_id) == str(user.id)

    return False


def check_rights(permission):# декоратор, который перед вызовом view-функции проверяет права через has_permission
    """Декоратор проверки прав"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('users_index'))
            # Получаем target_user_id из kwargs если есть
            target_user_id = kwargs.get('user_id')
            if not has_permission(current_user, permission, target_user_id):
                flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
                return redirect(url_for('users_index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# Модель пользователя


class User(UserMixin):
    def __init__(self, id, login, password_hash, first_name,
                 last_name=None, middle_name=None, role_id=None):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.role_id = role_id

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(p for p in parts if p)

    @property
    def role_name(self):
        return get_user_role_name(self)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if row is None:
        return None
    return User(row['id'], row['login'], row['password_hash'],
                row['first_name'], row['last_name'],
                row['middle_name'], row['role_id'])



# Журнал посещений (before_request)


@app.before_request
def log_visit():
    # Не логируем статику и сами логи
    if request.path.startswith('/static'):
        return
    if request.path.startswith('/visits'):
        return
    try:
        db = get_db()
        user_id = current_user.id if current_user.is_authenticated else None
        db.execute(
            'INSERT INTO visit_logs (path, user_id) VALUES (?, ?)',
            (request.path, user_id)
        )
        db.commit()
    except Exception:
        pass


# Валидация


def validate_login(login):
    errors = []
    if not login:
        errors.append('Поле не может быть пустым.')
    elif not re.fullmatch(r'[a-zA-Z0-9]{5,}', login):
        errors.append('Логин должен содержать только латинские буквы и цифры, минимум 5 символов.')
    return errors

def validate_password(password):
    errors = []
    allowed_special = r'~!?@#$%^&*_\-+()\[\]{}<>/\\|"\'.,:;'
    if not password:
        errors.append('Поле не может быть пустым.')
        return errors
    if len(password) < 8:
        errors.append('Пароль должен содержать не менее 8 символов.')
    if len(password) > 128:
        errors.append('Пароль должен содержать не более 128 символов.')
    if not re.search(r'[A-ZА-ЯЁ]', password):
        errors.append('Пароль должен содержать хотя бы одну заглавную букву.')
    if not re.search(r'[a-zа-яё]', password):
        errors.append('Пароль должен содержать хотя бы одну строчную букву.')
    if not re.search(r'[0-9]', password):
        errors.append('Пароль должен содержать хотя бы одну цифру.')
    if re.search(r'\s', password):
        errors.append('Пароль не должен содержать пробелы.')
    if not re.fullmatch(rf'[a-zA-Zа-яА-ЯёЁ0-9{allowed_special}]+', password):
        errors.append('Пароль содержит недопустимые символы.')
    return errors

def validate_user_form(form, is_create=True):
    field_errors = {}
    if is_create:
        login_errors = validate_login(form.get('login', '').strip())
        if login_errors:
            field_errors['login'] = login_errors
        password_errors = validate_password(form.get('password', ''))
        if password_errors:
            field_errors['password'] = password_errors
    if not form.get('first_name', '').strip():
        field_errors['first_name'] = ['Поле не может быть пустым.']
    return field_errors



# Аутентификация


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form
        db = get_db()
        row = db.execute('SELECT * FROM users WHERE login = ?',
                         (login_val,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            user = User(row['id'], row['login'], row['password_hash'],
                        row['first_name'], row['last_name'],
                        row['middle_name'], row['role_id'])
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('users_index'))
        else:
            flash('Неверный логин или пароль!', 'danger')
    return render_template('login.html', title='Вход')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('users_index'))



# Главная — список пользователей


@app.route('/')
def users_index():
    db = get_db()
    users = db.execute('''
        SELECT u.*, r.name as role_name
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        ORDER BY u.id
    ''').fetchall()
    return render_template('users/index.html',
                           title='Пользователи',
                           users=users,
                           has_permission=has_permission)



# Просмотр пользователя


@app.route('/users/<int:user_id>')
@check_rights('view_user')
def user_view(user_id):
    db = get_db()
    user = db.execute('''
        SELECT u.*, r.name as role_name
        FROM users u
        LEFT JOIN roles r ON u.role_id = r.id
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    if user is None:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('users_index'))
    return render_template('users/view.html',
                           title='Просмотр пользователя', user=user)



# Создание пользователя

@app.route('/users/create', methods=['GET', 'POST'])
@check_rights('create_user')
def user_create():
    db = get_db()
    roles = db.execute('SELECT * FROM roles').fetchall()
    form_data = {}
    field_errors = {}
    if request.method == 'POST':
        form_data = request.form
        field_errors = validate_user_form(form_data, is_create=True)
        if not field_errors:
            try:
                db.execute('''
                    INSERT INTO users
                    (login, password_hash, last_name, first_name, middle_name, role_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    form_data['login'].strip(),
                    generate_password_hash(form_data['password']),
                    form_data.get('last_name', '').strip() or None,
                    form_data['first_name'].strip(),
                    form_data.get('middle_name', '').strip() or None,
                    form_data.get('role_id') or None
                ))
                db.commit()
                flash('Пользователь успешно создан!', 'success')
                return redirect(url_for('users_index'))
            except Exception as e:
                db.rollback()
                flash(f'Ошибка при создании пользователя: {e}', 'danger')
    return render_template('users/create.html', title='Создание пользователя',
                           roles=roles, form_data=form_data,
                           field_errors=field_errors)



# Редактирование пользователя


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@check_rights('edit_user')
def user_edit(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?',
                      (user_id,)).fetchone()
    if user is None:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('users_index'))

    roles = db.execute('SELECT * FROM roles').fetchall()
    field_errors = {}
    form_data = dict(user)
    # Может ли текущий пользователь менять роль
    role_name = get_user_role_name(current_user)
    can_change_role = (role_name == 'Администратор')

    if request.method == 'POST':
        form_data = request.form
        field_errors = validate_user_form(form_data, is_create=False)
        if not field_errors:
            try:
                new_role_id = form_data.get('role_id') or None
                if not can_change_role:
                    new_role_id = user['role_id']  # роль не меняется
                db.execute('''
                    UPDATE users
                    SET last_name=?, first_name=?, middle_name=?, role_id=?
                    WHERE id=?
                ''', (
                    form_data.get('last_name', '').strip() or None,
                    form_data['first_name'].strip(),
                    form_data.get('middle_name', '').strip() or None,
                    new_role_id,
                    user_id
                ))
                db.commit()
                flash('Пользователь успешно обновлён!', 'success')
                return redirect(url_for('users_index'))
            except Exception as e:
                db.rollback()
                flash(f'Ошибка при обновлении: {e}', 'danger')

    return render_template('users/edit.html',
                           title='Редактирование пользователя',
                           user=user, roles=roles,
                           form_data=form_data,
                           field_errors=field_errors,
                           can_change_role=can_change_role)


# Удаление пользователя


@app.route('/users/<int:user_id>/delete', methods=['POST'])
@check_rights('delete_user')
def user_delete(user_id):
    db = get_db()
    try:
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
        flash('Пользователь успешно удалён.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('users_index'))


# Смена пароля


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    field_errors = {}
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not check_password_hash(current_user.password_hash, old_password):
            field_errors['old_password'] = ['Неверный текущий пароль.']
        password_errors = validate_password(new_password)
        if password_errors:
            field_errors['new_password'] = password_errors
        if new_password != confirm_password:
            field_errors['confirm_password'] = ['Пароли не совпадают.']

        if not field_errors:
            try:
                db = get_db()
                db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
                           (generate_password_hash(new_password), current_user.id))
                db.commit()
                flash('Пароль успешно изменён!', 'success')
                return redirect(url_for('users_index'))
            except Exception as e:
                flash(f'Ошибка: {e}', 'danger')

    return render_template('change_password.html',
                           title='Изменение пароля',
                           field_errors=field_errors)



# Подключение Blueprint


from visits.views import visits_bp
app.register_blueprint(visits_bp, url_prefix='/visits')


# Передача has_permission в шаблоны


@app.context_processor
def inject_permissions():
    return dict(has_permission=has_permission)


if __name__ == '__main__':
    init_db(app)
    with app.app_context():
        db = get_db()
        db.execute("UPDATE users SET password_hash=? WHERE login='admin'",
                   (generate_password_hash('Admin123'),))
        db.commit()
    app.run(debug=True)

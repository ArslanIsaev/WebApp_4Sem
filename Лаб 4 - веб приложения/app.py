# import re
# from flask import Flask, render_template, request, redirect, url_for, flash, g
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
# from config import Config
# from db import get_db, close_db, init_db

# app = Flask(__name__)
# app.config.from_object(Config)
# application = app

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# app.teardown_appcontext(close_db)


# # Модель пользователя
# class User(UserMixin):
#     def __init__(self, id, login, password_hash, first_name, last_name=None,
#                  middle_name=None, role_id=None):
#         self.id = id
#         self.login = login
#         self.password_hash = password_hash
#         self.first_name = first_name
#         self.last_name = last_name
#         self.middle_name = middle_name
#         self.role_id = role_id

#     @property
#     def full_name(self):
#         parts = [self.last_name, self.first_name, self.middle_name]
#         return ' '.join(p for p in parts if p)

# # Загрузчик пользователя
# @login_manager.user_loader
# def load_user(user_id):
#     db = get_db()
#     row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#     if row is None:
#         return None
#     return User(row['id'], row['login'], row['password_hash'],
#                 row['first_name'], row['last_name'],
#                 row['middle_name'], row['role_id'])


# # Валидация


# def validate_login(login):
#     errors = []
#     if not login:
#         errors.append('Поле не может быть пустым.')
#     elif not re.fullmatch(r'[a-zA-Z0-9]{5,}', login):
#         errors.append('Логин должен содержать только латинские буквы и цифры, минимум 5 символов.')
#     return errors

# def validate_password(password):
#     errors = []
#     allowed_special = r'~!?@#$%^&*_\-+()\[\]{}<>/\\|"\'.,:;'
#     if not password:
#         errors.append('Поле не может быть пустым.')
#         return errors
#     if len(password) < 8:
#         errors.append('Пароль должен содержать не менее 8 символов.')
#     if len(password) > 128:
#         errors.append('Пароль должен содержать не более 128 символов.')
#     if not re.search(r'[A-ZА-ЯЁ]', password):
#         errors.append('Пароль должен содержать хотя бы одну заглавную букву.')
#     if not re.search(r'[a-zа-яё]', password):
#         errors.append('Пароль должен содержать хотя бы одну строчную букву.')
#     if not re.search(r'[0-9]', password):
#         errors.append('Пароль должен содержать хотя бы одну цифру.')
#     if re.search(r'\s', password):
#         errors.append('Пароль не должен содержать пробелы.')
#     if not re.fullmatch(rf'[a-zA-Zа-яА-ЯёЁ0-9{allowed_special}]+', password):
#         errors.append('Пароль содержит недопустимые символы.')
#     return errors

# def validate_user_form(form, is_create=True):
#     """Возвращает словарь {поле: [ошибки]}"""
#     field_errors = {}

#     if is_create:
#         login_errors = validate_login(form.get('login', '').strip())
#         if login_errors:
#             field_errors['login'] = login_errors

#         password_errors = validate_password(form.get('password', ''))
#         if password_errors:
#             field_errors['password'] = password_errors

#     if not form.get('first_name', '').strip():
#         field_errors['first_name'] = ['Поле не может быть пустым.']

#     return field_errors



# # Аутентификация


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         login_val = request.form.get('username', '').strip()
#         password = request.form.get('password', '')
#         remember = 'remember' in request.form

#         db = get_db()
#         row = db.execute('SELECT * FROM users WHERE login = ?', (login_val,)).fetchone()

#         if row and check_password_hash(row['password_hash'], password):
#             user = User(row['id'], row['login'], row['password_hash'],
#                         row['first_name'], row['last_name'],
#                         row['middle_name'], row['role_id'])
#             login_user(user, remember=remember)
#             flash('Вы успешно вошли в систему!', 'success')
#             return redirect(url_for('users_index'))
#         else:
#             flash('Неверный логин или пароль!', 'danger')

#     return render_template('login.html', title='Вход')


# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('Вы вышли из системы.', 'info')
#     return redirect(url_for('users_index'))



# # Главная — список пользователей


# @app.route('/')
# def users_index():
#     db = get_db()
#     users = db.execute('''
#         SELECT u.*, r.name as role_name
#         FROM users u
#         LEFT JOIN roles r ON u.role_id = r.id
#         ORDER BY u.id
#     ''').fetchall()
#     return render_template('users/index.html', title='Пользователи', users=users)



# # Просмотр пользователя


# @app.route('/users/<int:user_id>')
# def user_view(user_id):
#     db = get_db()
#     user = db.execute('''
#         SELECT u.*, r.name as role_name
#         FROM users u
#         LEFT JOIN roles r ON u.role_id = r.id
#         WHERE u.id = ?
#     ''', (user_id,)).fetchone()
#     if user is None:
#         flash('Пользователь не найден.', 'danger')
#         return redirect(url_for('users_index'))
#     return render_template('users/view.html', title='Просмотр пользователя', user=user)



# # Создание пользователя


# @app.route('/users/create', methods=['GET', 'POST'])
# @login_required
# def user_create():
#     db = get_db()
#     roles = db.execute('SELECT * FROM roles').fetchall()
#     form_data = {}
#     field_errors = {}

#     if request.method == 'POST':
#         form_data = request.form
#         field_errors = validate_user_form(form_data, is_create=True)

#         if not field_errors:
#             try:
#                 db.execute('''
#                     INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 ''', (
#                     form_data['login'].strip(),
#                     generate_password_hash(form_data['password']),
#                     form_data.get('last_name', '').strip() or None,
#                     form_data['first_name'].strip(),
#                     form_data.get('middle_name', '').strip() or None,
#                     form_data.get('role_id') or None
#                 ))
#                 db.commit()
#                 flash('Пользователь успешно создан!', 'success')
#                 return redirect(url_for('users_index'))
#             except Exception as e:
#                 db.rollback()
#                 flash(f'Ошибка при создании пользователя: {e}', 'danger')

#     return render_template('users/create.html', title='Создание пользователя',
#                            roles=roles, form_data=form_data, field_errors=field_errors)



# # Редактирование пользователя


# @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
# @login_required
# def user_edit(user_id):
#     db = get_db()
#     user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
#     if user is None:
#         flash('Пользователь не найден.', 'danger')
#         return redirect(url_for('users_index'))

#     roles = db.execute('SELECT * FROM roles').fetchall()
#     field_errors = {}
#     form_data = dict(user)

#     if request.method == 'POST':
#         form_data = request.form
#         field_errors = validate_user_form(form_data, is_create=False)

#         if not field_errors:
#             try:
#                 db.execute('''
#                     UPDATE users
#                     SET last_name=?, first_name=?, middle_name=?, role_id=?
#                     WHERE id=?
#                 ''', (
#                     form_data.get('last_name', '').strip() or None,
#                     form_data['first_name'].strip(),
#                     form_data.get('middle_name', '').strip() or None,
#                     form_data.get('role_id') or None,
#                     user_id
#                 ))
#                 db.commit()
#                 flash('Пользователь успешно обновлён!', 'success')
#                 return redirect(url_for('users_index'))
#             except Exception as e:
#                 db.rollback()
#                 flash(f'Ошибка при обновлении пользователя: {e}', 'danger')

#     return render_template('users/edit.html', title='Редактирование пользователя',
#                            user=user, roles=roles,
#                            form_data=form_data, field_errors=field_errors)



# # Удаление пользователя


# @app.route('/users/<int:user_id>/delete', methods=['POST'])
# @login_required
# def user_delete(user_id):
#     db = get_db()
#     try:
#         db.execute('DELETE FROM users WHERE id = ?', (user_id,))
#         db.commit()
#         flash('Пользователь успешно удалён.', 'success')
#     except Exception as e:
#         db.rollback()
#         flash(f'Ошибка при удалении: {e}', 'danger')
#     return redirect(url_for('users_index'))



# # Смена пароля


# @app.route('/change-password', methods=['GET', 'POST'])
# @login_required
# def change_password():
#     field_errors = {}

#     if request.method == 'POST':
#         old_password = request.form.get('old_password', '')
#         new_password = request.form.get('new_password', '')
#         confirm_password = request.form.get('confirm_password', '')

#         if not check_password_hash(current_user.password_hash, old_password):
#             field_errors['old_password'] = ['Неверный текущий пароль.']

#         password_errors = validate_password(new_password)
#         if password_errors:
#             field_errors['new_password'] = password_errors

#         if new_password != confirm_password:
#             field_errors['confirm_password'] = ['Пароли не совпадают.']

#         if not field_errors:
#             try:
#                 db = get_db()
#                 db.execute('UPDATE users SET password_hash = ? WHERE id = ?',
#                            (generate_password_hash(new_password), current_user.id))
#                 db.commit()
#                 flash('Пароль успешно изменён!', 'success')
#                 return redirect(url_for('users_index'))
#             except Exception as e:
#                 flash(f'Ошибка при смене пароля: {e}', 'danger')

#     return render_template('change_password.html',
#                            title='Изменение пароля',
#                            field_errors=field_errors)



# # Инициализация БД и запуск

# if __name__ == '__main__':
#     init_db(app)
#     app.run(debug=True)










































import re
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
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



# Модель пользователя

class User(UserMixin):
    def __init__(self, id, login, password_hash, first_name, last_name=None,
                 middle_name=None, role_id=None):
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


# Загрузчик пользователя

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    row = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if row is None:
        return None
    return User(row['id'], row['login'], row['password_hash'],
                row['first_name'], row['last_name'],
                row['middle_name'], row['role_id'])



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


def validate_name_field(value):
    errors = []
    if not value or not value.strip():
        errors.append('Поле не может быть пустым.')
        return errors
    if not re.fullmatch(r'[a-zA-Z]+', value.strip()):
        errors.append('Поле должно содержать только латинские буквы, без пробелов и спецсимволов.')
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

    # Имя — обязательное
    first_name_errors = validate_name_field(form.get('first_name', ''))
    if first_name_errors:
        field_errors['first_name'] = first_name_errors

    # Фамилия — необязательная, но если заполнена — валидируем
    last_name = form.get('last_name', '').strip()
    if last_name:
        last_name_errors = validate_name_field(last_name)
        if last_name_errors:
            field_errors['last_name'] = last_name_errors

    # Отчество — необязательное, но если заполнено — валидируем
    middle_name = form.get('middle_name', '').strip()
    if middle_name:
        middle_name_errors = validate_name_field(middle_name)
        if middle_name_errors:
            field_errors['middle_name'] = middle_name_errors

    return field_errors



# Аутентификация



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_val = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form

        db = get_db()
        row = db.execute('SELECT * FROM users WHERE login = ?', (login_val,)).fetchone()

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
    return render_template('users/index.html', title='Пользователи', users=users)



# Просмотр пользователя



@app.route('/users/<int:user_id>')
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
    return render_template('users/view.html', title='Просмотр пользователя', user=user)



# Создание пользователя



@app.route('/users/create', methods=['GET', 'POST'])
@login_required
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
                    INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)
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
                           roles=roles, form_data=form_data, field_errors=field_errors)



# Редактирование пользователя



@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user is None:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('users_index'))

    roles = db.execute('SELECT * FROM roles').fetchall()
    field_errors = {}
    form_data = dict(user)

    if request.method == 'POST':
        form_data = request.form
        field_errors = validate_user_form(form_data, is_create=False)

        if not field_errors:
            try:
                db.execute('''
                    UPDATE users
                    SET last_name=?, first_name=?, middle_name=?, role_id=?
                    WHERE id=?
                ''', (
                    form_data.get('last_name', '').strip() or None,
                    form_data['first_name'].strip(),
                    form_data.get('middle_name', '').strip() or None,
                    form_data.get('role_id') or None,
                    user_id
                ))
                db.commit()
                flash('Пользователь успешно обновлён!', 'success')
                return redirect(url_for('users_index'))
            except Exception as e:
                db.rollback()
                flash(f'Ошибка при обновлении пользователя: {e}', 'danger')

    return render_template('users/edit.html', title='Редактирование пользователя',
                           user=user, roles=roles,
                           form_data=form_data, field_errors=field_errors)



# Удаление пользователя



@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
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
                flash(f'Ошибка при смене пароля: {e}', 'danger')

    return render_template('change_password.html',
                           title='Изменение пароля',
                           field_errors=field_errors)



# Инициализация БД и запуск

if __name__ == '__main__':
    init_db(app)
    app.run(debug=True)

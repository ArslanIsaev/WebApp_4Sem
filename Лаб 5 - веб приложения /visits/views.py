import csv
import io
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, make_response)
from flask_login import current_user
from db import get_db
from functools import wraps

visits_bp = Blueprint('visits', __name__,
                      template_folder='../templates/visits')

PER_PAGE = 10


def check_visits_access(f):
    """Декоратор: Администратор видит всё, Пользователь — только своё"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('У вас недостаточно прав для доступа к данной странице.', 'danger')
            return redirect(url_for('users_index'))
        return f(*args, **kwargs)
    return decorated


def is_admin():
    if not current_user.is_authenticated:
        return False
    db = get_db()
    row = db.execute('''
        SELECT r.name FROM roles r
        JOIN users u ON u.role_id = r.id
        WHERE u.id = ?
    ''', (current_user.id,)).fetchone()
    return row and row['name'] == 'Администратор'


# ========================
# Главная журнала посещений
# ========================

@visits_bp.route('/')
@check_visits_access
def index():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PER_PAGE

    if is_admin():
        total = db.execute('SELECT COUNT(*) FROM visit_logs').fetchone()[0]
        logs = db.execute('''
            SELECT vl.*, u.last_name, u.first_name, u.middle_name
            FROM visit_logs vl
            LEFT JOIN users u ON vl.user_id = u.id
            ORDER BY vl.created_at DESC
            LIMIT ? OFFSET ?
        ''', (PER_PAGE, offset)).fetchall()
    else:
        total = db.execute(
            'SELECT COUNT(*) FROM visit_logs WHERE user_id = ?',
            (current_user.id,)
        ).fetchone()[0]
        logs = db.execute('''
            SELECT vl.*, u.last_name, u.first_name, u.middle_name
            FROM visit_logs vl
            LEFT JOIN users u ON vl.user_id = u.id
            WHERE vl.user_id = ?
            ORDER BY vl.created_at DESC
            LIMIT ? OFFSET ?
        ''', (current_user.id, PER_PAGE, offset)).fetchall()

    total_pages = (total + PER_PAGE - 1) // PER_PAGE

    return render_template('visits/index.html',
                           title='Журнал посещений',
                           logs=logs,
                           page=page,
                           total_pages=total_pages)


# ========================
# Отчёт по страницам
# ========================

@visits_bp.route('/by-pages')
@check_visits_access
def by_pages():
    db = get_db()
    rows = db.execute('''
        SELECT path, COUNT(*) as cnt
        FROM visit_logs
        GROUP BY path
        ORDER BY cnt DESC
    ''').fetchall()
    return render_template('visits/by_pages.html',
                           title='Отчёт по страницам',
                           rows=rows)


@visits_bp.route('/by-pages/export')
@check_visits_access
def by_pages_export():
    db = get_db()
    rows = db.execute('''
        SELECT path, COUNT(*) as cnt
        FROM visit_logs
        GROUP BY path
        ORDER BY cnt DESC
    ''').fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    for i, row in enumerate(rows, 1):
        writer.writerow([i, row['path'], row['cnt']])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=by_pages.csv'
    return response


# ========================
# Отчёт по пользователям
# ========================

@visits_bp.route('/by-users')
@check_visits_access
def by_users():
    db = get_db()
    rows = db.execute('''
        SELECT u.last_name, u.first_name, u.middle_name,
               COUNT(*) as cnt
        FROM visit_logs vl
        LEFT JOIN users u ON vl.user_id = u.id
        GROUP BY vl.user_id
        ORDER BY cnt DESC
    ''').fetchall()
    return render_template('visits/by_users.html',
                           title='Отчёт по пользователям',
                           rows=rows)


@visits_bp.route('/by-users/export')
@check_visits_access
def by_users_export():
    db = get_db()
    rows = db.execute('''
        SELECT u.last_name, u.first_name, u.middle_name,
               COUNT(*) as cnt
        FROM visit_logs vl
        LEFT JOIN users u ON vl.user_id = u.id
        GROUP BY vl.user_id
        ORDER BY cnt DESC
    ''').fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    for i, row in enumerate(rows, 1):
        parts = [row['last_name'], row['first_name'], row['middle_name']]
        full = ' '.join(p for p in parts if p) or 'Неаутентифицированный пользователь'
        writer.writerow([i, full, row['cnt']])

    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=by_users.csv'
    return response

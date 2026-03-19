from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, Course, Category, User, Review
from tools import CoursesFilter, ImageSaver

bp = Blueprint('courses', __name__, url_prefix='/courses')

COURSE_PARAMS = [
    'author_id', 'name', 'category_id', 'short_desc', 'full_desc'
]

RATING_LABELS = {
    5: 'Отлично',
    4: 'Хорошо',
    3: 'Удовлетворительно',
    2: 'Неудовлетворительно',
    1: 'Плохо',
    0: 'Ужасно',
}

def params():
    return { p: request.form.get(p) or None for p in COURSE_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': [x for x in request.args.getlist('category_ids') if x],
    }

@bp.route('/')
def index():
    courses = CoursesFilter(**search_params()).perform()
    pagination = db.paginate(courses)
    courses = pagination.items
    categories = db.session.execute(db.select(Category)).scalars()
    return render_template('courses/index.html',
        courses=courses,
        categories=categories,
        pagination=pagination,
        search_params=search_params())

@bp.route('/new')
@login_required
def new():
    course = Course()
    categories = db.session.execute(db.select(Category)).scalars()
    users = db.session.execute(db.select(User)).scalars()
    return render_template('courses/new.html',
        categories=categories,
        users=users,
        course=course)

@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img')
    img = None
    course = Course()
    try:
        if f and f.filename:
            img = ImageSaver(f).save()

        image_id = img.id if img else None
        course = Course(**params(), background_image_id=image_id)
        db.session.add(course)
        db.session.commit()
    except IntegrityError as err:
        flash(f'Возникла ошибка при записи данных в БД. Проверьте корректность введённых данных. ({err})', 'danger')
        db.session.rollback()
        categories = db.session.execute(db.select(Category)).scalars()
        users = db.session.execute(db.select(User)).scalars()
        return render_template('courses/new.html',
            categories=categories,
            users=users,
            course=course)

    flash(f'Курс {course.name} был успешно добавлен!', 'success')
    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    course = db.get_or_404(Course, course_id)

    # 5 последних отзывов
    last_reviews = db.session.execute(
        db.select(Review)
          .filter_by(course_id=course_id)
          .order_by(Review.created_at.desc())
          .limit(5)
    ).scalars().all()

    # Отзыв текущего пользователя (если авторизован)
    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
        ).scalar()

    return render_template('courses/show.html',
        course=course,
        last_reviews=last_reviews,
        user_review=user_review,
        rating_labels=RATING_LABELS)

@bp.route('/<int:course_id>/reviews')
def reviews(course_id):
    course = db.get_or_404(Course, course_id)
    sort = request.args.get('sort', 'new')

    query = db.select(Review).filter_by(course_id=course_id)

    if sort == 'positive':
        query = query.order_by(Review.rating.desc())
    elif sort == 'negative':
        query = query.order_by(Review.rating.asc())
    else:  # 'new' — по умолчанию
        query = query.order_by(Review.created_at.desc())

    pagination = db.paginate(query, per_page=5)
    all_reviews = pagination.items

    user_review = None
    if current_user.is_authenticated:
        user_review = db.session.execute(
            db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
        ).scalar()

    return render_template('courses/reviews.html',
        course=course,
        reviews=all_reviews,
        pagination=pagination,
        sort=sort,
        user_review=user_review,
        rating_labels=RATING_LABELS)

@bp.route('/<int:course_id>/reviews/create', methods=['POST'])
@login_required
def create_review(course_id):
    course = db.get_or_404(Course, course_id)

    # Проверка: не оставлял ли уже отзыв
    existing = db.session.execute(
        db.select(Review).filter_by(course_id=course_id, user_id=current_user.id)
    ).scalar()
    if existing:
        flash('Вы уже оставляли отзыв к этому курсу.', 'warning')
        return redirect(request.referrer or url_for('courses.show', course_id=course_id))

    rating = int(request.form.get('rating', 5))
    text = request.form.get('text', '').strip()

    review = Review(
        rating=rating,
        text=text,
        course_id=course_id,
        user_id=current_user.id
    )
    db.session.add(review)

    # Пересчёт рейтинга курса
    course.rating_sum += rating
    course.rating_num += 1

    db.session.commit()
    flash('Ваш отзыв успешно добавлен!', 'success')

    # Возвращаем туда, откуда пришли
    next_url = request.form.get('next') or url_for('courses.show', course_id=course_id)
    return redirect(next_url)

from app import app
from models import db, Category, Course, User

with app.app_context():
    # Очищаем старые данные
    db.session.query(Course).delete()
    db.session.query(Category).delete()
    db.session.commit()

    # Категории
    cat1 = Category(name='Программирование')
    cat2 = Category(name='Математика')
    cat3 = Category(name='Иностранные языки')
    db.session.add_all([cat1, cat2, cat3])
    db.session.commit()

    # Пользователь
    user = db.session.execute(db.select(User)).scalar()

    # Курсы
    courses = [
        Course(name='Python для начинающих',
               short_desc='Базовый курс по языку Python',
               full_desc='Полный курс по Python: переменные, циклы, функции, ООП, работа с файлами и библиотеками.',
               category_id=cat1.id, author_id=user.id, background_image_id=None),
        Course(name='Веб-разработка на Flask',
               short_desc='Создание веб-приложений на Flask',
               full_desc='Изучите Flask: маршруты, шаблоны Jinja2, работа с базами данных через SQLAlchemy, аутентификация.',
               category_id=cat1.id, author_id=user.id, background_image_id=None),
        Course(name='JavaScript с нуля',
               short_desc='Основы JavaScript для веб-разработки',
               full_desc='Курс охватывает основы JS: типы данных, функции, DOM, события, fetch и асинхронность.',
               category_id=cat1.id, author_id=user.id, background_image_id=None),
        Course(name='Линейная алгебра',
               short_desc='Векторы, матрицы и линейные преобразования',
               full_desc='Подробный курс по линейной алгебре: матрицы, определители, собственные значения, применение в ML.',
               category_id=cat2.id, author_id=user.id, background_image_id=None),
        Course(name='Математический анализ',
               short_desc='Пределы, производные и интегралы',
               full_desc='Курс охватывает пределы, производные, интегралы, ряды и дифференциальные уравнения.',
               category_id=cat2.id, author_id=user.id, background_image_id=None),
        Course(name='Английский язык — Intermediate',
               short_desc='Английский для среднего уровня',
               full_desc='Грамматика, лексика, разговорная практика и чтение на уровне B1-B2.',
               category_id=cat3.id, author_id=user.id, background_image_id=None),
        Course(name='Немецкий язык для начинающих',
               short_desc='Немецкий с нуля',
               full_desc='Алфавит, базовая грамматика, приветствия, числа, дни недели и простые диалоги на немецком.',
               category_id=cat3.id, author_id=user.id, background_image_id=None),
    ]

    db.session.add_all(courses)
    db.session.commit()
    print(f'Готово! Категорий: 3, курсов: {len(courses)}')

import random
import re
from flask import Flask, render_template, request, make_response

from faker import Faker

fake = Faker()

app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = {'author': fake.name(), 'text': fake.text()}
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')


# 1. Отображение данных запроса
@app.route('/request-info')
def request_info():
    return render_template('request_info.html',
                           title='Данные запроса',
                           url_params=request.args,
                           headers=request.headers,
                           cookies=request.cookies)

# 2. Форма авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    form_data = None
    if request.method == 'POST':
        form_data = {
            'username': request.form.get('username', ''),
            'password': request.form.get('password', '')
        }
    return render_template('login.html', title='Авторизация', form_data=form_data)


# 3. Форма с проверкой номера телефона
def validate_phone(phone):
   
    # Проверяем на недопустимые символы
    if re.search(r'[^\d\s\(\)\-\.\+]', phone):
        return None, 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'

    # Извлекаем только цифры
    digits = re.sub(r'\D', '', phone)

    # Определяем нужное количество цифр
    stripped = phone.strip()
    if stripped.startswith('+7') or stripped.startswith('8'):
        required = 11
    else:
        required = 10

    if len(digits) != required:
        return None, 'Недопустимый ввод. Неверное количество цифр.'


    if len(digits) == 10:
        digits = '8' + digits

    formatted = f'8-{digits[1:4]}-{digits[4:7]}-{digits[7:9]}-{digits[9:11]}'
    return formatted, None


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone_input = ''
    formatted = None
    error = None

    if request.method == 'POST':
        phone_input = request.form.get('phone', '')
        formatted, error = validate_phone(phone_input)

    return render_template('phone.html',
                           title='Проверка номера телефона',
                           phone_input=phone_input,
                           formatted=formatted,
                           error=error)


if __name__ == '__main__':
    app.run(debug=True)

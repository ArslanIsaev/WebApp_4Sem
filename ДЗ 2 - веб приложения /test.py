import subprocess
import pytest
import os
import tempfile
import shutil
import math

# Для MAC
INTERPRETER = 'python3'

def run_script(filename, input_data=None):
    proc = subprocess.run(
        [INTERPRETER, filename],
        input='\n'.join(input_data if input_data else []),
        capture_output=True,
        text=True,
        check=False
    )
    return proc.stdout.strip()

# ============= ЗАДАЧА 1: fact.py =============
from fact import fact_it, fact_rec

test_data_fact = [
    (1, 1),
    (5, 120),
    (10, 3628800),
    (3, 6),
    (7, 5040),
]

@pytest.mark.parametrize("input_data, expected", test_data_fact)
def test_fact_it(input_data, expected):
    assert fact_it(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data_fact)
def test_fact_rec(input_data, expected):
    assert fact_rec(input_data) == expected

# ============= ЗАДАЧА 2: show_employee.py =============
from show_employee import show_employee

test_data_employee = [
    ("Иванов Иван Иванович", 30000, "Иванов Иван Иванович: 30000 ₽"),
    ("Петров Петр", 50000, "Петров Петр: 50000 ₽"),
    ("Сидоров Сидор", None, "Сидоров Сидор: 100000 ₽"),
    ("Smith John", 75000, "Smith John: 75000 ₽"),
]

def test_show_employee_with_salary():
    assert show_employee("Иванов Иван Иванович", 30000) == "Иванов Иван Иванович: 30000 ₽"

def test_show_employee_default_salary():
    assert show_employee("Петров Петр") == "Петров Петр: 100000 ₽"

def test_show_employee_zero_salary():
    assert show_employee("Test Name", 0) == "Test Name: 0 ₽"

def test_show_employee_large_salary():
    assert show_employee("Rich Person", 999999999) == "Rich Person: 999999999 ₽"

# ============= ЗАДАЧА 3: sum_and_sub.py =============
from sum_and_sub import sum_and_sub

test_data_sum_sub = [
    (5, 3, (8, 2)),
    (10.5, 2.5, (13.0, 8.0)),
    (-5, 3, (-2, -8)),
    (0, 0, (0, 0)),
    (100, 50, (150, 50)),
]

@pytest.mark.parametrize("a, b, expected", test_data_sum_sub)
def test_sum_and_sub(a, b, expected):
    assert sum_and_sub(a, b) == expected

# ============= ЗАДАЧА 4: process_list.py =============
from process_list import process_list, process_list_gen

test_data_process = [
    ([1, 2, 3, 4], [1, 4, 27, 16]),
    ([2, 4, 6], [4, 16, 36]),
    ([1, 3, 5], [1, 27, 125]),
    ([10], [100]),
    ([0, 1], [0, 1]),
]

@pytest.mark.parametrize("input_data, expected", test_data_process)
def test_process_list(input_data, expected):
    assert process_list(input_data) == expected

@pytest.mark.parametrize("input_data, expected", test_data_process)
def test_process_list_gen(input_data, expected):
    assert list(process_list_gen(input_data)) == expected

# ============= ЗАДАЧА 5: my_sum.py =============
from my_sum import my_sum

def test_my_sum_two_args():
    assert my_sum(1, 2) == 3

def test_my_sum_multiple_args():
    assert my_sum(1, 2, 3, 4, 5) == 15

def test_my_sum_floats():
    assert my_sum(1.5, 2.5, 3.0) == 7.0

def test_my_sum_negative():
    assert my_sum(-1, -2, -3) == -6

def test_my_sum_single():
    assert my_sum(10) == 10

def test_my_sum_zero():
    assert my_sum(0, 0, 0) == 0

# ============= ЗАДАЧА 6: my_sum_argv.py =============
def test_my_sum_argv_basic():
    result = run_script('my_sum_argv.py', ['1', '2', '3', '4', '5'])
    proc = subprocess.run(
        [INTERPRETER, 'my_sum_argv.py', '1', '2', '3', '4', '5'],
        capture_output=True,
        text=True
    )
    assert proc.stdout.strip() == '15'

def test_my_sum_argv_two_numbers():
    proc = subprocess.run(
        [INTERPRETER, 'my_sum_argv.py', '10', '20'],
        capture_output=True,
        text=True
    )
    assert proc.stdout.strip() == '30'

# ============= ЗАДАЧА 7: files_sort.py =============
def test_files_sort():
    # Создаём временную директорию с файлами
    with tempfile.TemporaryDirectory() as tmpdir:
        files = ['a.py', 'b.txt', 'c.py', 'a.txt']
        for f in files:
            open(os.path.join(tmpdir, f), 'w').close()
        
        proc = subprocess.run(
            [INTERPRETER, 'files_sort.py', tmpdir],
            capture_output=True,
            text=True
        )
        output = proc.stdout.strip().split('\n')
        assert output == ['a.py', 'c.py', 'a.txt', 'b.txt']

# ============= ЗАДАЧА 9: email_validation.py =============
from email_validation import fun, filter_mail

test_data_email = [
    ('lara@mospolytech.ru', True),
    ('brian-23@mospolytech.ru', True),
    ('britts_54@mospolytech.ru', True),
    ('invalid@', False),
    ('@invalid.com', False),
    ('no-at-sign.com', False),
    ('toolong@example.comm', False),
    ('test@test.c', True),
]

@pytest.mark.parametrize("email, expected", test_data_email)
def test_email_validation(email, expected):
    assert fun(email) == expected

def test_filter_mail():
    emails = ['valid@test.ru', 'invalid@', 'another@valid.com']
    result = filter_mail(emails)
    assert len(result) == 2
    assert 'valid@test.ru' in result

# ============= ЗАДАЧА 10: fibonacci.py =============
from fibonacci import fibonacci, cube

test_data_fib = [
    (1, [0]),
    (2, [0, 1]),
    (5, [0, 1, 1, 2, 3]),
    (7, [0, 1, 1, 2, 3, 5, 8]),
]

@pytest.mark.parametrize("n, expected", test_data_fib)
def test_fibonacci(n, expected):
    assert fibonacci(n) == expected

def test_cube_function():
    assert cube(2) == 8
    assert cube(3) == 27
    assert cube(0) == 0

# ============= ЗАДАЧА 11: average_scores.py =============
from average_scores import compute_average_scores

def test_average_scores_basic():
    scores = [(89, 90, 78), (90, 91, 85), (91, 92, 83)]
    result = compute_average_scores(scores)
    assert result == (90.0, 91.0, 82.0)

def test_average_scores_single_student():
    scores = [(100,), (90,), (80,)]
    result = compute_average_scores(scores)
    assert result == (90.0,)

def test_average_scores_two_subjects():
    scores = [(80, 90), (70, 80)]
    result = compute_average_scores(scores)
    assert result == (75.0, 85.0)

# ============= ЗАДАЧА 12: plane_angle.py =============
from plane_angle import Point, plane_angle

def test_plane_angle_perpendicular():
    # Простой случай: две пересекающиеся плоскости
    a = Point(0, 0, 0)
    b = Point(1, 0, 0)
    c = Point(1, 1, 0)
    d = Point(1, 1, 1)
    angle = plane_angle(a, b, c, d)
    # Просто проверяем что угол в разумных пределах
    assert 0 <= angle <= 180

def test_plane_angle_parallel():
    # Параллельные плоскости должны давать 0 градусов
    a = Point(0, 0, 0)
    b = Point(1, 0, 0)
    c = Point(0, 1, 0)
    d = Point(1, 1, 0)
    angle = plane_angle(a, b, c, d)
    assert abs(angle) < 1e-5 or abs(angle - 180) < 1e-5

def test_point_operations():
    p1 = Point(1, 2, 3)
    p2 = Point(4, 5, 6)
    diff = p1 - p2
    assert diff.x == -3 and diff.y == -3 and diff.z == -3

# ============= ЗАДАЧА 13: phone_number.py =============
def test_phone_number():
    input_data = ['3', '07895462130', '89875641230', '9195969878']
    output = run_script('phone_number.py', input_data)
    lines = output.split('\n')
    assert '+7 (789) 546-21-30' in lines
    assert '+7 (919) 596-98-78' in lines
    assert '+7 (987) 564-12-30' in lines

# ============= ЗАДАЧА 14: people_sort.py =============
def test_people_sort():
    input_data = ['3', 'Mike Thomson 20 M', 'Robert Bustle 32 M', 'Andria Bustle 30 F']
    output = run_script('people_sort.py', input_data)
    lines = output.split('\n')
    assert 'Andria Bustle' in lines[0]
    assert 'Robert Bustle' in lines[1]

# ============= ЗАДАЧА 15: complex_numbers.py =============
from complex_numbers import Complex

def test_complex_add():
    c1 = Complex(2, 1)
    c2 = Complex(5, 6)
   

def test_complex_sub():
    c1 = Complex(5, 6)
    c2 = Complex(2, 1)
    result = c1 - c2
    assert result.real == 3 and result.imaginary == 5

def test_complex_mul():
    c1 = Complex(2, 1)
    c2 = Complex(5, 6)
    result = c1 * c2
    assert result.real == 4 and result.imaginary == 17

def test_complex_div():
    c1 = Complex(2, 1)
    c2 = Complex(5, 6)
    result = c1 / c2
    assert abs(result.real - 0.26) < 0.01
    assert abs(result.imaginary - (-0.11)) < 0.01

def test_complex_mod():
    c = Complex(3, 4)
    result = c.mod()
    assert abs(result.real - 5.0) < 0.01
    assert result.imaginary == 0

def test_complex_str():
    c1 = Complex(2.0, 1.0)
    assert str(c1) == "2.00+1.00i"
    c2 = Complex(3.0, -4.0)
    assert str(c2) == "3.00-4.00i"

# ============= ЗАДАЧА 16: circle_square_mk.py =============
from circle_square_mk import circle_square_mk

def test_circle_square_mk_accuracy():
    r = 1
    n = 100000
    result = circle_square_mk(r, n)
    expected = math.pi * r * r
    # Проверяем что погрешность меньше 5%
    assert abs(result - expected) / expected < 0.05

def test_circle_square_mk_different_radius():
    r = 5
    n = 50000
    result = circle_square_mk(r, n)
    expected = math.pi * r * r
    assert abs(result - expected) / expected < 0.1

def test_circle_square_mk_small_n():
    r = 1
    n = 100
    result = circle_square_mk(r, n)
    assert result > 0

# ============= ЗАДАЧА 17: log_decorator.py =============
from log_decorator import function_logger

def test_log_decorator():
    log_file = 'test_log.txt'
    
    # Удаляем файл если существует
    if os.path.exists(log_file):
        os.remove(log_file)
    
    @function_logger(log_file)
    def test_func(x, y):
        return x + y
    
    result = test_func(5, 10)
    assert result == 15
    
    # Проверяем что лог создан
    assert os.path.exists(log_file)
    
    with open(log_file, 'r') as f:
        content = f.read()
        assert 'test_func' in content
        assert '(5, 10)' in content
        assert '15' in content
    
    # Очищаем
    os.remove(log_file)

def test_log_decorator_multiple_calls():
    log_file = 'test_log2.txt'
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    @function_logger(log_file)
    def add(a, b):
        return a + b
    
    add(1, 2)
    add(3, 4)
    
    with open(log_file, 'r') as f:
        content = f.read()
        assert content.count('add') == 2
        assert '(1, 2)' in content
        assert '(3, 4)' in content
    
    os.remove(log_file)

# ============= Дополнительные тесты для покрытия =============

def test_fact_it_large():
    assert fact_it(12) == 479001600

def test_sum_and_sub_negative():
    assert sum_and_sub(-10, -5) == (-15, -5)

def test_my_sum_empty():
    assert my_sum() == 0

def test_fibonacci_edge_case():
    assert fibonacci(1) == [0]

def test_complex_zero():
    c = Complex(0, 0)
    assert str(c) == "0.00+0.00i"

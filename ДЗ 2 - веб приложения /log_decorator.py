from datetime import datetime
import os
import sys


def function_logger(path):
    def decorator(f):
        def wrapper(*args, **kwargs):
            start = datetime.now()
            res = f(*args, **kwargs)
            end = datetime.now()
            
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            
            with open(path, 'a', encoding='utf-8') as file:
                file.write(f"{f.__name__}\n")
                file.write(f"{start}\n")
                file.write(f"{args=}\n")
                file.write(f"{res=}\n") 
                file.write(f"{end}\n")
                file.write(f"{end-start}\n\n")
            return res
        return wrapper
    return decorator

if __name__ == '__main__':
    log_file = 'demo_log.txt'
    
    if os.path.exists(log_file):
        os.remove(log_file)
    
    @function_logger(log_file)
    def test_func(x, y):
        return x + y
    
    @function_logger(log_file)
    def multiply(a, b):
        return a * b
    
    print("1. Запуск test_func(5, 10)...")
    result1 = test_func(5, 10)
    print(f"Результат: {result1}")
    
    print("\n2. Запуск multiply(3, 4)...")
    result2 = multiply(3, 4)
    print(f"Результат: {result2}")
    
    print("\n3. Содержимое лога:")
    print("-" * 50)
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            print(f.read())
    except FileNotFoundError:
        print("Лог не найден")
    


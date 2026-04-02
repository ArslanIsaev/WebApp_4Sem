cube = lambda x: x ** 3

def fibonacci(n):
    if not isinstance(n, int) or n < 1 or n > 15:
        raise ValueError("n должно быть целым числом от 1 до 15")
    res = [0, 1]
    for _ in range(2, n):
        res.append(res[-1] + res[-2])
    return res[:n]

if __name__ == '__main__':
    n = int(input())
    print(list(map(cube, fibonacci(n))))

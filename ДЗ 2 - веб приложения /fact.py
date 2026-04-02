import time
import sys

sys.setrecursionlimit(200_000)


def fact_rec(n):
    if not isinstance(n, int) or n < 1 or n > 10**5:
        raise ValueError("n должно быть целым числом от 1 до 10^5")
    if n == 1:
        return 1
    return n * fact_rec(n - 1)


def fact_it(n):
    if not isinstance(n, int) or n < 1 or n > 10**5:
        raise ValueError("n должно быть целым числом от 1 до 10^5")
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res


# Итерационная версия работает быстрее рекурсивной
# из-за отсутствия накладных расходов на стек вызовов


if __name__ == '__main__':
    # Ограничения: 1 <= n <= 10**5
    n = 10**5

    start = time.perf_counter()
    fact_rec(n)
    end = time.perf_counter()
    print(f"fact_rec({n}): {end - start:.4f} сек")

    start = time.perf_counter()
    fact_it(n)
    end = time.perf_counter()
    print(f"fact_it({n}):  {end - start:.4f} сек")
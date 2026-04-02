import random
import math

def circle_square_mk(r, n):
    inside = 0
    for _ in range(n):
        x, y = random.uniform(-r, r), random.uniform(-r, r)
        if x*x + y*y <= r*r:
            inside += 1
    return 4 * r * r * inside / n

# При увеличении n погрешность уменьшается

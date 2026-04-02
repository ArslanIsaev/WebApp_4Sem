import math

class Complex:
    def __init__(self, r, i):
        self.real, self.imaginary = r, i

    def __add__(self, o):
        return Complex(self.real+o.real, self.imaginary+o.imaginary)

    def __sub__(self, o):
        return Complex(self.real-o.real, self.imaginary-o.imaginary)

    def __mul__(self, o):
        return Complex(
            self.real*o.real - self.imaginary*o.imaginary,
            self.real*o.imaginary + self.imaginary*o.real
        )

    def __truediv__(self, o):
        d = o.real**2 + o.imaginary**2
        return Complex(
            (self.real*o.real + self.imaginary*o.imaginary)/d,
            (self.imaginary*o.real - self.real*o.imaginary)/d
        )

    def mod(self):
        return Complex(math.sqrt(self.real**2 + self.imaginary**2), 0)

    def __str__(self):
        return f"{self.real:.2f}{'+' if self.imaginary>=0 else '-'}{abs(self.imaginary):.2f}i"

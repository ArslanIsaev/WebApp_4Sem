import math

class Point:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __sub__(self, o): #Получаем вектор
        return Point(self.x - o.x, self.y - o.y, self.z - o.z)

    def dot(self, o): #скалярное произведение
        return self.x*o.x + self.y*o.y + self.z*o.z

    def cross(self, o): #векторное произведение
        return Point(
            self.y*o.z - self.z*o.y,
            self.z*o.x - self.x*o.z,
            self.x*o.y - self.y*o.x
        )

    def absolute(self): #длина вектора
        return math.sqrt(self.dot(self))

def plane_angle(a, b, c, d):
    X = (b - a).cross(b - c) # Нормаль к плоскости ABC
    Y = (b - c).cross(c - d) # Нормаль к плоскости BCD
    cos_phi = X.dot(Y) / (X.absolute() * Y.absolute())
    return math.degrees(math.acos(cos_phi))

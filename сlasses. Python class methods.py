#обрахувати два крадратних рівняння
#a*x^2+b*x+c=0

#import numpy as np
#class QudratEquation:
    #a=0.0
    #b=0.0
   # c=0.0
#def Qadratic(a, b, c):
   # coefficients = [a, b, c]
   # roots = np.roots(coefficients)
    #return roots


import numpy as np
class QuadraticEquation:
    def __init__(self, a=0.0, b=0.0, c=0.0):
        self.a = a
        self.b = b
        self.c = c
    
    def find_roots(self):
        coefficients = [self.a, self.b, self.c]
        roots = np.roots(coefficients)
        return roots

a1 = float(input("коефіцієнт a1: "))
b1 = float(input("коефіцієнт b1: "))
c1 = float(input("коефіцієнт c1: "))

a2 = float(input("коефіцієнт a2: "))
b2 = float(input("коефіцієнт b2: "))
c2 = float(input("коефіцієнт c2: "))

equation1 = QuadraticEquation(a1, b1, c1)
equation2 = QuadraticEquation(a2, b2, c2)

roots1 = equation1.find_roots()
print(f"Корені першого рівняння: {roots1}")

roots2 = equation2.find_roots()
print(f"Корені другого рівняння: {roots2}")


import numpy as np

# Похідний клас для лінійних рівнянь
class LinearEquation(Equation):
    def __init__(self, a=1.0, b=0.0):
        self.a = a
        self.b = b

    def find_roots(self):
        # Для лінійного рівняння ax + b = 0 корінь дорівнює -b/a, якщо a != 0
        if self.a != 0:
            return [-self.b / self.a]
        else:
            return ["Рівняння не має коренів"]

# Похідний клас для квадратних рівнянь
class QuadraticEquation(Equation):
    def __init__(self, a=1.0, b=0.0, c=0.0):
        self.a = a
        self.b = b
        self.c = c

    def find_roots(self):
        # Використовуємо numpy для знаходження коренів
        coefficients = [self.a, self.b, self.c]
        roots = np.roots(coefficients)
        return roots

# Третій похідний клас для кубічних рівнянь
class CubicEquation(Equation):
    def __init__(self, a=1.0, b=0.0, c=0.0, d=0.0):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def find_roots(self):
        # Використовуємо numpy для знаходження коренів
        coefficients = [self.a, self.b, self.c, self.d]
        roots = np.roots(coefficients)
        return roots

# Приклад поліморфізму
def display_roots(equation):
    roots = equation.find_roots()
    print(f"Корені рівняння: {roots}")

# Створення об'єктів для різних типів рівнянь
linear_eq = LinearEquation(a=2, b=-4)        # 2x - 4 = 0
quadratic_eq = QuadraticEquation(a=1, b=-3, c=2)  # x^2 - 3x + 2 = 0
cubic_eq = CubicEquation(a=1, b=-6, c=11, d=-6)   # x^3 - 6x^2 + 11x - 6 = 0

# Виклик функції display_roots для різних об'єктів (поліморфізм)
display_roots(linear_eq)     # Викликає find_roots() з LinearEquation
display_roots(quadratic_eq)  # Викликає find_roots() з QuadraticEquation
display_roots(cubic_eq)      # Викликає find_roots() з CubicEquation


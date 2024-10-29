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


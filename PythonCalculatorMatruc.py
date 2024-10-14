
import numpy as np

# Функція для зчитування матриці від користувача
def input_matrix():
    rows = int(input("Введіть кількість рядків матриці: "))
    cols = int(input("Введіть кількість стовпців матриці: "))
    matrix = []
    for i in range(rows):
        row = list(map(int, input(f"Введіть елементи рядка {i + 1}, розділені пробілами: ").split()))
        if len(row) != cols:
            print("Неправильна кількість елементів у рядку!")
            return None
        matrix.append(row)
    return np.array(matrix)

# Функція для додавання двох матриць
def add_matrices(mat1, mat2):
    if mat1.shape != mat2.shape:
        print("Матриці повинні мати однаковий розмір для додавання!")
        return None
    return mat1 + mat2

# Функція для віднімання двох матриць
def subtract_matrices(mat1, mat2):
    if mat1.shape != mat2.shape:
        print("Матриці повинні мати однаковий розмір для віднімання!")
        return None
    return mat1 - mat2

# Функція для множення матриці на число
def multiply_matrix_by_scalar(matrix, scalar):
    return matrix * scalar

# Функція для множення двох матриць
def multiply_matrices(mat1, mat2):
    if mat1.shape[1] != mat2.shape[0]:
        print("Кількість стовпців першої матриці повинна дорівнювати кількості рядків другої для множення!")
        return None
    return np.dot(mat1, mat2)

# Головна функція
def matrix_calculator():
    print("Калькулятор матриць")
    print("1 - Додавання матриць")
    print("2 - Віднімання матриць")
    print("3 - Множення матриці на число")
    print("4 - Множення двох матриць")

    operation = input("Оберіть операцію (1/2/3/4): ")

    if operation == "1":
        print("Введіть першу матрицю:")
        mat1 = input_matrix()
        if mat1 is None:
            return
        print("Введіть другу матрицю:")
        mat2 = input_matrix()
        if mat2 is None:
            return
        result = add_matrices(mat1, mat2)
        if result is not None:
            print("Результат додавання:")
            print(result)

    elif operation == "2":
        print("Введіть першу матрицю:")
        mat1 = input_matrix()
        if mat1 is None:
            return
        print("Введіть другу матрицю:")
        mat2 = input_matrix()
        if mat2 is None:
            return
        result = subtract_matrices(mat1, mat2)
        if result is not None:
            print("Результат віднімання:")
            print(result)

    elif operation == "3":
        print("Введіть матрицю:")
        mat = input_matrix()
        if mat is None:
            return
        scalar = int(input("Введіть число для множення: "))
        result = multiply_matrix_by_scalar(mat, scalar)
        print("Результат множення на число:")
        print(result)

    elif operation == "4":
        print("Введіть першу матрицю:")
        mat1 = input_matrix()
        if mat1 is None:
            return
        print("Введіть другу матрицю:")
        mat2 = input_matrix()
        if mat2 is None:
            return
        result = multiply_matrices(mat1, mat2)
        if result is not None:
            print("Результат множення матриць:")
            print(result)

    else:
        print("Неправильна операція!")


if __name__ == "__main__":
    matrix_calculator()

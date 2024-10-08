class my_class(object):
    pass

# Оголошення змінних та типи даних
a = 25          # int
b = 3.14        # float
name = "Yura"   # str
is_student = True  # bool

# Виведемо значення змінних
print("Значення змінних:")
print("int:", a)
print("float:", b)
print("str:", name)
print("bool:", is_student)

# Перевірка типів змінних
print("Типи змінних:")
print("a має тип:", type(a))
print("b має тип:", type(b))
print("name має тип:", type(name))
print("is_student має тип:", type(is_student))

# Операції з числами
x = 15
y = 4

print("\nОперації з числами:")
print("Додавання:", x + y)
print("Віднімання:", x - y)
print("Множення:", x * y)
print("Ділення:", x / y)
print("Піднесення до степеня:", x ** y)

# Використання функцій round(), abs(), %
result = x / y
print("Округлення результату ділення:", round(result, 2))
print("Абсолютне значення -10:", abs(-10))
print("Остача від ділення:", x % y)

# Обчислення середнього арифметичного трьох чисел
num1 = 10
num2 = 20
num3 = 30
average = (num1 + num2 + num3) / 3
print("Середнє арифметичне трьох чисел:", average)

# Робота з рядками
name = "Yura"
age = 26

# Методи роботи з рядками
print("\nРобота з рядками:")
print("Конкатенація:", "Привіт, " + name + "!")
print("Зміна регістру:", name.upper(), name.lower())

# Форматування рядка (f-strings та format())
print(f"Мене звати {name}, мені {age} років.")  # f-strings
print("Мене звати {}, мені {} років.".format(name, age))  # format()

# Умовні конструкції (if-elif-else)
num = int(input("\nВведіть число: "))
if num % 2 == 0:
    print("Число парне")
else:
    print("Число непарне")

# Перевірка, чи входить число в діапазон
num = int(input("Введіть число для перевірки діапазону (від 10 до 50): "))
if 10 <= num <= 50:
    print("Число в діапазоні")
else:
    print("Число не в діапазоні")

# Цикли (for, while)
print("\nЦикл for, що виводить числа від 1 до 10:")
for i in range(1, 11):
    print(i)

print("\nЦикл while для обчислення суми чисел від 1 до 100:")
sum = 0
i = 1
while i <= 100:
    sum += i
    i += 1
print("Сума чисел від 1 до 100:", sum)

# Функції
def add_numbers(a, b):
    return a + b

def reverse_string(s):
    return s[::-1]

# Виклик функцій
print("\nФункції:")
print("Сума 5 і 10:", add_numbers(5, 10))
print("Зворотний рядок:", reverse_string("Hello"))

# Списки та цикли
numbers = [1, 2, 3, 4, 5]

print("\nСписок та цикл:")
print("Елементи списку:")
for number in numbers:
    print(number)

numbers.append(6)
print("Список після додавання:", numbers)

numbers.pop()
print("Список після видалення останнього елемента:", numbers)

# Робота зі словниками
student = {
    "name": "Yura",
    "age": 26,
    "faculty": "Computer Science"
}

# Вивести значення за ключем
print("\nСловник студента:")
print("Ім'я студента:", student["name"])

# Додати новий ключ "рік навчання"
student["year"] = 1
print("Словник після додавання 'рік навчання':", student)

# Обробка виключень (try-except)
try:
    num1 = int(input("\nВведіть перше число: "))
    num2 = int(input("Введіть друге число: "))
    result = num1 / num2
    print(f"Результат ділення: {result}")
except ZeroDivisionError:
    print("Помилка: ділення на нуль!")
except ValueError:
    print("Помилка: введено нечислове значення!")



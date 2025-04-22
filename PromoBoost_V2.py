import os
import json
import random
import string

#Основна папка
BASE_DIR = r"C:\Web\PromoAcceleration"
INFO_LIST_DIR = os.path.join(BASE_DIR, "InfoList")  # Де зберігатимуться списки промокодів

#Створюємо необхідні папки
os.makedirs(INFO_LIST_DIR, exist_ok=True)

#Введення назви категорії (наприклад, "OffroadHatchback")
category_name = input("Jeep GladiatorF9 BOSS").strip()

#Папка для збереження JSON-файлів цієї категорії
CATEGORY_DIR = os.path.join(BASE_DIR, category_name)
os.makedirs(CATEGORY_DIR, exist_ok=True)

#Файл у InfoList, де зберігатимуться всі промокоди цієї категорії
info_list_file = os.path.join(INFO_LIST_DIR, f"{category_name}.json")

#Завантажуємо існуючі промокоди, якщо файл вже є
if os.path.exists(info_list_file):
    with open(info_list_file, "r", encoding="utf-8") as f:
        promo_codes = json.load(f)
else:
    promo_codes = []

#Перевіряємо унікальність кодів
existing_codes = {entry["code"] for entry in promo_codes}

#Функція генерації унікального промокоду (10 символів)
def generate_promo_code(length=10):
    while True:
        new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if new_code not in existing_codes:
            existing_codes.add(new_code)
            return new_code

#JSON-структура (шаблон опису товару)
promo_text = """{
    "maxUsages": 1,
    "currentUsages": 0,
    "blacklistedSteamIDS": [],
    "rewards": [
        {
            "isVehicle": 0,
            "Classname": "Apple",
            "QuantityPercent": -1,
            "HealthPercent": -1,
            "Attachments": []
        },
        {
            "isVehicle": 1,
            "Classname": "OffroadHatchback",
            "QuantityPercent": -1,
            "HealthPercent": -1,
            "Attachments": [
                "CHatchbackHood",
                "HatchbackTrunk",
                "HatchbackDoors_CoDriver",
                "HatchbackDoors_Driver",
                "CHatchbackWheel",
                "HatchbackWheel",
                "CarRadiator",
                "SparkPlug",
                "HeadlightH7",
                "HeadlightH7",
                "HatchbackWheel",
                "HatchbackWheel",
                "HatchbackWheel",
                "HatchbackWheel",
                "CarBattery"
            ]
        }
    ]
}"""

#Генеруємо 50 JSON-файлів з унікальними промокодами
for _ in range(20):
    promo_code = generate_promo_code()  # Генеруємо код
    file_name = f"{promo_code}.json"  # Назва JSON-файлу
    file_path = os.path.join(CATEGORY_DIR, file_name)

    #Дані для JSON-файлу
    data = {
        "promo_code": promo_code,
        "data": json.loads(promo_text)  # Перетворюємо текстовий JSON у словник
    }

    #Записуємо у JSON-файл
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    #Додаємо промокод у список (з `used: false`)
    promo_codes.append({"code": promo_code, "used": False})

#Записуємо оновлений список промокодів у InfoList JSON
with open(info_list_file, "w", encoding="utf-8") as f:
    json.dump(promo_codes, f, ensure_ascii=False, indent=4)

print(f"✅ 50 JSON-файлів згенеровано у {CATEGORY_DIR}")
print(f"📌 Усі промокоди збережені у {info_list_file}")

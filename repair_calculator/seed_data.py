# seed_data.py
from database import DB_PATH  # только для пути
import sqlite3
from database import init_db, DB_PATH 

def seed_database():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Убедимся, что таблицы существуют (они должны быть созданы при импорте)
    # Но если нет — создадим их (опционально)
    # init_db()  # ❌ НЕ ВЫЗЫВАЙ! Он уже вызван при импорте!

    tables = ["job_items", "rooms", "materials", "work_types", "executors", "customers"]
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"🧹 Очищена таблица: {table}")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Таблица {table} не существует: {e}")

    # Вставка данных
    customers = [
        ("Иван Петров", "+79001234567", "ivan@example.com"),
        ("Мария Сидорова", "+79002223344", "maria@example.com")
    ]
    cursor.executemany(
        "INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)",
        customers
    )

    executors = [
        ("Строительный Альянс", "+79001112233", "ООО \"СтройМонтаж\"", 4.8),
        ("Качественный ремонт", "+79003334455", "ИП Кузнецов", 4.6)
    ]
    cursor.executemany(
        "INSERT INTO executors (name, phone, company_name, rating) VALUES (?, ?, ?, ?)",
        executors
    )

    rooms = [
        ("Кухня", 12.5, 3, 1, 1),
        ("Спальня", 18.0, 2, 1, 1),
        ("Ванная", 5.2, 3, 1, 2)
    ]
    cursor.executemany(
        "INSERT INTO rooms (room_type, area_m2, floor, building_id, customer_id) VALUES (?, ?, ?, ?, ?)",
        rooms
    )

    materials = [
        ("Керамическая плитка", "м²", 850, "Плитка"),
        ("Гипсокартон", "лист", 320, "Конструкция"),
        ("Краска акриловая", "л", 450, "Окраска"),
        ("Электрокабель ВВГ", "м", 25, "Электромонтаж")
    ]
    cursor.executemany(
        "INSERT INTO materials (name, unit, price_per_unit, category) VALUES (?, ?, ?, ?)",
        materials
    )

    work_types = [
        ("Укладка плитки", "м²", 300, "Отделочные"),
        ("Штукатурка стен", "м²", 180, "Подготовительные"),
        ("Прокладка электрики", "м", 40, "Электромонтаж"),
        ("Установка розеток", "шт", 120, "Электромонтаж")
    ]
    cursor.executemany(
        "INSERT INTO work_types (name, unit, price_per_unit, category) VALUES (?, ?, ?, ?)",
        work_types
    )

    job_items = [
        (13, 1, 1, 10.2, 3060),   # Кухня (ID=13): плитка
        (13, 2, None, 15.0, 2700), # Штукатурка
        (13, 3, 4, 25.0, 1000),   # Электрика
    ]

    cursor.executemany(
        "INSERT INTO job_items (room_id, work_type_id, material_id, quantity, total_price) VALUES (?, ?, ?, ?, ?)",
        job_items
    )
    # После materials и work_types

    cursor.execute("DELETE FROM work_materials")
    print("🧹 Очищена таблица: work_materials")

    # Получаем реальные ID из только что вставленных записей
    cursor.execute("SELECT id FROM work_types WHERE name = 'Укладка плитки'")
    work_id_1 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM work_types WHERE name = 'Штукатурка стен'")
    work_id_2 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM work_types WHERE name = 'Прокладка электрики'")
    work_id_3 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM work_types WHERE name = 'Установка розеток'")
    work_id_4 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM materials WHERE name = 'Керамическая плитка'")
    mat_id_1 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM materials WHERE name = 'Гипсокартон'")
    mat_id_2 = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM materials WHERE name = 'Электрокабель ВВГ'")
    mat_id_4 = cursor.fetchone()[0]

    # Связи с правильными ID
    work_materials = [
        (work_id_1, mat_id_1),
        (work_id_2, mat_id_2),
        (work_id_3, mat_id_4),
        (work_id_4, mat_id_4),
    ]

    cursor.executemany(
        "INSERT INTO work_materials (work_type_id, material_id) VALUES (?, ?)",
        work_materials
    )

    conn.commit()
    conn.close()
    print("✅ Данные успешно загружены!")


if __name__ == "__main__":
    seed_database()
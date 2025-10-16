# database.py
import sqlite3
import os

#DB_PATH = "data/repair_db.sqlite"

# Определяем папку, где лежит этот файл (database.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(BASE_DIR, "shared")
DB_PATH = os.path.join(SHARED_DIR, "repair_db.sqlite")

def init_db():
    """Инициализирует базу данных и создаёт таблицы"""
    os.makedirs(SHARED_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица: Заказчики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT
        )
    ''')

    # Таблица: Исполнители
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS executors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            company_name TEXT,
            rating REAL
        )
    ''')

    # Таблица: Помещения
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_type TEXT NOT NULL,
            area_m2 REAL NOT NULL,
            floor INTEGER,
            building_id INTEGER,
            customer_id INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    ''')

    # Таблица: Материалы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            category TEXT
        )
    ''')

    # Таблица: Виды работ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            price_per_unit REAL NOT NULL,
            category TEXT
        )
    ''')

    # Таблица: Смета (позиции)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER,
            work_type_id INTEGER,
            material_id INTEGER,
            quantity REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(id),
            FOREIGN KEY (work_type_id) REFERENCES work_types(id),
            FOREIGN KEY (material_id) REFERENCES materials(id)
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS work_materials (
        work_type_id INTEGER,
        material_id INTEGER,
        PRIMARY KEY (work_type_id, material_id),
        FOREIGN KEY (work_type_id) REFERENCES work_types(id),
        FOREIGN KEY (material_id) REFERENCES materials(id)
    )
''')
        # Таблица: Сметы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            room_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    ''')

    # Таблица: Позиции сметы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estimate_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estimate_id INTEGER NOT NULL,
            work_type_id INTEGER,
            material_id INTEGER,
            quantity REAL NOT NULL,
            price_per_unit REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (estimate_id) REFERENCES estimates(id),
            FOREIGN KEY (work_type_id) REFERENCES work_types(id),
            FOREIGN KEY (material_id) REFERENCES materials(id)
        )
    ''')

    try:
        cursor.execute('''
        ALTER TABLE estimates ADD COLUMN executor_id INTEGER REFERENCES executors(id)
        ''')
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise
        # Иначе — столбец уже существует, ничего не делаем
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована.")

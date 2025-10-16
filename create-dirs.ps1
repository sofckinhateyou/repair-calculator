# Название проекта
$projectName = "repair_calculator"

# Путь к корневой директории (текущая папка)
$basePath = Get-Location

# Полный путь к проекту
$projectPath = Join-Path $basePath $projectName

# Создание основной директории
New-Item -ItemType Directory -Path $projectPath -Force

# Создание поддиректории data
$dataPath = Join-Path $projectPath "data"
New-Item -ItemType Directory -Path $dataPath -Force

# Содержимое файлов

# main.py
$mainContent = @"
import tkinter as tk
from tkinter import messagebox
from database import Database
from models import Repair

class RepairCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор ремонта")
        self.root.geometry("500x400")

        # Инициализация базы данных
        self.db = Database()

        # UI элементы
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="Калькулятор ремонта", font=("Arial", 16))
        title_label.pack(pady=10)

        # Поле ввода: название ремонта
        tk.Label(self.root, text="Название ремонта:").pack()
        self.repair_name_entry = tk.Entry(self.root, width=40)
        self.repair_name_entry.pack(pady=5)

        # Поле ввода: стоимость
        tk.Label(self.root, text="Стоимость (руб.):").pack()
        self.cost_entry = tk.Entry(self.root, width=40)
        self.cost_entry.pack(pady=5)

        # Кнопка добавления
        add_button = tk.Button(self.root, text="Добавить ремонт", command=self.add_repair)
        add_button.pack(pady=10)

        # Список ремонта
        self.listbox = tk.Listbox(self.root, width=60, height=10)
        self.listbox.pack(pady=10)
        self.update_listbox()

    def add_repair(self):
        name = self.repair_name_entry.get().strip()
        cost_str = self.cost_entry.get().strip()

        if not name or not cost_str:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            cost = float(cost_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Стоимость должна быть числом.")
            return

        repair = Repair(name=name, cost=cost)
        self.db.add_repair(repair)
        self.update_listbox()
        self.clear_entries()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        repairs = self.db.get_all_repairs()
        for r in repairs:
            self.listbox.insert(tk.END, f"{r.name} - {r.cost:.2f} руб.")

    def clear_entries(self):
        self.repair_name_entry.delete(0, tk.END)
        self.cost_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = RepairCalculatorApp(root)
    root.mainloop()
"@

# database.py
$databaseContent = @"
import sqlite3
from pathlib import Path
from models import Repair

class Database:
    def __init__(self, db_path='data/repair_db.sqlite'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS repairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    cost REAL NOT NULL
                )
            ''')
            conn.commit()

    def add_repair(self, repair: Repair):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO repairs (name, cost) VALUES (?, ?)",
                (repair.name, repair.cost)
            )
            conn.commit()

    def get_all_repairs(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, cost FROM repairs")
            rows = cursor.fetchall()
            return [Repair(id=row[0], name=row[1], cost=row[2]) for row in rows]
"@

# models.py
$modelsContent = @"
from typing import Optional

class Repair:
    def __init__(self, name: str, cost: float, id: Optional[int] = None):
        self.id = id
        self.name = name
        self.cost = cost

    def __repr__(self):
        return f"Repair(id={self.id}, name='{self.name}', cost={self.cost})"
"@

# Запись файлов

# main.py
$mainFilePath = Join-Path $projectPath "main.py"
Set-Content -Path $mainFilePath -Value $mainContent

# database.py
$databaseFilePath = Join-Path $projectPath "database.py"
Set-Content -Path $databaseFilePath -Value $databaseContent

# models.py
$modelsFilePath = Join-Path $projectPath "models.py"
Set-Content -Path $modelsFilePath -Value $modelsContent

# repair_db.sqlite — будет создан автоматически при первом обращении к БД
# Но можно создать пустой файл, чтобы он был виден
$sqliteFilePath = Join-Path $dataPath "repair_db.sqlite"
if (-not (Test-Path $sqliteFilePath)) {
    New-Item -ItemType File -Path $sqliteFilePath -Force | Out-Null
}

Write-Host "✅ Проект '$projectName' успешно создан!" -ForegroundColor Green
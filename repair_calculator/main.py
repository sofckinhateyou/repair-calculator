# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB_PATH
from add_item_dialog import AddItemDialog
from tkinter import simpledialog

class RepairCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт стоимости ремонта")
        self.root.geometry("1200x700")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.work_types = []
        self.materials = []
        self.room_data = []
        self.executors = []

        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, fill="x")

        ttk.Label(top_frame, text="Помещение:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.room_combo = ttk.Combobox(top_frame, state="readonly", width=30)
        self.room_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.load_rooms()

        # Кнопка "Добавить позицию"
        add_btn = ttk.Button(top_frame, text="Добавить позицию", command=self.add_item)
        add_btn.grid(row=0, column=2, padx=10, pady=5)

        # Кнопка "Удалить позицию"
        delete_btn = ttk.Button(top_frame, text="Удалить позицию", command=self.delete_item)
        delete_btn.grid(row=0, column=4, padx=10, pady=5)

        # Сохр все
        save_btn = ttk.Button(top_frame, text="Сохранить расчет", command=self.save_estimate)
        save_btn.grid(row=0, column=3, padx=10, pady=5)

        #Удалить все
        clear_btn = ttk.Button(top_frame, text="Очистить всё", command=self.clear_all)
        clear_btn.grid(row=0, column=5, padx=10, pady=5)

        # Кнопка "Просмотреть сохранённые расчёты"
        view_btn = ttk.Button(top_frame, text="Просмотреть сметы", command=self.view_saved_estimates)
        view_btn.grid(row=0, column=5, padx=10, pady=5)

        #Исполнители
        ttk.Label(top_frame, text="Исполнитель:", font=("Arial", 10)).grid(row=0, column=6, padx=10, pady=5, sticky="w")
        self.executor_combo = ttk.Combobox(top_frame, state="readonly", width=25)
        self.executor_combo.grid(row=0, column=7, padx=10, pady=5, sticky="ew")
        # Загрузим исполнителей
        self.load_executors()

        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("Работа", "Материал", "Количество", "Цена за ед.", "Итого"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, fill="both", expand=True)

        # Итог
        self.total_label = ttk.Label(self.root, text="Итого: 0 руб", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=10)

        # Подписываемся на события
        self.room_combo.bind("<<ComboboxSelected>>", lambda e: self.update_estimate())

        # 🟢 ПРАВИЛЬНЫЙ ПОРЯДОК ЗАГРУЗКИ ДАННЫХ
        self.load_work_types()
        self.load_materials()
        self.load_work_materials()

        # 🟢 Только ПОСЛЕ загрузки данных — создаём диалог
        self.add_item_dialog = AddItemDialog(self.root, self.work_types, self.materials, self.work_materials)

    def load_rooms(self):
        self.cursor.execute("SELECT id, room_type, area_m2 FROM rooms")
        self.room_data = self.cursor.fetchall()

        print("🔍 Помещения:")
        for r in self.room_data:
            print(f"ID: {r[0]}, Тип: {r[1]}, Площадь: {r[2]} м²")

        values = [f"{r[1]} ({r[2]} м²)" for r in self.room_data]
        self.room_combo['values'] = values
        if self.room_data:
            self.room_combo.current(0)

            # 🟢 Запускаем update_estimate() ПОСЛЕ создания UI
            self.root.after(100, self.update_estimate)

    def load_work_types(self):
        self.cursor.execute("SELECT id, name, unit, price_per_unit FROM work_types")
        self.work_types = self.cursor.fetchall()

        print("🔍 Работы:")
        for w in self.work_types:
            print(f"ID: {w[0]}, {w[1]} ({w[2]}, {w[3]} руб)")

    def load_materials(self):
        self.cursor.execute("SELECT id, name, unit, price_per_unit FROM materials")
        self.materials = self.cursor.fetchall()

        print("🔍 Материалы:")
        for m in self.materials:
            print(f"ID: {m[0]}, {m[1]} ({m[2]}, {m[3]} руб)")

    def load_work_materials(self):
        self.cursor.execute("SELECT work_type_id, material_id FROM work_materials")
        raw_data = self.cursor.fetchall()

        print("🔍 Связи работа-материал:")
        self.work_materials = []  # 🟢 ИНИЦИАЛИЗАЦИЯ СПИСКА ПЕРЕД ЦИКЛОМ

        for work_id, mat_id in raw_data:
            # Найти имя работы
            work_name = "Неизвестная работа"
            for w in self.work_types:
                if w[0] == work_id:
                    work_name = w[1]
                    break

            # Найти имя материала
            mat_name = "Неизвестный материал"
            for m in self.materials:
                if m[0] == mat_id:
                    mat_name = m[1]
                    break

            # Выводим информацию
            print(f"Работа: {work_name} → Материал: {mat_name}")

            # Сохраняем только если оба элемента существуют
            if work_name != "Неизвестная работа" and mat_name != "Неизвестный материал":
                self.work_materials.append((work_id, mat_id))
            else:
                print(f"⚠️ Пропущена связь: work_id={work_id}, mat_id={mat_id} (не найдено)")

        print(f"✅ Загружено корректных связей: {len(self.work_materials)}")

    def add_item(self):
        dialog = AddItemDialog(self.root, self.work_types, self.materials, self.work_materials)
        result = dialog.show()

        if result:
            self.tree.insert("", "end", values=(
                result["work_name"],
                result["material_name"] or "—",
                result["quantity"],
                result["price_per_unit"],
                result["total_price"]
            ))
            self.update_total()

    def delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Ошибка", "Выберите позицию для удаления.")
            return

        # Подтверждение
        if messagebox.askyesno("Подтвердите", "Вы уверены, что хотите удалить выбранную позицию?"):
            for item in selected_items:
                self.tree.delete(item)
            self.update_total()

    def clear_all(self):
        if messagebox.askyesno("Очистить всё", "Вы уверены, что хотите очистить весь список?"):
            for row in self.tree.get_children():
                self.tree.delete(row)
            self.update_total()

    def update_estimate(self):
        selected_index = self.room_combo.current()
        if selected_index == -1:
            return

        room_id = self.room_data[selected_index][0]

        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Загрузка позиций из БД
        self.cursor.execute('''
            SELECT w.name, m.name, j.quantity, w.price_per_unit, j.total_price
            FROM job_items j
            JOIN work_types w ON j.work_type_id = w.id
            LEFT JOIN materials m ON j.material_id = m.id
            WHERE j.room_id = ?
        ''', (room_id,))
        
        rows = self.cursor.fetchall()

        total = 0
        for row in rows:
            work_name, mat_name, qty, price, total_price = row
            mat_name = mat_name or "—"
            self.tree.insert("", "end", values=(work_name, mat_name, qty, price, total_price))
            total += total_price

        self.total_label.config(text=f"Итого: {total:.2f} руб")

    def update_total(self):
        total = 0
        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            total += float(values[4])

        # Получаем выбранный исполнитель
        selected_executor = self.executor_combo.get()
        executor_id = None
        multiplier = 1.0

        if selected_executor:
            for e in self.executors:
                if e[1] == selected_executor:
                    executor_id = e[0]
                    rating = e[2]  # 🟢 Это рейтинг! Индекс 2, а не 3
                    multiplier = self.get_multiplier(rating)
                    break

        final_total = total * multiplier

        self.total_label.config(text=f"Итого: {final_total:.2f} руб (множитель: {multiplier:.2f})")
        
    def save_estimate(self):
        selected_index = self.room_combo.current()
        if selected_index == -1:
            messagebox.showwarning("Ошибка", "Выберите помещение.")
            return

        room_id = self.room_data[selected_index][0]
        room_name = self.room_combo.get().split(" ")[0]

        name = simpledialog.askstring("Сохранить смету", f"Введите название для сметы:", initialvalue=f"Ремонт {room_name} {self.root.winfo_toplevel().winfo_toplevel().title()}")
        if not name:
            return

        # Получаем итог
        total = 0
        items = []

        for row in self.tree.get_children():
            values = self.tree.item(row, "values")
            work_name = values[0]
            material_name = values[1]
            qty = float(values[2])
            price_per_unit = float(values[3])
            total_price = float(values[4])

            work_id = None
            for w in self.work_types:
                if w[1] == work_name:
                    work_id = w[0]
                    break

            mat_id = None
            if material_name != "—":
                for m in self.materials:
                    if m[1] == material_name:
                        mat_id = m[0]
                        break

            items.append((work_id, mat_id, qty, price_per_unit, total_price))
            total += total_price

        # Множитель от исполнителя
        selected_executor = self.executor_combo.get()
        executor_id = None
        multiplier = 1.0

        if selected_executor:
            for e in self.executors:
                if e[1] == selected_executor:
                    executor_id = e[0]
                    multiplier = self.get_multiplier(e[3])
                    break

        final_total = total * multiplier

        # Сохраняем в БД
        try:
            self.cursor.execute(
                "INSERT INTO estimates (name, room_id, total_price, executor_id) VALUES (?, ?, ?, ?)",
                (name, room_id, final_total, executor_id)
            )
            estimate_id = self.cursor.lastrowid

            for item in items:
                work_id, mat_id, qty, price_per_unit, total_price = item
                self.cursor.execute(
                    "INSERT INTO estimate_items (estimate_id, work_type_id, material_id, quantity, price_per_unit, total_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (estimate_id, work_id, mat_id, qty, price_per_unit, total_price)
                )

            self.conn.commit()
            messagebox.showinfo("Успех", f"Смета '{name}' успешно сохранена!\nИтого: {final_total:.2f} руб (множитель: {multiplier:.2f})")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить смету: {e}")
    def view_saved_estimates(self):
        # Создаём окно
        view_window = tk.Toplevel(self.root)
        view_window.title("История смет")
        view_window.geometry("800x500")
        view_window.resizable(False, False)

        # Центрируем окно
        view_window.transient(self.root)
        view_window.grab_set()

        # Фрейм
        frame = ttk.Frame(view_window, padding="20")
        frame.pack(fill="both", expand=True)

        # Заголовок
        ttk.Label(frame, text="Сохранённые сметы", font=("Arial", 14, "bold")).pack(pady=10)

        # Таблица
        columns = ("ID", "Название", "Помещение", "Итого", "Дата")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100 if col != "Название" else 200)
        tree.pack(pady=10, fill="both", expand=True)

        # Прокрутка
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Загрузка данных из БД
        try:
            self.cursor.execute('''
                SELECT e.id, e.name, r.room_type, e.total_price, e.created_at
                FROM estimates e
                JOIN rooms r ON e.room_id = r.id
                ORDER BY e.created_at DESC
            ''')
            rows = self.cursor.fetchall()

            for row in rows:
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сметы: {e}")
            return

        # Кнопки
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)

        def on_select():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Выберите", "Выберите смету для просмотра.")
                return
            item = tree.item(selected[0])
            estimate_id = item["values"][0]

            # Открываем детали
            self.show_estimate_details(estimate_id)

        def on_delete():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Выберите", "Выберите смету для удаления.")
                return
            item = tree.item(selected[0])
            estimate_id = item["values"][0]
            name = item["values"][1]

            if messagebox.askyesno("Удалить", f"Вы уверены, что хотите удалить смету '{name}'?"):
                try:
                    self.cursor.execute("DELETE FROM estimate_items WHERE estimate_id = ?", (estimate_id,))
                    self.cursor.execute("DELETE FROM estimates WHERE id = ?", (estimate_id,))
                    self.conn.commit()
                    tree.delete(selected[0])
                    messagebox.showinfo("Успех", "Смета удалена.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить: {e}")

        # Кнопки
        ttk.Button(button_frame, text="Просмотреть", command=on_select).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Удалить", command=on_delete).pack(side="right", padx=5)

        # Связь Enter/Escape
        view_window.bind("<Return>", lambda e: on_select())
        view_window.bind("<Escape>", lambda e: view_window.destroy())

    def show_estimate_details(self, estimate_id):
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Детали сметы #{estimate_id}")
        detail_window.geometry("700x500")
        detail_window.resizable(False, False)

        detail_window.transient(self.root)
        detail_window.grab_set()

        frame = ttk.Frame(detail_window, padding="20")
        frame.pack(fill="both", expand=True)

        # Заголовок
        ttk.Label(frame, text=f"Смета #{estimate_id}", font=("Arial", 14, "bold")).pack(pady=10)

        # Таблица позиций
        columns = ("Работа", "Материал", "Кол-во", "Цена за ед.", "Итого")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(pady=10, fill="both", expand=True)

        # Прокрутка
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Загрузка позиций
        try:
            self.cursor.execute('''
                SELECT wt.name, m.name, ei.quantity, ei.price_per_unit, ei.total_price
                FROM estimate_items ei
                LEFT JOIN work_types wt ON ei.work_type_id = wt.id
                LEFT JOIN materials m ON ei.material_id = m.id
                WHERE ei.estimate_id = ?
            ''', (estimate_id,))
            rows = self.cursor.fetchall()

            for row in rows:
                work_name = row[0] or "—"
                mat_name = row[1] or "—"
                qty = row[2]
                price = row[3]
                total = row[4]
                tree.insert("", "end", values=(work_name, mat_name, qty, price, total))

            # Итог
            total_sum = sum(row[4] for row in rows)
            ttk.Label(frame, text=f"Итого: {total_sum:.2f} руб", font=("Arial", 12, "bold")).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            return

        # Кнопка закрытия
        ttk.Button(frame, text="Закрыть", command=detail_window.destroy).pack(pady=10)

        # Bind клавиш
        detail_window.bind("<Escape>", lambda e: detail_window.destroy())

    def load_executors(self):
        try:
            # Загружаем ID, имя и рейтинг
            self.cursor.execute("""
                SELECT id, name, rating 
                FROM executors
                ORDER BY rating DESC
            """)
            executors = self.cursor.fetchall()

            print("🔍 Исполнители:")
            for e in executors:
                print(f"ID: {e[0]}, {e[1]} (рейтинг: {e[2]})")

            values = [e[1] for e in executors]
            self.executor_combo['values'] = values
            if values:
                self.executor_combo.current(0)

            # Сохраняем все данные: (id, name, rating)
            self.executors = executors

            # Привязываем событие
            self.executor_combo.bind("<<ComboboxSelected>>", lambda e: self.update_total())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить исполнителей: {e}")

    def get_multiplier(self, rating):
        """Возвращает множитель стоимости по рейтингу"""
        # Пример: 4.8 → 1.1, 4.6 → 1.05, 4.0 → 1.0
        if rating >= 4.8:
            return 1.1
        elif rating >= 4.6:
            return 1.05
        elif rating >= 4.4:
            return 1.02
        else:
            return 1.0
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = RepairCalculatorApp(tk.Tk())
    app.run()
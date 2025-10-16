import tkinter as tk
from tkinter import ttk
# add_item_dialog.py
class AddItemDialog:
    def __init__(self, parent, work_types, materials, work_materials):
        self.parent = parent
        self.work_types = work_types
        self.materials = materials
        self.work_materials = work_materials  # Связи работы и материалов
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить позицию")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)

        self.work_var = tk.StringVar()
        self.material_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1.0")

        ttk.Label(self.dialog, text="Работа:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.work_combo = ttk.Combobox(self.dialog, textvariable=self.work_var, values=[w[1] for w in work_types], state="readonly")
        self.work_combo.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(self.dialog, text="Материал:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.material_combo = ttk.Combobox(self.dialog, textvariable=self.material_var, state="readonly")
        self.material_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ttk.Label(self.dialog, text="Количество:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Entry(self.dialog, textvariable=self.quantity_var).grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        btn_frame = ttk.Frame(self.dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Добавить", command=self.add_item).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=10)

        # Привязка
        self.work_combo.bind("<<ComboboxSelected>>", self.on_work_selected)

        if work_types:
            self.work_combo.current(0)
            self.on_work_selected(None)

    def on_work_selected(self, event):
        selected_name = self.work_var.get()
        work_id = next(w[0] for w in self.work_types if w[1] == selected_name)

        # Находим подходящие материалы
        available_materials = []
        for wm in self.work_materials:
            if wm[0] == work_id:
                mat_id = wm[1]
                mat_name = next(m[1] for m in self.materials if m[0] == mat_id)
                available_materials.append(mat_name)

        # Обновляем список материалов
        self.material_combo['values'] = ["—"] + available_materials
        self.material_combo.set("—")

    def add_item(self):
        try:
            work_name = self.work_var.get()
            material_name = self.material_var.get()
            quantity = float(self.quantity_var.get())

            if not work_name or work_name == "—":
                messagebox.showwarning("Ошибка", "Выберите работу!")
                return

            work_id = next(w[0] for w in self.work_types if w[1] == work_name)
            material_id = None
            if material_name != "—":
                material_id = next(m[0] for m in self.materials if m[1] == material_name)

            price_per_unit = next(w[3] for w in self.work_types if w[1] == work_name)
            total_price = quantity * price_per_unit

            self.result = {
                "work_id": work_id,
                "work_name": work_name,
                "material_id": material_id,
                "material_name": material_name,
                "quantity": quantity,
                "price_per_unit": price_per_unit,
                "total_price": total_price
            }

            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")

    def show(self):
        self.dialog.grab_set()
        self.dialog.wait_window()
        return self.result
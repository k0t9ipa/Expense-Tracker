import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

# --- Конфигурация ---
DATA_FILE = "expenses.json" # Имя файла для сохранения данных

# --- Основная логика приложения ---
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")

        # Список для хранения расходов в памяти
        self.expenses = []

        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем данные из файла при запуске, если он существует
        self.load_data_from_file()

    def create_widgets(self):
        # --- Блок ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить новый расход", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_sum = ttk.Entry(input_frame)
        self.entry_sum.grid(row=0, column=1, sticky="ew", pady=2)

        # Категория
        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_category = ttk.Entry(input_frame)
        self.entry_category.grid(row=1, column=1, sticky="ew", pady=2)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_date = ttk.Entry(input_frame)
        self.entry_date.grid(row=2, column=1, sticky="ew", pady=2)

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=10
        )

        # --- Таблица расходов ---
        self.tree = ttk.Treeview(self.root, columns=("sum", "category", "date"), show="headings")
        
        self.tree.heading("sum", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("sum", anchor="center", width=100)
        self.tree.column("category", anchor="w")
        self.tree.column("date", anchor="center", width=120)
        
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # --- Блок фильтрации и подсчета ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация и отчет", padding="10")
        filter_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # Период (С - По)
        ttk.Label(filter_frame, text="Период:").grid(row=0, column=0, sticky="w")
        
        ttk.Label(filter_frame, text="С:").grid(row=1, column=0, sticky="e")
        self.entry_date_from = ttk.Entry(filter_frame, width=12)
        self.entry_date_from.grid(row=1, column=1, sticky="w")
        
        ttk.Label(filter_frame, text="По:").grid(row=1, column=2, sticky="e", padx=(10, 0))
        self.entry_date_to = ttk.Entry(filter_frame, width=12)
        self.entry_date_to.grid(row=1, column=3, sticky="w")

         # Категория фильтра
        ttk.Label(filter_frame, text="Категория:").grid(row=2, column=0, sticky="e", pady=(5, 0))
        self.filter_category = ttk.Entry(filter_frame)
        self.filter_category.grid(row=2, column=1, columnspan=3, sticky="ew", pady=(5, 0))

         # Кнопки действий
         ttk.Button(filter_frame, text="Посчитать сумму", command=self.calculate_sum).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(10, 2), padx=(0, 5)
         )
        
         # Файловые операции (JSON)
         file_ops_frame = ttk.LabelFrame(self.root, text="Файловые операции", padding="5")
         file_ops_frame.grid(row=2, column=1, sticky="nsew", padx=(0, 10), pady=(5, 10))
         
         ttk.Button(file_ops_frame, text="Сохранить в JSON", command=self.save_data).pack(fill='x', padx=5, pady=2)
         ttk.Button(file_ops_frame, text="Загрузить из JSON", command=self.load_data_from_file).pack(fill='x', padx=5, pady=2)
         ttk.Button(file_ops_frame, text="Очистить все данные", command=self.clear_all_data).pack(fill='x', padx=5, pady=(2, 5))


    # --- Логика работы с данными ---
    def add_expense(self):
        """Добавляет новый расход после валидации."""
        try:
            sum_value = float(self.entry_sum.get())
            if sum_value <= 0:
                raise ValueError("Сумма должна быть положительным числом.")
            
            category = self.entry_category.get().strip()
            if not category:
                raise ValueError("Категория не может быть пустой.")
                
            date_str = self.entry_date.get().strip()
            date = datetime.strptime(date_str, "%Y-%m-%d") 

            expense = {
                "sum": sum_value,
                "category": category,
                "date": date_str
            }
            self.expenses.append(expense)
            self.update_treeview()
            
            self.entry_sum.delete(0, tk.END)
            self.entry_category.delete(0, tk.END)
            self.entry_date.delete(0, tk.END)
            self.entry_sum.focus()

            messagebox.showinfo("Успех", "Расход добавлен.")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def update_treeview(self):
        """Обновляет данные в таблице."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for expense in self.expenses:
            self.tree.insert("", "end", values=(f"{expense['sum']:.2f}", expense['category'], expense['date']))

    def calculate_sum(self):
       """Подсчитывает сумму расходов за указанный период."""
       try:
           date_from_str = self.entry_date_from.get()
           date_to_str = self.entry_date_to.get()
           
           if date_from_str and date_to_str:
               date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
               date_to = datetime.strptime(date_to_str, "%Y-%m-%d")
               
               total = sum(
                   e["sum"] for e in self.expenses 
                   if date_from <= datetime.strptime(e["date"], "%Y-%m-%d") <= date_to
               )
               messagebox.showinfo("Отчет за период", f"Сумма расходов с {date_from_str} по {date_to_str}: {total:.2f} руб.")
           else:
               messagebox.showwarning("Предупреждение", "Пожалуйста, укажите обе даты для расчета.")
               
       except ValueError:
           messagebox.showerror("Ошибка даты", "Некорректный формат даты. Используйте ГГГГ-ММ-ДД.")


    # --- Логика работы с файлами ---
    def save_data(self):
       """Сохраняет список расходов в файл JSON."""
       try:
           with open(DATA_FILE, "w", encoding="utf-8") as f:
               json.dump(self.expenses, f, ensure_ascii=False, indent=4)
           messagebox.showinfo("Сохранение", f"Данные успешно сохранены в {DATA_FILE}")
       except Exception as e:
           messagebox.showerror("Ошибка сохранения", str(e))

    def load_data_from_file(self):
       """Загружает данные из файла JSON при запуске или по кнопке."""
       if os.path.exists(DATA_FILE):
           try:
               with open(DATA_FILE, "r", encoding="utf-8") as f:
                   self.expenses = json.load(f)
               self.update_treeview()
               messagebox.showinfo("Загрузка", f"Данные успешно загружены из {DATA_FILE}")
           except Exception as e:
               messagebox.showerror("Ошибка загрузки", str(e))
       else:
           messagebox.showinfo("Файл не найден", f"Файл {DATA_FILE} не найден. Будет создан при первом сохранении.")

    def clear_all_data(self):
       """Очищает все данные из памяти и таблицы."""
       if messagebox.askyesno("Подтвердите действие", "Вы уверены? Все данные будут удалены безвозвратно."):
           self.expenses.clear()
           self.update_treeview()
           messagebox.showinfo("Очистка", "Все данные удалены.")


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    
    root.grid_rowconfigure(1, weight=1) 
    root.grid_columnconfigure(0, weight=1) 

    root.mainloop()

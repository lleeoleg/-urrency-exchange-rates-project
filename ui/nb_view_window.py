import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.database import Database


class NBViewWindow:
    
    def __init__(self, parent, db):
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("Курсы Национального Банка")
        self.window.geometry("800x600")
        
        self.create_widgets()
        self.refresh_rates()
    
    def create_widgets(self):
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(control_frame, text="Дата:").pack(side=tk.LEFT, padx=5)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(control_frame, textvariable=self.date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(control_frame, text="Фильтр", 
                  command=self.filter_by_date).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Показать все", 
                  command=self.show_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", 
                  command=self.refresh_rates).pack(side=tk.LEFT, padx=5)
        
        # Таблица
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('Валюта', 'Название', 'Курс', 'Дата', 'Загружено')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('Валюта', text='Код валюты')
        self.tree.heading('Название', text='Название валюты')
        self.tree.heading('Курс', text='Курс к KZT')
        self.tree.heading('Дата', text='Дата курса')
        self.tree.heading('Загружено', text='Дата загрузки')
        
        self.tree.column('Валюта', width=100)
        self.tree.column('Название', width=200)
        self.tree.column('Курс', width=120)
        self.tree.column('Дата', width=120)
        self.tree.column('Загружено', width=150)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.stats_label = ttk.Label(self.window, text="", font=("Arial", 9))
        self.stats_label.pack(pady=5)
    
    def refresh_rates(self, date_filter=None):
        """Обновляет список курсов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rates = self.db.get_nb_rates(date_filter)
        
        for rate in rates:
            created_at = rate.get('created_at', '')
            if isinstance(created_at, str):
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    created_at_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    created_at_str = created_at
            else:
                created_at_str = str(created_at)
            
            self.tree.insert('', 'end', values=(
                rate.get('currency_code', ''),
                rate.get('currency_name', ''),
                f"{rate.get('rate', 0):.4f}",
                rate.get('date', ''),
                created_at_str
            ))
        
        self.stats_label.config(text=f"Всего курсов: {len(rates)}")
    
    def filter_by_date(self):
        """Фильтрует курсы по дате"""
        date_str = self.date_var.get().strip()
        if date_str:
            self.refresh_rates(date_str)
        else:
            messagebox.showwarning("Предупреждение", "Введите дату в формате YYYY-MM-DD")
    
    def show_all(self):
        """Показывает все курсы"""
        self.date_var.set("")
        self.refresh_rates()


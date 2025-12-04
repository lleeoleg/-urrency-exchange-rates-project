import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from config import (CURRENCY_RATE_TYPES, ALL_CURRENCIES, LOYALTY_UNITS,
                   STATUS_SANCTIONED, STATUS_UNSANCTIONED, STATUS_WITH_REMARKS)
from excel_loader import ExcelLoader


class SearchWindow:
    
    def __init__(self, parent, db, main_window):
        self.db = db
        self.main_window = main_window
        
        self.window = tk.Toplevel(parent)
        self.window.title("Поиск курсов")
        self.window.geometry("600x500")
        
        self.create_widgets()
    
    def create_widgets(self):
        filter_frame = ttk.LabelFrame(self.window, text="Фильтры поиска")
        filter_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Тип курса валюты:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.rate_type_combo = ttk.Combobox(filter_frame, values=CURRENCY_RATE_TYPES, 
                                            width=40, state='readonly')
        self.rate_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Старшая валюта:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.senior_combo = ttk.Combobox(filter_frame, values=ALL_CURRENCIES, width=20, state='readonly')
        self.senior_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Статус:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.status_combo = ttk.Combobox(filter_frame, 
                                        values=["утвержден", "не утвержден", "есть замечание"],
                                        width=20, state='readonly')
        self.status_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Льготные условия:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.lu_combo = ttk.Combobox(filter_frame, values=LOYALTY_UNITS, width=20, state='readonly')
        self.lu_combo.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Период с:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_from_entry = ttk.Entry(filter_frame, width=15)
        self.date_from_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Период по:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_to_entry = ttk.Entry(filter_frame, width=15)
        self.date_to_entry.grid(row=5, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Поиск", 
                  command=self.search).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="В Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
    
    def search(self):
        filters = {}
        
        if self.rate_type_combo.get():
            filters['rate_type'] = self.rate_type_combo.get()
        
        if self.senior_combo.get():
            filters['senior_currency'] = self.senior_combo.get()
        
        if self.status_combo.get():
            status_map = {
                "утвержден": "санкционировано",
                "не утвержден": "не санкционировано",
                "есть замечание": "есть замечание"
            }
            filters['status'] = status_map.get(self.status_combo.get())
        
        if self.lu_combo.get():
            filters['loyalty_unit'] = self.lu_combo.get()
        
        if self.date_from_entry.get():
            filters['date_from'] = self.date_from_entry.get()
        
        if self.date_to_entry.get():
            filters['date_to'] = self.date_to_entry.get()
        
        self.main_window.refresh_rates(filters)
        self.window.destroy()
    
    def export_to_excel(self):
        filters = {}
        
        if self.rate_type_combo.get():
            filters['rate_type'] = self.rate_type_combo.get()
        
        if self.senior_combo.get():
            filters['senior_currency'] = self.senior_combo.get()
        
        if self.status_combo.get():
            status_map = {
                "утвержден": "санкционировано",
                "не утвержден": "не санкционировано",
                "есть замечание": "есть замечание"
            }
            filters['status'] = status_map.get(self.status_combo.get())
        
        if self.lu_combo.get():
            filters['loyalty_unit'] = self.lu_combo.get()
        
        if self.date_from_entry.get():
            filters['date_from'] = self.date_from_entry.get()
        
        if self.date_to_entry.get():
            filters['date_to'] = self.date_to_entry.get()
        
        # Получить курсы по фильтрам
        rates = self.db.get_rates(filters)
        
        if not rates:
            messagebox.showinfo("Информация", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            excel_loader = ExcelLoader(self.db)
            excel_loader.export_to_excel(rates, file_path)
            messagebox.showinfo("Успех", "Курсы успешно выгружены в Excel")


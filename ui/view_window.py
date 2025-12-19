import tkinter as tk
from tkinter import ttk
from config.config import LOYALTY_UNITS


class ViewWindow:
    
    def __init__(self, parent, db):
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("Просмотр последних санкционированных курсов")
        self.window.geometry("1200x700")
        
        self.create_widgets()
        self.load_rates()
    
    def create_widgets(self):
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('№', 'Тип', 'Пара валют', 'Покупка', 'Продажа', 
                  'ST1F', 'ST1J', 'ST2F', 'ST2J', 'Время')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=25)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column('№', width=50)
        self.tree.column('Тип', width=200)
        self.tree.column('Пара валют', width=120)
        self.tree.column('Покупка', width=100)
        self.tree.column('Продажа', width=100)
        self.tree.column('Время', width=150)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(self.window, text="Закрыть", 
                  command=self.window.destroy).pack(pady=10)
    
    def load_rates(self):
        rates = self.db.get_latest_sanctioned_rates()
        
        grouped = {}
        for rate in rates:
            key = (rate.get('rate_type'), 
                  rate.get('senior_currency'), 
                  rate.get('base_currency'))
            
            if key not in grouped:
                grouped[key] = {}
            
            lu = rate.get('loyalty_unit', '')
            if lu:
                grouped[key][lu] = rate
        
        for i, (key, lu_rates) in enumerate(grouped.items(), 1):
            rate_type, senior, base = key
            pair = f"{senior}/{base}"
            
            main_rate = lu_rates.get('') or list(lu_rates.values())[0] if lu_rates else None
            
            if main_rate:
                values = [
                    i,
                    rate_type,
                    pair,
                    f"{main_rate.get('buy_rate', 0):.4f}",
                    f"{main_rate.get('sell_rate', 0):.4f}",
                    self._get_lu_value(lu_rates, 'ST1F'),
                    self._get_lu_value(lu_rates, 'ST1J'),
                    self._get_lu_value(lu_rates, 'ST2F'),
                    self._get_lu_value(lu_rates, 'ST2J'),
                    f"{main_rate.get('date', '')} {main_rate.get('time', '')}"
                ]
                
                self.tree.insert('', 'end', values=values)
    
    def _get_lu_value(self, lu_rates, lu_code):
        if lu_code in lu_rates:
            rate = lu_rates[lu_code]
            return f"{rate.get('buy_rate', 0):.4f}/{rate.get('sell_rate', 0):.4f}"
        return "-"


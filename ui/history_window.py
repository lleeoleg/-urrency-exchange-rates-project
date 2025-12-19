import tkinter as tk
from tkinter import ttk
from datetime import datetime


class HistoryWindow:
    
    def __init__(self, parent, db, rate_id):
        self.db = db
        self.rate_id = rate_id
        
        self.window = tk.Toplevel(parent)
        self.window.title("История изменений")
        self.window.geometry("900x600")
        
        self.create_widgets()
        self.load_history()
    
    def create_widgets(self):
        title_label = ttk.Label(self.window, text="История изменений курса", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        table_frame = ttk.Frame(self.window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('№', 'Изменен сотрудником', 'Время изменения', 'Описание')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        self.tree.heading('№', text='№')
        self.tree.heading('Изменен сотрудником', text='Изменен сотрудником')
        self.tree.heading('Время изменения', text='Время изменения')
        self.tree.heading('Описание', text='Описание')
        
        self.tree.column('№', width=50)
        self.tree.column('Изменен сотрудником', width=200)
        self.tree.column('Время изменения', width=200)
        self.tree.column('Описание', width=400)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(self.window, text="Закрыть", 
                  command=self.window.destroy).pack(pady=10)
    
    def load_history(self):
        history = self.db.get_rate_history(self.rate_id)
        
        for i, record in enumerate(history, 1):
            try:
                changed_at = datetime.strptime(record.get('changed_at', ''), 
                                              "%Y-%m-%d %H:%M:%S")
                time_str = changed_at.strftime("%d.%m.%Y %H:%M:%S")
            except:
                time_str = record.get('changed_at', '')
            
            self.tree.insert('', 'end', values=(
                i,
                record.get('changed_by', ''),
                time_str,
                record.get('description', '')
            ))


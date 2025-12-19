import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class EditTimeWindow:
    
    def __init__(self, parent, db, rate_ids, user):
        self.db = db
        self.rate_ids = rate_ids if isinstance(rate_ids, list) else [rate_ids]
        self.user = user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Редактировать время")
        self.window.geometry("400x200")
        
        self.create_widgets()
    
    def create_widgets(self):
        ttk.Button(self.window, text="Назад", command=self.window.destroy).pack(pady=5)
        
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Дата курса (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=15)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Актуально с (ЧЧ:ММ):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.time_entry = ttk.Entry(main_frame, width=10)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.grid(row=1, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Отмена", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обновить", 
                  command=self.update_time).pack(side=tk.LEFT, padx=5)
    
    def update_time(self):
        try:
            date = self.date_entry.get()
            time = self.time_entry.get()
            
            if not date or not time:
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return
            
            updated_count = 0
            
            for rate_id in self.rate_ids:
                rate = self.db.get_rate_by_id(rate_id)
                if rate:
                    rate['date'] = date
                    rate['time'] = time
                    self.db.update_rate(rate_id, rate, self.user)
                    updated_count += 1
            
            messagebox.showinfo("Успех", f"Обновлено курсов: {updated_count}")
            self.window.destroy()
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка обновления: {str(e)}")


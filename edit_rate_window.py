
import tkinter as tk
from tkinter import ttk, messagebox
from config import CURRENCY_RATE_TYPES, ALL_CURRENCIES, LOYALTY_UNITS


class EditRateWindow:
    
    def __init__(self, parent, db, rate, user):
        self.db = db
        self.rate = rate
        self.user = user
        
        self.window = tk.Toplevel(parent)
        self.window.title("Редактировать курс")
        self.window.geometry("500x400")
        
        self.create_widgets()
        self.load_rate_data()
    
    def create_widgets(self):
        ttk.Button(self.window, text="Назад", command=self.window.destroy).pack(pady=5)
        
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(main_frame, text="Тип курса валюты:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.rate_type_combo = ttk.Combobox(main_frame, values=CURRENCY_RATE_TYPES, 
                                            width=40, state='readonly')
        self.rate_type_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Дата курса (ДД.ММ.ГГГГ):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(main_frame, width=15)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Актуально с (ЧЧ:ММ):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.time_entry = ttk.Entry(main_frame, width=10)
        self.time_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Курс:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.course_type_combo = ttk.Combobox(main_frame, values=["Стандартный", "Курс конверсии"], 
                                              width=20, state='readonly')
        self.course_type_combo.grid(row=3, column=1, padx=5, pady=5)
        self.course_type_combo.set("Стандартный")
        
        ttk.Label(main_frame, text="Старшая валюта:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.senior_combo = ttk.Combobox(main_frame, values=ALL_CURRENCIES, width=15, state='readonly')
        self.senior_combo.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Базовая валюта:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.base_combo = ttk.Combobox(main_frame, values=ALL_CURRENCIES, width=15, state='readonly')
        self.base_combo.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Покупка:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.buy_entry = ttk.Entry(main_frame, width=15)
        self.buy_entry.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Продажа:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.sell_entry = ttk.Entry(main_frame, width=15)
        self.sell_entry.grid(row=7, column=1, padx=5, pady=5)
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Сохранить", 
                  command=self.save_rate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete_rate).pack(side=tk.LEFT, padx=5)
    
    def load_rate_data(self):
        if self.rate:
            self.rate_type_combo.set(self.rate.get('rate_type', ''))
            self.date_entry.insert(0, self.rate.get('date', ''))
            self.time_entry.insert(0, self.rate.get('time', ''))
            self.senior_combo.set(self.rate.get('senior_currency', ''))
            self.base_combo.set(self.rate.get('base_currency', ''))
            self.buy_entry.insert(0, str(self.rate.get('buy_rate', 0)))
            self.sell_entry.insert(0, str(self.rate.get('sell_rate', 0)))
    
    def save_rate(self):
        try:
            rate_data = {
                'rate_type': self.rate_type_combo.get(),
                'date': self.date_entry.get(),
                'time': self.time_entry.get(),
                'senior_currency': self.senior_combo.get(),
                'base_currency': self.base_combo.get(),
                'buy_rate': float(self.buy_entry.get()),
                'sell_rate': float(self.sell_entry.get()),
                'status': self.rate.get('status', 'не санкционировано')
            }
            
            if not all([rate_data['rate_type'], rate_data['date'], rate_data['time'],
                       rate_data['senior_currency'], rate_data['base_currency']]):
                messagebox.showwarning("Предупреждение", "Заполните все поля")
                return
            
            if rate_data['senior_currency'] == rate_data['base_currency']:
                messagebox.showwarning("Предупреждение", 
                                      "Старшая и базовая валюты не могут быть одинаковыми")
                return
            
            self.db.update_rate(self.rate['id'], rate_data, self.user)
            messagebox.showinfo("Успех", "Курс успешно обновлен")
            self.window.destroy()
        
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные числовые значения")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def delete_rate(self):
        if messagebox.askyesno("Подтверждение", "Удалить этот курс?"):
            self.db.delete_rate(self.rate['id'], self.user)
            messagebox.showinfo("Успех", "Курс удален")
            self.window.destroy()


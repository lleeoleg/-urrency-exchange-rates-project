import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config.config import CURRENCY_RATE_TYPES, ALL_CURRENCIES


class AddRateWindow:
    def __init__(self, parent, db, user):
        self.db = db
        self.user = user
        self.rate_blocks = []
        self.block_frames = []  # Храним ссылки на фреймы блоков для удаления
        
        self.window = tk.Toplevel(parent)
        self.window.title("Добавить курс")
        self.window.geometry("600x700")
        
        self.create_widgets()
    
    def create_widgets(self):
        ttk.Button(self.window, text="Назад", command=self.window.destroy).pack(pady=5)

        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.add_rate_block(main_frame)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Отмена", 
                  command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Рассчитать", 
                  command=self.calculate_spread).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Добавить блок", 
                  command=lambda: self.add_rate_block(main_frame)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить блок", 
                  command=self.remove_rate_block).pack(side=tk.LEFT, padx=5)
        btn_save = tk.Button(button_frame, text="Сохранить", 
                            command=self.save_rates,
                            bg="#021aee", fg="white",
                            relief=tk.RAISED, bd=2, padx=10, pady=2)
        btn_save.pack(side=tk.LEFT, padx=5)
    
    def add_rate_block(self, parent):
        block_frame = ttk.LabelFrame(parent, text=f"Курс {len(self.rate_blocks) + 1}")
        block_frame.pack(fill=tk.X, pady=5)
        
        block_data = {'frame': block_frame}  # Сохраняем ссылку на фрейм

        ttk.Label(block_frame, text="Дата курса (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        date_entry = ttk.Entry(block_frame, width=15)
        date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        date_entry.grid(row=0, column=1, padx=5, pady=2)
        block_data['date'] = date_entry

        ttk.Label(block_frame, text="Актуально с (ЧЧ:ММ):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        time_entry = ttk.Entry(block_frame, width=10)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))
        time_entry.grid(row=0, column=3, padx=5, pady=2)
        block_data['time'] = time_entry

        ttk.Label(block_frame, text="Тип курса валюты:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        rate_type_combo = ttk.Combobox(block_frame, values=CURRENCY_RATE_TYPES, width=40, state='readonly')
        rate_type_combo.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=2)
        block_data['rate_type'] = rate_type_combo

        ttk.Label(block_frame, text="Старшая валюта:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        senior_combo = ttk.Combobox(block_frame, values=ALL_CURRENCIES, width=15, state='readonly')
        senior_combo.grid(row=2, column=1, padx=5, pady=2)
        block_data['senior_currency'] = senior_combo

        ttk.Label(block_frame, text="Базовая валюта:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=2)
        base_combo = ttk.Combobox(block_frame, values=ALL_CURRENCIES, width=15, state='readonly')
        base_combo.grid(row=2, column=3, padx=5, pady=2)
        block_data['base_currency'] = base_combo

        ttk.Label(block_frame, text="Покупка:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        buy_entry = ttk.Entry(block_frame, width=15)
        buy_entry.grid(row=3, column=1, padx=5, pady=2)
        block_data['buy_rate'] = buy_entry

        ttk.Label(block_frame, text="Продажа:").grid(row=3, column=2, sticky=tk.W, padx=5, pady=2)
        sell_entry = ttk.Entry(block_frame, width=15)
        sell_entry.grid(row=3, column=3, padx=5, pady=2)
        block_data['sell_rate'] = sell_entry
        
        ttk.Label(block_frame, text="Spread:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        spread_label = ttk.Label(block_frame, text="0.0000", foreground="blue")
        spread_label.grid(row=4, column=1, padx=5, pady=2)
        block_data['spread'] = spread_label
        
        self.rate_blocks.append(block_data)
        self.block_frames.append(block_frame)
    
    def remove_rate_block(self):
        """Удаляет последний блок курса"""
        if len(self.rate_blocks) <= 1:
            messagebox.showwarning("Предупреждение", 
                                  "Нельзя удалить последний блок. Должен остаться хотя бы один блок.")
            return
        
        # Удаляем последний блок
        last_block = self.rate_blocks.pop()
        last_frame = self.block_frames.pop()
        
        # Удаляем фрейм из интерфейса
        last_frame.destroy()
        
        # Обновляем номера блоков
        for i, block in enumerate(self.rate_blocks):
            block['frame'].config(text=f"Курс {i + 1}")
    
    def calculate_spread(self):
        for block in self.rate_blocks:
            try:
                buy = float(block['buy_rate'].get() or 0)
                sell = float(block['sell_rate'].get() or 0)
                spread = sell - buy
                block['spread'].config(text=f"{spread:.4f}")
            except ValueError:
                block['spread'].config(text="Ошибка")
    
    def save_rates(self):
        saved_count = 0
        
        for block in self.rate_blocks:
            try:
                rate_type = block['rate_type'].get()
                date = block['date'].get()
                time = block['time'].get()
                senior = block['senior_currency'].get()
                base = block['base_currency'].get()
                buy = float(block['buy_rate'].get())
                sell = float(block['sell_rate'].get())
                
                if not all([rate_type, date, time, senior, base]):
                    continue
                
                if senior == base:
                    messagebox.showwarning("Предупреждение", 
                                          f"Старшая и базовая валюты не могут быть одинаковыми")
                    continue
                
                rate_data = {
                    'rate_type': rate_type,
                    'date': date,
                    'time': time,
                    'senior_currency': senior,
                    'base_currency': base,
                    'buy_rate': buy,
                    'sell_rate': sell,
                    'status': 'не санкционировано'
                }
                
                self.db.add_rate(rate_data, self.user)
                saved_count += 1
            
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректные числовые значения")
                return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
                return
        
        if saved_count > 0:
            messagebox.showinfo("Успех", f"Сохранено курсов: {saved_count}")
            self.window.destroy()
        else:
            messagebox.showwarning("Предупреждение", "Не удалось сохранить ни одного курса")


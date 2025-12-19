import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from database.database import Database
from controller.excel_loader import ExcelLoader
from controller.nb_loader import NBLoader
from config.config import *
import ui.add_rate_window as add_rate_window
import ui.edit_rate_window as edit_rate_window
import ui.edit_time_window as edit_time_window
import ui.history_window as history_window
import ui.view_window as view_window
import ui.search_window as search_window


class MainWindow:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Курсы валют")
        self.root.geometry("1400x800")
        
        self.db = Database()
        self.excel_loader = ExcelLoader(self.db)
        self.nb_loader = NBLoader(self.db)
        
        self.current_user = "Пользователь" 
        self.is_first_load_today = True 
        
        self.create_menu()
        self.create_toolbar()
        self.create_main_content()
        
        self.refresh_rates()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить из Excel", command=self.load_from_excel)
        file_menu.add_command(label="Выгрузить в Excel", command=self.export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        rates_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Курсы", menu=rates_menu)
        rates_menu.add_command(label="Добавить курс", command=self.add_rate)
        rates_menu.add_command(label="Просмотр последних санкционированных", 
                              command=self.view_sanctioned)
        rates_menu.add_command(label="Поиск", command=self.search_rates)
        
        nb_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Нацбанк", menu=nb_menu)
        nb_menu.add_command(label="Загрузить курсы", command=self.load_nb_rates)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        btn_excel_load = tk.Button(toolbar, text="Обзор (Добавление с Excel)", 
                                   command=self.load_from_excel,
                                   bg="#90ee02", fg="black", 
                                   relief=tk.RAISED, bd=2, padx=5, pady=2)
        btn_excel_load.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="Добавить курс", 
                  command=self.add_rate).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        btn_sanction = tk.Button(toolbar, text="Санкционировать последние", 
                                 command=self.sanction_latest,
                                 bg="#D32F2F", fg="white",
                                 relief=tk.RAISED, bd=2, padx=5, pady=2)
        btn_sanction.pack(side=tk.LEFT, padx=2)
        
        btn_delete_unsanctioned = tk.Button(toolbar, text="Удалить несанкционированные", 
                                           command=self.delete_unsanctioned,
                                           bg="#D32F2F", fg="white",
                                           relief=tk.RAISED, bd=2, padx=5, pady=2)
        btn_delete_unsanctioned.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        ttk.Button(toolbar, text="Обновить", 
                  command=self.refresh_rates).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Поиск", 
                  command=self.search_rates).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Просмотр", 
                  command=self.view_sanctioned).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Вверх", 
                  command=self.scroll_to_top).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        btn_edit_time = tk.Button(toolbar, text="Редактировать время", 
                                  command=self.edit_time,
                                  bg="#FFDE03", fg="black",
                                  relief=tk.RAISED, bd=2, padx=5, pady=2)
        btn_edit_time.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar, text="В Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=2)
    
    def create_main_content(self):
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Тип', 'Дата', 'Время', 'Старшая', 'Базовая', 
                  'ЛУ', 'Покупка', 'Продажа', 'Статус')
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=25)
        
        # для чередования цветов строк
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       rowheight=25)
        style.configure("Treeview.EvenRow", background="#F5F5F5")
        style.configure("Treeview.OddRow", background="white")
        
        # теги для строк
        self.tree.tag_configure('even', background='#F5F5F5')
        self.tree.tag_configure('odd', background='white')
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Тип', text='Тип курса валюты')
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Время', text='Время')
        self.tree.heading('Старшая', text='Старшая валюта')
        self.tree.heading('Базовая', text='Базовая валюта')
        self.tree.heading('ЛУ', text='ЛУ')
        self.tree.heading('Покупка', text='Покупка')
        self.tree.heading('Продажа', text='Продажа')
        self.tree.heading('Статус', text='Статус')
        
        self.tree.column('ID', width=50)
        self.tree.column('Тип', width=200)
        self.tree.column('Дата', width=100)
        self.tree.column('Время', width=80)
        self.tree.column('Старшая', width=100)
        self.tree.column('Базовая', width=100)
        self.tree.column('ЛУ', width=80)
        self.tree.column('Покупка', width=100)
        self.tree.column('Продажа', width=100)
        self.tree.column('Статус', width=150)
        
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.create_context_menu()
        
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Санкционировать", command=self.sanction_selected)
        self.context_menu.add_command(label="Редактировать", command=self.edit_selected)
        self.context_menu.add_command(label="История", command=self.show_history)
        self.context_menu.add_command(label="Коррекция", command=self.send_for_revision)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Удалить", command=self.delete_selected)
    
    def refresh_rates(self, filters=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rates = self.db.get_rates(filters)
        
        for index, rate in enumerate(rates):
            status_icon = "✓" if rate.get('status') == 'санкционировано' else "✗"
            status_text = f"{status_icon} {rate.get('status', '')}"
            
            tag = 'even' if index % 2 == 0 else 'odd'
            
            self.tree.insert('', 'end', values=(
                rate.get('id'),
                rate.get('rate_type', ''),
                rate.get('date', ''),
                rate.get('time', ''),
                rate.get('senior_currency', ''),
                rate.get('base_currency', ''),
                rate.get('loyalty_unit', ''),
                f"{rate.get('buy_rate', 0):.4f}",
                f"{rate.get('sell_rate', 0):.4f}",
                status_text
            ), tags=(tag,))
    
    def load_from_excel(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            result = self.excel_loader.load_from_excel(
                file_path, 
                self.current_user,
                self.is_first_load_today
            )
            
            if result['success']:
                messagebox.showinfo(
                    "Успех",
                    f"Загружено: {result['loaded']}\n"
                    f"Обновлено: {result['updated']}\n"
                    f"Время начала действия: {result['time']}\n"
                    f"Дата: {result['date']}"
                )
                self.is_first_load_today = False
                self.refresh_rates()
            else:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {result.get('error', 'Неизвестная ошибка')}")
    
    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            rates = self.db.get_rates()
            self.excel_loader.export_to_excel(rates, file_path)
            messagebox.showinfo("Успех", "Курсы успешно выгружены в Excel")
    
    def add_rate(self):
        window = add_rate_window.AddRateWindow(self.root, self.db, self.current_user)
        window.window.wait_window()
        self.refresh_rates()
    
    def edit_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите курс для редактирования")
            return
        
        item = self.tree.item(selection[0])
        rate_id = item['values'][0]
        
        rate = self.db.get_rate_by_id(rate_id)
        if rate:
            if rate.get('status') == 'санкционировано':
                messagebox.showwarning("Предупреждение", "Нельзя редактировать санкционированный курс")
                return
            
            window = edit_rate_window.EditRateWindow(
                self.root, self.db, rate, self.current_user
            )
            window.window.wait_window()
            self.refresh_rates()
    
    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный курс?"):
            item = self.tree.item(selection[0])
            rate_id = item['values'][0]
            
            rate = self.db.get_rate_by_id(rate_id)
            if rate and rate.get('status') == 'санкционировано':
                messagebox.showwarning("Предупреждение", "Нельзя удалить санкционированный курс")
                return
            
            self.db.delete_rate(rate_id, self.current_user)
            self.refresh_rates()
    
    def sanction_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        rate_id = item['values'][0]
        
        self.db.sanction_rate(rate_id, self.current_user)
        self.refresh_rates()
    
    def sanction_latest(self):
        if messagebox.askyesno("Подтверждение", 
                              "Санкционировать последние курсы за сегодня?"):
            count = self.db.sanction_latest_today(self.current_user)
            messagebox.showinfo("Успех", f"Санкционировано курсов: {count}")
            self.refresh_rates()
    
    def delete_unsanctioned(self):
        if messagebox.askyesno("Подтверждение", 
                              "Удалить все несанкционированные курсы?"):
            count = self.db.delete_unsanctioned(self.current_user)
            messagebox.showinfo("Успех", f"Удалено курсов: {count}")
            self.refresh_rates()
    
    def show_history(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите курс для просмотра истории")
            return
        
        item = self.tree.item(selection[0])
        rate_id = item['values'][0]
        
        window = history_window.HistoryWindow(self.root, self.db, rate_id)
        window.window.wait_window()
    
    def send_for_revision(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        rate_id = item['values'][0]
        
        rate = self.db.get_rate_by_id(rate_id)
        if rate:
            rate['status'] = 'есть замечание'
            self.db.update_rate(rate_id, rate, self.current_user)
            self.refresh_rates()
    
    def on_item_double_click(self, event):
        self.edit_selected()
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def search_rates(self):
        window = search_window.SearchWindow(self.root, self.db, self)
        window.window.wait_window()
    
    def view_sanctioned(self):
        window = view_window.ViewWindow(self.root, self.db)
        window.window.wait_window()
    
    def load_nb_rates(self):
        import ui.nb_load_window as nb_load_window
        window = nb_load_window.NBLoadWindow(self.root, self.db)
        window.window.wait_window()
    
    def edit_time(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите курс(ы) для редактирования времени")
            return
        
        rate_ids = []
        for item in selection:
            rate_id = self.tree.item(item)['values'][0]
            rate_ids.append(rate_id)
        
        window = edit_time_window.EditTimeWindow(self.root, self.db, rate_ids, self.current_user)
        window.window.wait_window()
        self.refresh_rates()
    
    def scroll_to_top(self):
        self.tree.see(self.tree.get_children()[0] if self.tree.get_children() else '')


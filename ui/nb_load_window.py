import tkinter as tk
from tkinter import ttk, messagebox
import threading
from controller.nb_loader import NBLoader


class NBLoadWindow:
    
    def __init__(self, parent, db):
        self.db = db
        self.nb_loader = NBLoader(db)
        
        self.window = tk.Toplevel(parent)
        self.window.title("Загрузка курсов Нацбанка")
        self.window.geometry("500x200")
        self.window.resizable(False, False)
        
        self.is_loading = False
        self.load_thread = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        info_label = ttk.Label(main_frame, 
                              text="Загрузка курсов валют с сайта Национального Банка РК",
                              font=("Arial", 10))
        info_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Готов к загрузке", 
                                      font=("Arial", 9))
        self.status_label.pack(pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.btn_load = tk.Button(button_frame, text="Загрузить курсы", 
                                  command=self.start_load,
                                  bg="#4CAF50", fg="white",
                                  relief=tk.RAISED, bd=2, padx=15, pady=5,
                                  font=("Arial", 9, "bold"))
        self.btn_load.pack(side=tk.LEFT, padx=5)
        
        self.btn_close = tk.Button(button_frame, text="Закрыть", 
                                   command=self.window.destroy,
                                   relief=tk.RAISED, bd=2, padx=15, pady=5)
        self.btn_close.pack(side=tk.LEFT, padx=5)
        
        self.btn_view = tk.Button(button_frame, text="Просмотр курсов", 
                                  command=self.view_rates,
                                  bg="#2196F3", fg="white",
                                  relief=tk.RAISED, bd=2, padx=15, pady=5)
        self.btn_view.pack(side=tk.LEFT, padx=5)
    
    def start_load(self):
        """Запускает загрузку в отдельном потоке"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.btn_load.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="Загрузка курсов...")
        
        self.load_thread = threading.Thread(target=self.load_rates_thread, daemon=True)
        self.load_thread.start()
    
    def load_rates_thread(self):
        """Загружает курсы в отдельном потоке"""
        try:
            result = self.nb_loader.load_rates()
            
            self.window.after(0, self.load_complete, result)
        except Exception as e:
            self.window.after(0, self.load_error, str(e))
    
    def load_complete(self, result):
        """Обработка завершения загрузки"""
        self.is_loading = False
        self.progress.stop()
        self.btn_load.config(state=tk.NORMAL)
        
        if result['success']:
            self.status_label.config(text=f"Загружено: {result['loaded']} курсов")
            messagebox.showinfo("Успех", 
                              f"Курсы успешно загружены!\n\n"
                              f"Загружено: {result['loaded']} курсов\n"
                              f"Дата: {result.get('date', 'N/A')}")
        else:
            self.status_label.config(text="Ошибка загрузки")
            messagebox.showerror("Ошибка", 
                               f"Не удалось загрузить курсы:\n{result.get('error', 'Неизвестная ошибка')}")
    
    def load_error(self, error_msg):
        """Обработка ошибки загрузки"""
        self.is_loading = False
        self.progress.stop()
        self.btn_load.config(state=tk.NORMAL)
        self.status_label.config(text="Ошибка загрузки")
        messagebox.showerror("Ошибка", f"Ошибка при загрузке: {error_msg}")
    
    def view_rates(self):
        """Открывает окно просмотра курсов Нацбанка"""
        import ui.nb_view_window as nb_view_window
        window = nb_view_window.NBViewWindow(self.window, self.db)
        window.window.wait_window()


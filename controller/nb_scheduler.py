import schedule
import time
from database.database import Database
from controller.nb_loader import NBLoader
import pytz
from datetime import datetime


def update_nb_rates():
    db = Database()
    loader = NBLoader(db)
    
    result = loader.load_rates()
    
    if result['success']:
        print(f"[{datetime.now()}] Успешно загружено курсов: {result['loaded']}")
    else:
        print(f"[{datetime.now()}] Ошибка загрузки: {result.get('error', '')}")


def main():
    schedule.every().day.at("09:00").do(update_nb_rates)
    
    print("Планировщик запущен. Ожидание 9:00 по времени Астаны...")
    print("Для остановки нажмите Ctrl+C")
    
    update_nb_rates()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПланировщик остановлен")

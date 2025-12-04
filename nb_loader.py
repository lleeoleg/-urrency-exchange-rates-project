import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz
from typing import List, Dict
from database import Database
from config import NB_RSS_URL, NB_TIMEZONE, PRIORITY_CURRENCY_PAIRS


class NBLoader:
    
    def __init__(self, db: Database):
        self.db = db
        self.url = NB_RSS_URL
    
    def load_rates(self) -> Dict:
        try:
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            date_elem = root.find('.//date')
            if date_elem is not None:
                date_str = date_elem.text
            else:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            items = root.findall('.//item')
            
            loaded_count = 0
            
            for item in items:
                try:
                    # Извлекаем данные
                    title = item.find('title')
                    description = item.find('description')
                    pub_date = item.find('pubDate')
                    
                    if title is not None and description is not None:
                        currency_code = self._extract_currency_code(title.text)
                        currency_name = self._extract_currency_name(title.text)
                        rate = self._extract_rate(description.text)
                        
                        if currency_code and rate and rate > 0:
                            self.db.add_nb_rate(
                                currency_code,
                                currency_name,
                                rate,
                                date_str
                            )
                            loaded_count += 1
                
                except Exception as e:
                    print(f"Ошибка при обработке курса: {e}")
                    continue
            
            return {
                'success': True,
                'loaded': loaded_count,
                'date': date_str
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'loaded': 0
            }
    
    def _extract_currency_code(self, title: str) -> str:
        parts = title.split('/')
        if len(parts) > 0:
            return parts[0].strip().upper()
        return title.strip().upper()
    
    def _extract_currency_name(self, title: str) -> str:
        parts = title.split('-')
        if len(parts) > 1:
            return parts[1].strip()
        return title.strip()
    
    def _extract_rate(self, description: str) -> float:
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', description)
            if numbers:
                return float(numbers[0])
        except:
            pass
        return 0.0
    
    def get_priority_rates(self, date: str = None) -> List[Dict]:
        nb_rates = self.db.get_nb_rates(date)
        
        rates_dict = {rate['currency_code']: rate['rate'] for rate in nb_rates}
        
        priority_rates = []
        
        for senior, base in PRIORITY_CURRENCY_PAIRS:
            if senior in rates_dict:
                priority_rates.append({
                    'senior_currency': senior,
                    'base_currency': base,
                    'rate': rates_dict[senior]
                })
        
        return priority_rates
    
    def schedule_daily_update(self):
        try:
            import schedule
            import time
            import threading
            
            def update_job():
                result = self.load_rates()
                print(f"Обновление курсов Нацбанка: {result}")
            
            schedule.every().day.at("09:00").do(update_job)
            
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            
            thread = threading.Thread(target=run_scheduler, daemon=True)
            thread.start()
        except ImportError:
            print("Библиотека schedule не установлена. Автоматическое обновление недоступно.")


import pandas as pd
import datetime
from typing import List, Dict
from database import Database


class ExcelLoader:
    
    def __init__(self, db: Database):
        self.db = db
    
    def load_from_excel(self, file_path: str, user: str = "System", 
                       is_first_load: bool = False) -> Dict:
        try:
            df = pd.read_excel(file_path)
            
            load_time = datetime.datetime.now()
            start_time = load_time + datetime.timedelta(minutes=7)
            time_str = start_time.strftime("%H:%M")
            date_str = load_time.strftime("%d.%m.%Y")
            
            loaded_count = 0
            updated_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    rate_data = self._parse_row(row, date_str, time_str)
                    
                    if rate_data:
                        existing = self._find_existing_rate(rate_data)
                        
                        if existing:
                            if is_first_load or self._has_changes(existing, rate_data):
                                self.db.update_rate(existing['id'], rate_data, user)
                                updated_count += 1
                        else:
                            self.db.add_rate(rate_data, user)
                            loaded_count += 1
                
                except Exception as e:
                    errors.append(f"Строка {index + 2}: {str(e)}")
            
            return {
                'success': True,
                'loaded': loaded_count,
                'updated': updated_count,
                'errors': errors,
                'time': time_str,
                'date': date_str
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'loaded': 0,
                'updated': 0,
                'errors': []
            }
    
    def _parse_row(self, row: pd.Series, date: str, time: str) -> Dict:
        rate_data = {
            'rate_type': str(row.get('Тип курса валюты', '')),
            'date': date,
            'time': time,
            'senior_currency': str(row.get('Старшая валюта', '')),
            'base_currency': str(row.get('Базовая валюта', '')),
            'loyalty_unit': str(row.get('ЛУ', '')) if pd.notna(row.get('ЛУ', '')) else None,
            'buy_rate': float(row.get('Покупка', 0)),
            'sell_rate': float(row.get('Продажа', 0)),
            'status': 'не санкционировано'
        }
        
        return rate_data
    
    def _find_existing_rate(self, rate_data: Dict) -> Dict:
        filters = {
            'rate_type': rate_data['rate_type'],
            'senior_currency': rate_data['senior_currency'],
            'base_currency': rate_data['base_currency'],
            'date': rate_data['date']
        }
        
        if rate_data.get('loyalty_unit'):
            filters['loyalty_unit'] = rate_data['loyalty_unit']
        
        rates = self.db.get_rates(filters)
        
        for rate in rates:
            if rate.get('loyalty_unit') == rate_data.get('loyalty_unit'):
                return rate
        
        return None
    
    def _has_changes(self, existing: Dict, new: Dict) -> bool:
        return (
            existing.get('buy_rate') != new.get('buy_rate') or
            existing.get('sell_rate') != new.get('sell_rate') or
            existing.get('time') != new.get('time')
        )
    
    def export_to_excel(self, rates: List[Dict], file_path: str):
        data = []
        
        for i, rate in enumerate(rates, 1):
            data.append({
                '№': i,
                'Тип курса валюты': rate.get('rate_type', ''),
                'Дата': rate.get('date', ''),
                'Время': rate.get('time', ''),
                'Старшая валюта': rate.get('senior_currency', ''),
                'Базовая валюта': rate.get('base_currency', ''),
                'Льготные условия': rate.get('loyalty_unit', ''),
                'Покупка': rate.get('buy_rate', 0),
                'Продажа': rate.get('sell_rate', 0)
            })
        
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Курсы валют', index=False)
            
            worksheet = writer.sheets['Курсы валют']
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)


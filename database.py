import sqlite3
import datetime
from typing import List, Dict, Optional, Tuple
from config import DATABASE_NAME


class Database:
    
    def __init__(self):
        self.db_name = DATABASE_NAME
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rate_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                senior_currency TEXT NOT NULL,
                base_currency TEXT NOT NULL,
                loyalty_unit TEXT,
                buy_rate REAL NOT NULL,
                sell_rate REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'не санкционировано',
                created_at TEXT NOT NULL,
                updated_at TEXT,
                created_by TEXT,
                updated_by TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rate_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                description TEXT,
                old_values TEXT,
                new_values TEXT,
                FOREIGN KEY (rate_id) REFERENCES currency_rates(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nb_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_code TEXT NOT NULL,
                currency_name TEXT,
                rate REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(currency_code, date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_rate(self, rate_data: Dict, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO currency_rates 
            (rate_type, date, time, senior_currency, base_currency, 
             loyalty_unit, buy_rate, sell_rate, status, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rate_data['rate_type'],
            rate_data['date'],
            rate_data['time'],
            rate_data['senior_currency'],
            rate_data['base_currency'],
            rate_data.get('loyalty_unit'),
            rate_data['buy_rate'],
            rate_data['sell_rate'],
            rate_data.get('status', 'не санкционировано'),
            now,
            user
        ))
        
        rate_id = cursor.lastrowid
        
        self.add_history(rate_id, "Добавление нового курса валюты", user, rate_data)
        
        conn.commit()
        conn.close()
        
        return rate_id
    
    def update_rate(self, rate_id: int, rate_data: Dict, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = ?", (rate_id,))
        old_data = cursor.fetchone()
        old_dict = self._row_to_dict(old_data, cursor.description) if old_data else {}
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE currency_rates 
            SET rate_type = ?, date = ?, time = ?, senior_currency = ?,
                base_currency = ?, loyalty_unit = ?, buy_rate = ?,
                sell_rate = ?, status = ?, updated_at = ?, updated_by = ?
            WHERE id = ?
        """, (
            rate_data['rate_type'],
            rate_data['date'],
            rate_data['time'],
            rate_data['senior_currency'],
            rate_data['base_currency'],
            rate_data.get('loyalty_unit'),
            rate_data['buy_rate'],
            rate_data['sell_rate'],
            rate_data.get('status', old_dict.get('status', 'не санкционировано')),
            now,
            user,
            rate_id
        ))
        
        self.add_history(rate_id, "Изменение курса валюты", user, rate_data, old_dict)
        
        conn.commit()
        conn.close()
    
    def delete_rate(self, rate_id: int, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = ?", (rate_id,))
        old_data = cursor.fetchone()
        old_dict = self._row_to_dict(old_data, cursor.description) if old_data else {}
        
        cursor.execute("DELETE FROM currency_rates WHERE id = ?", (rate_id,))
        
        self.add_history(rate_id, "Удаление курса валюты", user, {}, old_dict)
        
        conn.commit()
        conn.close()
    
    def sanction_rate(self, rate_id: int, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE currency_rates 
            SET status = ?, updated_at = ?, updated_by = ?
            WHERE id = ?
        """, (
            'санкционировано',
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user,
            rate_id
        ))
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = ?", (rate_id,))
        rate_data = cursor.fetchone()
        rate_dict = self._row_to_dict(rate_data, cursor.description) if rate_data else {}
        
        self.add_history(rate_id, "Санкционирован курс валюты", user, rate_dict)
        
        conn.commit()
        conn.close()
    
    def sanction_latest_today(self, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        
        cursor.execute("""
            SELECT id FROM currency_rates 
            WHERE date = ? AND status = 'не санкционировано'
            ORDER BY time DESC
        """, (today,))
        
        rate_ids = [row[0] for row in cursor.fetchall()]
        
        for rate_id in rate_ids:
            self.sanction_rate(rate_id, user)
        
        conn.close()
        
        return len(rate_ids)
    
    def delete_unsanctioned(self, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM currency_rates WHERE status = 'не санкционировано'")
        rate_ids = [row[0] for row in cursor.fetchall()]
        
        for rate_id in rate_ids:
            self.delete_rate(rate_id, user)
        
        conn.close()
        
        return len(rate_ids)
    
    def get_rates(self, filters: Optional[Dict] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM currency_rates WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('rate_type'):
                query += " AND rate_type = ?"
                params.append(filters['rate_type'])
            
            if filters.get('senior_currency'):
                query += " AND senior_currency = ?"
                params.append(filters['senior_currency'])
            
            if filters.get('status'):
                query += " AND status = ?"
                params.append(filters['status'])
            
            if filters.get('loyalty_unit'):
                query += " AND loyalty_unit = ?"
                params.append(filters['loyalty_unit'])
            
            if filters.get('date_from'):
                query += " AND date >= ?"
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += " AND date <= ?"
                params.append(filters['date_to'])
        
        query += " ORDER BY date DESC, time DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        rates = []
        for row in rows:
            rates.append(self._row_to_dict(row, cursor.description))
        
        conn.close()
        
        return rates
    
    def get_rate_by_id(self, rate_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = ?", (rate_id,))
        row = cursor.fetchone()
        
        if row:
            rate = self._row_to_dict(row, cursor.description)
        else:
            rate = None
        
        conn.close()
        
        return rate
    
    def get_rate_history(self, rate_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM rate_history 
            WHERE rate_id = ? 
            ORDER BY changed_at DESC
        """, (rate_id,))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append(self._row_to_dict(row, cursor.description))
        
        conn.close()
        
        return history
    
    def get_latest_sanctioned_rates(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM currency_rates 
            WHERE status = 'санкционировано'
            ORDER BY date DESC, time DESC
            LIMIT 100
        """)
        
        rows = cursor.fetchall()
        
        rates = []
        for row in rows:
            rates.append(self._row_to_dict(row, cursor.description))
        
        conn.close()
        
        return rates
    
    def add_history(self, rate_id: int, action: str, user: str, 
                   new_values: Dict = None, old_values: Dict = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = ?", (rate_id,))
        rate_row = cursor.fetchone()
        rate_dict = self._row_to_dict(rate_row, cursor.description) if rate_row else {}
        
        description = self._format_history_description(
            action, rate_dict, new_values, old_values
        )
        
        cursor.execute("""
            INSERT INTO rate_history 
            (rate_id, action, changed_by, changed_at, description, old_values, new_values)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rate_id,
            action,
            user,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            description,
            str(old_values) if old_values else None,
            str(new_values) if new_values else None
        ))
        
        conn.commit()
        conn.close()
    
    def _format_history_description(self, action: str, rate_dict: Dict,
                                   new_values: Dict = None, old_values: Dict = None) -> str:
        currency = rate_dict.get('senior_currency', '')
        rate_type = rate_dict.get('rate_type', '')
        buy = rate_dict.get('buy_rate', '')
        sell = rate_dict.get('sell_rate', '')
        
        if action == "Добавление нового курса валюты":
            return f'Добавление нового курса валюты "{currency}": тип курса валюты – {rate_type}, покупка - {buy}, продажа - {sell}'
        elif action == "Изменение курса валюты":
            return f'Изменение курса валюты "{currency}": тип курса валюты – {rate_type}, покупка - {buy}, продажа - {sell}'
        elif action == "Санкционирован курс валюты":
            return f'Санкционирован курс валюты'
        else:
            return action
    
    def _row_to_dict(self, row: Tuple, description) -> Dict:
        if not row:
            return {}
        
        return {
            desc[0]: value 
            for desc, value in zip(description, row)
        }
    
    def add_nb_rate(self, currency_code: str, currency_name: str, 
                   rate: float, date: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT OR REPLACE INTO nb_rates 
            (currency_code, currency_name, rate, date, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (currency_code, currency_name, rate, date, now))
        
        conn.commit()
        conn.close()
    
    def get_nb_rates(self, date: Optional[str] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if date:
            cursor.execute("""
                SELECT * FROM nb_rates 
                WHERE date = ?
                ORDER BY currency_code
            """, (date,))
        else:
            cursor.execute("""
                SELECT * FROM nb_rates 
                ORDER BY date DESC, currency_code
            """)
        
        rows = cursor.fetchall()
        
        rates = []
        for row in rows:
            rates.append(self._row_to_dict(row, cursor.description))
        
        conn.close()
        
        return rates


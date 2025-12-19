import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
import psycopg2.extras
import datetime
from typing import List, Dict, Optional, Tuple
from config.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


class Database:
    
    def __init__(self):
        self.connection_params = {
            'host': DB_HOST,
            'port': DB_PORT,
            'database': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD
        }
        self.init_database()
    
    def get_connection(self):
        """Создает новое соединение с базой данных"""
        return psycopg2.connect(**self.connection_params)
    
    def init_database(self):
        """Инициализирует таблицы в базе данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Создание таблицы currency_rates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS currency_rates (
                id SERIAL PRIMARY KEY,
                rate_type VARCHAR(255) NOT NULL,
                date VARCHAR(50) NOT NULL,
                time VARCHAR(50) NOT NULL,
                senior_currency VARCHAR(10) NOT NULL,
                base_currency VARCHAR(10) NOT NULL,
                loyalty_unit VARCHAR(10),
                buy_rate NUMERIC(15, 4) NOT NULL,
                sell_rate NUMERIC(15, 4) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'не санкционировано',
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP,
                created_by VARCHAR(100),
                updated_by VARCHAR(100)
            )
        """)
        
        # Создание таблицы rate_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_history (
                id SERIAL PRIMARY KEY,
                rate_id INTEGER NOT NULL,
                action VARCHAR(255) NOT NULL,
                changed_by VARCHAR(100) NOT NULL,
                changed_at TIMESTAMP NOT NULL,
                description TEXT,
                old_values TEXT,
                new_values TEXT,
                FOREIGN KEY (rate_id) REFERENCES currency_rates(id) ON DELETE CASCADE
            )
        """)
        
        # Создание таблицы nb_rates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nb_rates (
                id SERIAL PRIMARY KEY,
                currency_code VARCHAR(10) NOT NULL,
                currency_name VARCHAR(100),
                rate NUMERIC(15, 4) NOT NULL,
                date VARCHAR(50) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                UNIQUE(currency_code, date)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def add_rate(self, rate_data: Dict, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        
        cursor.execute("""
            INSERT INTO currency_rates 
            (rate_type, date, time, senior_currency, base_currency, 
             loyalty_unit, buy_rate, sell_rate, status, created_at, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
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
        
        rate_id = cursor.fetchone()[0]
        
        self.add_history(rate_id, "Добавление нового курса валюты", user, rate_data)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return rate_id
    
    def update_rate(self, rate_id: int, rate_data: Dict, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = %s", (rate_id,))
        old_data = cursor.fetchone()
        old_dict = self._row_to_dict(old_data, cursor.description) if old_data else {}
        
        now = datetime.datetime.now()
        
        cursor.execute("""
            UPDATE currency_rates 
            SET rate_type = %s, date = %s, time = %s, senior_currency = %s,
                base_currency = %s, loyalty_unit = %s, buy_rate = %s,
                sell_rate = %s, status = %s, updated_at = %s, updated_by = %s
            WHERE id = %s
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
        cursor.close()
        conn.close()
    
    def delete_rate(self, rate_id: int, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = %s", (rate_id,))
        old_data = cursor.fetchone()
        old_dict = self._row_to_dict(old_data, cursor.description) if old_data else {}
        
        cursor.execute("DELETE FROM currency_rates WHERE id = %s", (rate_id,))
        
        self.add_history(rate_id, "Удаление курса валюты", user, {}, old_dict)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def sanction_rate(self, rate_id: int, user: str = "System"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now()
        
        cursor.execute("""
            UPDATE currency_rates 
            SET status = %s, updated_at = %s, updated_by = %s
            WHERE id = %s
        """, (
            'санкционировано',
            now,
            user,
            rate_id
        ))
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = %s", (rate_id,))
        rate_data = cursor.fetchone()
        rate_dict = self._row_to_dict(rate_data, cursor.description) if rate_data else {}
        
        self.add_history(rate_id, "Санкционирован курс валюты", user, rate_dict)
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def sanction_latest_today(self, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.datetime.now().strftime("%d.%m.%Y")
        
        cursor.execute("""
            SELECT id FROM currency_rates 
            WHERE date = %s AND status = 'не санкционировано'
            ORDER BY time DESC
        """, (today,))
        
        rate_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        for rate_id in rate_ids:
            self.sanction_rate(rate_id, user)
        
        return len(rate_ids)
    
    def delete_unsanctioned(self, user: str = "System") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM currency_rates WHERE status = 'не санкционировано'")
        rate_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        for rate_id in rate_ids:
            self.delete_rate(rate_id, user)
        
        return len(rate_ids)
    
    def get_rates(self, filters: Optional[Dict] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = "SELECT * FROM currency_rates WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('rate_type'):
                query += " AND rate_type = %s"
                params.append(filters['rate_type'])
            
            if filters.get('senior_currency'):
                query += " AND senior_currency = %s"
                params.append(filters['senior_currency'])
            
            if filters.get('status'):
                query += " AND status = %s"
                params.append(filters['status'])
            
            if filters.get('loyalty_unit'):
                query += " AND loyalty_unit = %s"
                params.append(filters['loyalty_unit'])
            
            if filters.get('date_from'):
                query += " AND date >= %s"
                params.append(filters['date_from'])
            
            if filters.get('date_to'):
                query += " AND date <= %s"
                params.append(filters['date_to'])
        
        query += " ORDER BY date DESC, time DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        rates = []
        for row in rows:
            rates.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return rates
    
    def get_rate_by_id(self, rate_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM currency_rates WHERE id = %s", (rate_id,))
        row = cursor.fetchone()
        
        if row:
            rate = dict(row)
        else:
            rate = None
        
        cursor.close()
        conn.close()
        
        return rate
    
    def get_rate_history(self, rate_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM rate_history 
            WHERE rate_id = %s 
            ORDER BY changed_at DESC
        """, (rate_id,))
        
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return history
    
    def get_latest_sanctioned_rates(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM currency_rates 
            WHERE status = 'санкционировано'
            ORDER BY date DESC, time DESC
            LIMIT 100
        """)
        
        rows = cursor.fetchall()
        
        rates = []
        for row in rows:
            rates.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return rates
    
    def add_history(self, rate_id: int, action: str, user: str, 
                   new_values: Dict = None, old_values: Dict = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        #существует ли курс
        cursor.execute("SELECT * FROM currency_rates WHERE id = %s", (rate_id,))
        rate_row = cursor.fetchone()
        rate_dict = self._row_to_dict(rate_row, cursor.description) if rate_row else {}
        
        description = self._format_history_description(
            action, rate_dict, new_values, old_values
        )
        
        now = datetime.datetime.now()
        
        cursor.execute("""
            INSERT INTO rate_history 
            (rate_id, action, changed_by, changed_at, description, old_values, new_values)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            rate_id,
            action,
            user,
            now,
            description,
            str(old_values) if old_values else None,
            str(new_values) if new_values else None
        ))
        
        conn.commit()
        cursor.close()
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
        
        now = datetime.datetime.now()
        
        cursor.execute("""
            INSERT INTO nb_rates 
            (currency_code, currency_name, rate, date, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (currency_code, date) 
            DO UPDATE SET 
                currency_name = EXCLUDED.currency_name,
                rate = EXCLUDED.rate,
                created_at = EXCLUDED.created_at
        """, (currency_code, currency_name, rate, date, now))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_nb_rates(self, date: Optional[str] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        if date:
            cursor.execute("""
                SELECT * FROM nb_rates 
                WHERE date = %s
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
            rates.append(dict(row))
        
        cursor.close()
        conn.close()
        
        return rates

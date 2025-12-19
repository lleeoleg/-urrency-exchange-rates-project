"""
Скрипт для создания базы данных PostgreSQL
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def create_database():
    """Создает бд"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {DB_NAME}')
            print(f"База данных '{DB_NAME}' успешно создана")
        else:
            print(f"База данных '{DB_NAME}' уже существует")
        
        cursor.close()
        conn.close()
        
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from database.database import Database
        db = Database()
        print("Таблицы успешно созданы")
        
    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        print("\nУбедитесь, что:")
        print("1. PostgreSQL установлен и запущен")
        print("2. Пользователь и пароль в config/config.py правильные")
        print("3. У пользователя есть права на создание баз данных")

if __name__ == "__main__":
    create_database()


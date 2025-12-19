"""
Конфигурация для тестов
"""
import pytest
import sys
import os
import tempfile
import shutil

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def temp_db():
    """Создает временную базу данных для тестов"""
    import psycopg2
    from config.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD
    from database.database import Database
    
    # Создаем временную базу данных
    test_db_name = "test_currency_rates"
    
    # Подключаемся к postgres для создания тестовой БД
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database='postgres',
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Удаляем тестовую БД если существует
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    except:
        pass
    cursor.execute(f"CREATE DATABASE {test_db_name}")
    cursor.close()
    conn.close()
    
    # Создаем объект базы данных с тестовой БД
    # Используем прямое подключение к тестовой БД
    db = Database()
    # Временно переопределяем connection_params
    original_params = db.connection_params.copy()
    db.connection_params['database'] = test_db_name
    
    # Переинициализируем БД
    db.init_database()
    
    yield db
    
    # Очистка после тестов
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        # Закрываем все соединения с тестовой БД
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid()
        """, (test_db_name,))
        cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при очистке тестовой БД: {e}")

@pytest.fixture
def sample_rate_data():
    """Возвращает пример данных курса"""
    return {
        'rate_type': 'Курс покрытия',
        'date': '19.12.2025',
        'time': '10:00',
        'senior_currency': 'USD',
        'base_currency': 'KZT',
        'buy_rate': 450.50,
        'sell_rate': 451.00,
        'status': 'не санкционировано'
    }

@pytest.fixture
def sample_excel_data():
    """Возвращает пример данных для Excel"""
    return {
        'Тип курса валюты': 'Курс покрытия',
        'Старшая валюта': 'USD',
        'Базовая валюта': 'KZT',
        'Покупка': 450.50,
        'Продажа': 451.00,
        'ЛУ': None
    }


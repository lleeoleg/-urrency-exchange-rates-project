# Приложение "Курсы валют"

Приложение для управления курсами валют банка.

## Требования

- Python 3.8+
- PostgreSQL 12+

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Установите и запустите PostgreSQL на вашем компьютере.

3. Настройте подключение к базе данных в файле `config/config.py`:
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "currency_rates"
DB_USER = "postgres"
DB_PASSWORD = "ваш_пароль"
```

4. Создайте базу данных:
```bash
python database/setup_db.py
```

## Запуск

```bash
python main.py
```

## Тестирование

Для запуска тестов:

```bash
python tests/run_tests.py
```

или

```bash
pytest tests/ -v
```

Подробнее о тестах см. `tests/README.md`

## Структура проекта

```
Python-Project/
├── main.py                    # Точка входа приложения
├── config/                    # Конфигурация
│   └── config.py              # Конфигурационные параметры
├── database/                  # Работа с базой данных
│   ├── database.py            # Модуль работы с базой данных
│   └── setup_db.py            # Скрипт создания базы данных
├── controller/                # Бизнес-логика
│   ├── excel_loader.py        # Модуль загрузки/выгрузки Excel
│   ├── nb_loader.py           # Модуль загрузки курсов с сайта Нацбанка
│   └── nb_scheduler.py        # Планировщик автоматической загрузки
└── ui/                        # Пользовательский интерфейс
    ├── main_window.py         # Главное окно приложения
    ├── add_rate_window.py     # Окно добавления курса
    ├── edit_rate_window.py    # Окно редактирования курса
    ├── edit_time_window.py    # Окно редактирования времени
    ├── history_window.py      # Окно истории изменений
    ├── view_window.py         # Окно просмотра курсов
    ├── search_window.py       # Окно поиска
    ├── nb_load_window.py      # Окно загрузки курсов Нацбанка
    └── nb_view_window.py      # Окно просмотра курсов Нацбанка
└── tests/                     # Тесты
    ├── test_database.py       # Тесты для database.py
    ├── test_excel_loader.py   # Тесты для excel_loader.py
    ├── test_nb_loader.py      # Тесты для nb_loader.py
    └── run_tests.py           # Скрипт запуска тестов
```


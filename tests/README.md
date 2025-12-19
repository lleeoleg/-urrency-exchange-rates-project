# Тесты проекта "Курсы валют"

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Конфигурация и фикстуры
├── test_database.py         # Тесты для database.py
├── test_excel_loader.py     # Тесты для excel_loader.py
├── test_nb_loader.py        # Тесты для nb_loader.py
├── run_tests.py             # Скрипт запуска тестов
└── README.md                # Этот файл
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск тестов

### Все тесты

```bash
python tests/run_tests.py
```

или

```bash
pytest tests/ -v
```

### Конкретный модуль

```bash
pytest tests/test_database.py -v
pytest tests/test_excel_loader.py -v
pytest tests/test_nb_loader.py -v
```

### Конкретный тест

```bash
pytest tests/test_database.py::TestDatabase::test_add_rate -v
```

## Просмотр отчетов

После запуска тестов создаются отчеты:

- **HTML отчет**: `tests/htmlcov/index.html` - откройте в браузере для просмотра покрытия кода
- **XML отчет**: `tests/test-results.xml` - для интеграции с CI/CD системами

## Покрытие кода

Для просмотра покрытия кода:

```bash
pytest tests/ --cov=database --cov=controller --cov-report=html
```

Затем откройте `tests/htmlcov/index.html` в браузере.

## Фикстуры

В `conftest.py` определены следующие фикстуры:

- `temp_db` - временная база данных для тестов
- `sample_rate_data` - пример данных курса
- `sample_excel_data` - пример данных для Excel

## Добавление новых тестов

1. Создайте новый файл `test_<module_name>.py`
2. Импортируйте необходимые модули
3. Используйте фикстуры из `conftest.py`
4. Запустите тесты для проверки

## Пример теста

```python
def test_example(temp_db, sample_rate_data):
    """Описание теста"""
    # Arrange (подготовка)
    rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
    
    # Act (действие)
    rate = temp_db.get_rate_by_id(rate_id)
    
    # Assert (проверка)
    assert rate is not None
    assert rate['senior_currency'] == 'USD'
```


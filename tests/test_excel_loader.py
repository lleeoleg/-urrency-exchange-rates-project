import pytest
import pandas as pd
import tempfile
import os
from controller.excel_loader import ExcelLoader


class TestExcelLoader:
    """Тесты для класса ExcelLoader"""
    
    def test_init(self, temp_db):
        """Тест инициализации ExcelLoader"""
        loader = ExcelLoader(temp_db)
        assert loader.db == temp_db
    
    def test_parse_row(self, temp_db, sample_excel_data):
        """Тест парсинга строки Excel"""
        loader = ExcelLoader(temp_db)
        
        row = pd.Series(sample_excel_data)
        date = "19.12.2025"
        time = "10:00"
        
        rate_data = loader._parse_row(row, date, time)
        
        assert rate_data['rate_type'] == sample_excel_data['Тип курса валюты']
        assert rate_data['senior_currency'] == sample_excel_data['Старшая валюта']
        assert rate_data['base_currency'] == sample_excel_data['Базовая валюта']
        assert rate_data['buy_rate'] == sample_excel_data['Покупка']
        assert rate_data['sell_rate'] == sample_excel_data['Продажа']
        assert rate_data['date'] == date
        assert rate_data['time'] == time
    
    def test_has_changes(self, temp_db):
        """Тест проверки изменений"""
        loader = ExcelLoader(temp_db)
        
        existing = {
            'buy_rate': 450.50,
            'sell_rate': 451.00,
            'time': '10:00'
        }
        
        new_same = {
            'buy_rate': 450.50,
            'sell_rate': 451.00,
            'time': '10:00'
        }
        
        new_different = {
            'buy_rate': 460.00,
            'sell_rate': 461.00,
            'time': '10:00'
        }
        
        assert loader._has_changes(existing, new_same) == False
        assert loader._has_changes(existing, new_different) == True
    
    def test_export_to_excel(self, temp_db, sample_rate_data):
        """Тест экспорта в Excel"""
        loader = ExcelLoader(temp_db)
        
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        rates = temp_db.get_rates()
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            loader.export_to_excel(rates, tmp_path)
            
            assert os.path.exists(tmp_path)
            
            df = pd.read_excel(tmp_path)
            assert len(df) >= 1
            assert 'Тип курса валюты' in df.columns
            assert 'Старшая валюта' in df.columns
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_load_from_excel(self, temp_db, sample_excel_data):
        """Тест загрузки из Excel"""
        loader = ExcelLoader(temp_db)
        
        df = pd.DataFrame([sample_excel_data])
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            df.to_excel(tmp_path, index=False)
        
        try:
            result = loader.load_from_excel(tmp_path, "TestUser", True)
            
            assert result['success'] == True
            assert result['loaded'] >= 1 or result['updated'] >= 1
            
            rates = temp_db.get_rates()
            assert len(rates) >= 1
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


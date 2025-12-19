import pytest
from datetime import datetime


class TestDatabase:
    """Тесты для класса Database"""
    
    def test_init_database(self, temp_db):
        assert temp_db is not None
    
    def test_add_rate(self, temp_db, sample_rate_data):
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        assert rate_id > 0
        
        rate = temp_db.get_rate_by_id(rate_id)
        assert rate is not None
        assert rate['rate_type'] == sample_rate_data['rate_type']
        assert rate['senior_currency'] == sample_rate_data['senior_currency']
        assert float(rate['buy_rate']) == sample_rate_data['buy_rate']
    
    def test_get_rate_by_id(self, temp_db, sample_rate_data):
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        rate = temp_db.get_rate_by_id(rate_id)
        
        assert rate is not None
        assert rate['id'] == rate_id
        assert rate['senior_currency'] == sample_rate_data['senior_currency']
    
    def test_update_rate(self, temp_db, sample_rate_data):
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        
        updated_data = sample_rate_data.copy()
        updated_data['buy_rate'] = 460.00
        updated_data['sell_rate'] = 460.50
        
        temp_db.update_rate(rate_id, updated_data, "TestUser")
        
        rate = temp_db.get_rate_by_id(rate_id)
        assert float(rate['buy_rate']) == 460.00
        assert float(rate['sell_rate']) == 460.50
    
    def test_delete_rate(self, temp_db, sample_rate_data):
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        
        temp_db.delete_rate(rate_id, "TestUser")
        
        rate = temp_db.get_rate_by_id(rate_id)
        assert rate is None
    
    def test_sanction_rate(self, temp_db, sample_rate_data):
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        
        temp_db.sanction_rate(rate_id, "TestUser")
        
        rate = temp_db.get_rate_by_id(rate_id)
        assert rate['status'] == 'санкционировано'
    
    def test_get_rates_with_filters(self, temp_db, sample_rate_data):
        """Тест получения курсов с фильтрами"""

        temp_db.add_rate(sample_rate_data, "TestUser")
        
        eur_data = sample_rate_data.copy()
        eur_data['senior_currency'] = 'EUR'
        temp_db.add_rate(eur_data, "TestUser")
        
        rates = temp_db.get_rates({'senior_currency': 'USD'})
        assert len(rates) >= 1
        assert all(r['senior_currency'] == 'USD' for r in rates)
        
        rates = temp_db.get_rates({'status': 'не санкционировано'})
        assert len(rates) >= 2
    
    def test_add_nb_rate(self, temp_db):
        """Тест добавления курса Нацбанка"""
        temp_db.add_nb_rate('USD', 'Доллар США', 450.50, '2025-12-19')
        
        rates = temp_db.get_nb_rates('2025-12-19')
        assert len(rates) >= 1
        assert any(r['currency_code'] == 'USD' for r in rates)
    
    def test_get_nb_rates(self, temp_db):
        """Тест получения курсов Нацбанка"""
        temp_db.add_nb_rate('USD', 'Доллар США', 450.50, '2025-12-19')
        temp_db.add_nb_rate('EUR', 'Евро', 490.00, '2025-12-19')
        
        rates = temp_db.get_nb_rates('2025-12-19')
        assert len(rates) == 2
        
        all_rates = temp_db.get_nb_rates()
        assert len(all_rates) >= 2
    
    def test_rate_history(self, temp_db, sample_rate_data):
        """Тест истории изменений"""
        rate_id = temp_db.add_rate(sample_rate_data, "TestUser")
        
        history = temp_db.get_rate_history(rate_id)
        assert len(history) >= 1
        assert history[0]['action'] == 'Добавление нового курса валюты'
        
        updated_data = sample_rate_data.copy()
        updated_data['buy_rate'] = 460.00
        temp_db.update_rate(rate_id, updated_data, "TestUser")
        
        history = temp_db.get_rate_history(rate_id)
        assert len(history) >= 2


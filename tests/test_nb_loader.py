import pytest
from unittest.mock import Mock, patch, MagicMock
from controller.nb_loader import NBLoader


class TestNBLoader:
    """Тесты для класса NBLoader"""
    
    def test_init(self, temp_db):
        """Тест инициализации NBLoader"""
        loader = NBLoader(temp_db)
        assert loader.db == temp_db
        assert loader.url is not None
    
    def test_extract_currency_code(self, temp_db):
        """Тест извлечения кода валюты"""
        loader = NBLoader(temp_db)
        
        assert loader._extract_currency_code("USD/Доллар США") == "USD"
        assert loader._extract_currency_code("EUR") == "EUR"
        assert loader._extract_currency_code("  RUB  ") == "RUB"
    
    def test_extract_currency_name(self, temp_db):
        """Тест извлечения названия валюты"""
        loader = NBLoader(temp_db)
        
        name = loader._extract_currency_name("USD/Доллар США")
        assert "Доллар" in name or "USD" in name
        
        name = loader._extract_currency_name("EUR - Евро")
        assert "Евро" in name or "EUR" in name
    
    def test_extract_rate(self, temp_db):
        """Тест извлечения курса"""
        loader = NBLoader(temp_db)
        
        assert loader._extract_rate("Курс: 450.50") == 450.50
        assert loader._extract_rate("450.50") == 450.50
        assert loader._extract_rate("Цена 450") == 450.0
        assert loader._extract_rate("Нет курса") == 0.0
    
    @patch('controller.nb_loader.requests.get')
    def test_load_rates_success(self, mock_get, temp_db):
        """Тест успешной загрузки курсов"""
        loader = NBLoader(temp_db)
        
        mock_response = Mock()
        mock_response.content = b"""<?xml version="1.0"?>
        <rss>
            <channel>
                <date>2025-12-19</date>
                <item>
                    <title>USD/Доллар США</title>
                    <description>Курс: 450.50</description>
                </item>
                <item>
                    <title>EUR/Евро</title>
                    <description>Курс: 490.00</description>
                </item>
            </channel>
        </rss>"""
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = loader.load_rates()
        
        assert result['success'] == True
        assert result['loaded'] >= 2
        assert 'date' in result
    
    @patch('controller.nb_loader.requests.get')
    def test_load_rates_error(self, mock_get, temp_db):
        """Тест обработки ошибки загрузки"""
        loader = NBLoader(temp_db)
        
        mock_get.side_effect = Exception("Connection error")
        
        result = loader.load_rates()
        
        assert result['success'] == False
        assert 'error' in result
        assert result['loaded'] == 0
    
    def test_get_priority_rates(self, temp_db):
        """Тест получения приоритетных курсов"""
        loader = NBLoader(temp_db)
        
        temp_db.add_nb_rate('USD', 'Доллар США', 450.50, '2025-12-19')
        temp_db.add_nb_rate('EUR', 'Евро', 490.00, '2025-12-19')
        temp_db.add_nb_rate('RUB', 'Рубль', 5.00, '2025-12-19')
        
        priority_rates = loader.get_priority_rates('2025-12-19')
        
        assert len(priority_rates) >= 3
        assert any(r['senior_currency'] == 'USD' for r in priority_rates)
        assert any(r['senior_currency'] == 'EUR' for r in priority_rates)
        assert any(r['senior_currency'] == 'RUB' for r in priority_rates)


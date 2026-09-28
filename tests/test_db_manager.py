# tests/test_db_manager.py
import pytest
from src.database.db_manager import DBManager
from src.models.country import Country
from src.models.aircraft import Aircraft

@pytest.fixture
def db_manager():
    # Используй тестовую БД или тот же конфиг, но с другой схемой/таблицей
    config = {
        "host": "localhost",
        "port": 5433,
        "dbname": "aviation_tracker",
        "user": "postgres",
        "password": "your_password"
    }
    yield DBManager(config)

def test_save_and_get_country(db_manager):
    country = Country("TestLand", "TL", 0.0, 10.0, -10.0, 0.0)
    db_manager.save_country(country)
    stats = db_manager.get_countries_and_aeroplanes_count()
    assert any(s["country_name"] == "TestLand" for s in stats)

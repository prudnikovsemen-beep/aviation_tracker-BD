"""Тесты для DBManager: проверка CRUD-операций с базой данных."""

import pytest
from src.database.db_manager import DBManager
from src.models.country import Country

# --- ВРЕМЕННОЕ РЕШЕНИЕ: жёстко прописываем конфиг, чтобы обойти UnicodeDecodeError ---
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "aviation_tracker",
    "user": "postgres",
    "password": "******"  # <-- ВСТАВЬ СЮДА СВОЙ ПАРОЛЬ ОТ БД
}


# ------------------------------------------------------------------------------------

def test_save_and_get_country():
    """Проверяем, что страна сохраняется и корректно читается обратно."""
    db_manager = DBManager(DB_CONFIG)

    # Создаём тестовую страну
    country = Country(
        name="TestLand",
        code="TL",
        lamin=0.0,
        lamax=10.0,
        lomin=0.0,
        lomax=10.0
    )

    # Сохраняем
    db_manager.save_country(country)

    # Получаем по имени
    saved = db_manager.get_country_by_name("TestLand")

    assert saved is not None, "Страна не была найдена после сохранения"
    assert saved.name == "TestLand"
    assert saved.code == "TL"

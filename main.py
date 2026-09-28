"""Точка входа проекта: инициализация и запуск сбора данных."""

from src.utils.config import load_config
from src.database.db_init import DBInitializer
from src.services.data_service import DataService

def main():
    # 1. Загрузка конфигурации
    db_config = load_config("config.ini")
    print("✅ Конфигурация загружена.")

    # 2. Инициализация БД (создание таблиц)
    initializer = DBInitializer(db_config)
    initializer.create_tables()

    # 3. Запуск сервиса сбора данных
    service = DataService(db_config)
    service.run()
    print("🎉 Сбор данных завершён!")

if __name__ == "__main__":
    main()

"""Точка входа проекта: инициализация и запуск сбора данных."""

import argparse  # Добавь эту строку сверху
from src.utils.config import load_config
from src.database.db_init import DBInitializer
from src.services.data_service import DataService

def main():
    parser = argparse.ArgumentParser(description="Aviation Tracker")
    parser.add_argument("--debug", action="store_true", help="Быстрый режим: только 3 страны для проверки")
    args = parser.parse_args()

    db_config = load_config("config.ini")
    print("✅ Конфигурация загружена.")

    initializer = DBInitializer(db_config)
    initializer.create_tables()

    service = DataService(db_config, debug_mode=args.debug)
    service.run()

    print("Сбор данных завершён!")

if __name__ == "__main__":
    main()

"""Скрипт для инициализации схемы БД (запуск один раз)."""

import configparser
from pathlib import Path
from src.database.db_init import init_database

def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Файл конфигурации не найден: {config_path}. "
            "Скопируйте config.ini.example в config.ini и заполните настройки."
        )
    config = configparser.ConfigParser()
    config.read(path, encoding="utf-8")
    return config

if __name__ == "__main__":
    # Загружаем конфиг
    cfg = load_config("config.ini")
    db_cfg = cfg["database"]

    conn_params = {
        "host": db_cfg["host"],
        "port": int(db_cfg["port"]),
        "dbname": db_cfg["dbname"],
        "user": db_cfg["user"],
        "password": db_cfg["password"],
    }

    print("Инициализация схемы БД...")
    init_database(conn_params)
    print("✅ Таблицы countries и aircrafts созданы (или уже существовали).")

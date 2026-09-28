"""Утилита для загрузки конфигурации из config.ini."""

import configparser
from pathlib import Path
from typing import Dict


def load_config(config_path: str = "config.ini") -> Dict[str, str]:
    """Загружает параметры подключения к БД из config.ini.

    Args:
        config_path: Путь к файлу конфигурации.

    Returns:
        Словарь с параметрами: host, port, dbname, user, password.

    Raises:
        FileNotFoundError: Если файл конфигурации не найден.
        KeyError: Если секция [database] отсутствует.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    config = configparser.ConfigParser()
    config.read(config_file, encoding="utf-8")

    if "database" not in config:
        raise KeyError("Секция [database] не найдена в config.ini")

    db = config["database"]
    return {
        "host": db.get("host", "localhost"),
        "port": db.get("port", "5432"),
        "dbname": db.get("dbname", "aviation_tracker"),
        "user": db.get("user", "postgres"),
        "password": db.get("password", ""),
    }

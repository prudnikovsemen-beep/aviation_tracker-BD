"""Быстрая проверка работы DBManager."""

from src.database.db_manager import DBManager
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read("config.ini", encoding="utf-8")
db_cfg = cfg['database']

db = DBManager({
    "host": db_cfg['host'],
    "port": int(db_cfg['port']),
    "dbname": db_cfg['dbname'],
    "user": db_cfg['user'],
    "password": db_cfg['password']
})

print("=== Страны и количество самолётов ===")
for row in db.get_countries_and_aeroplanes_count():
    print(f"  {row}")

print("\n=== Средняя скорость ===")
print(f"  {db.get_avg_speed()}")

print("\n=== Самолёты быстрее 850 ===")
for row in db.get_aeroplanes_with_higher_speed(850):
    print(f"  {row}")

print("\n=== Поиск по 'AFL' ===")
for row in db.get_aeroplanes_with_keyword("AFL"):
    print(f"  {row}")

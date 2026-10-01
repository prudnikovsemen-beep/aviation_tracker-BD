"""Сервисный слой: связывает API и базу данных."""

from typing import List, Dict, Any
import time

from src.api.nominatim_api import NominatimAPI
from src.api.opensky_api import OpenSkyAPI
from src.database.db_manager import DBManager
from src.models.country import Country
from src.models.aircraft import Aircraft


class DataService:
    """Оркестрирует получение данных из API и запись в БД."""

    # Полный список для продакшн-запуска
    ALL_COUNTRIES = [
        ("Russia", "RU"),
        ("Belarus", "BY"),
        ("Kazakhstan", "KZ"),
        ("China", "CN"),
        ("Turkey", "TR"),
    ]

    # Короткий список для быстрой проверки (2–3 страны)
    DEBUG_COUNTRIES = [
        ("Russia", "RU"),
        ("China", "CN"),
        ("Turkey", "TR"),
    ]

    def __init__(self, db_config: Dict[str, Any], debug_mode: bool = False):
        """
        Инициализирует сервис: создаёт API-клиенты и подключение к БД.

        Args:
            db_config (Dict[str, Any]): Конфигурация подключения к PostgreSQL.
            debug_mode (bool): Если True — используется короткий список стран.
        """
        self.nominatim = NominatimAPI()
        self.opensky = OpenSkyAPI()
        self.db = DBManager(db_config)
        self.countries_list = self.DEBUG_COUNTRIES if debug_mode else self.ALL_COUNTRIES
        self.debug_mode = debug_mode

    def fetch_and_save_countries(self) -> List[Country]:
        """
        Получает координаты стран через Nominatim API и сохраняет их в БД.

        Returns:
            List[Country]: Список успешно сохранённых стран.
        """
        countries = []
        mode_msg = " DEBUG-режим (только 3 страны)" if self.debug_mode else " Полный режим (5 стран)"
        print(f" Начинаем сбор координат. Режим: {mode_msg}")

        for name, code in self.countries_list:
            country = self.nominatim.get_country_bounding_box(name, code)
            if country:
                countries.append(country)
                self.db.save_country(country)

        print(f"✅ Сохранено стран: {len(countries)}")
        return countries

    def fetch_and_save_aircrafts(self, countries: List[Country]) -> List[Aircraft]:
        """
        Получает данные о самолётах из OpenSky для каждой страны (по bounding box),
        приписывает каждому самолёту код страны (current_country_code) и сохраняет в БД.

        Связь «самолёт ↔ страна» устанавливается на этапе загрузки: каждому борту
        присваивается код страны, в границах которой он был получен. Это позволяет
        корректно считать самолёты в воздушном пространстве, а не по регистрации.

        Args:
            countries (List[Country]): Список стран с координатами границ.

        Returns:
            List[Aircraft]: Список всех сохранённых воздушных судов.
        """
        all_aircrafts = []

        # Очищаем таблицу перед загрузкой
        conn = self.db.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE aircrafts RESTART IDENTITY;")
            conn.commit()
        finally:
            conn.close()
        print("🧹 Таблица aircrafts очищена, счётчик ID сброшен.")

        for i, country in enumerate(countries, start=1):
            print(f"[{i}/{len(countries)}] Запрос для {country.name}...", end=" ", flush=True)

            aircrafts = self.opensky.get_aircrafts_in_bbox(
                country.lamin, country.lomin, country.lamax, country.lomax
            )

            print(f"найдено {len(aircrafts)} судов")

            for ac in aircrafts:
                # Приписываем самолёт к стране, в bounding box которой он найден
                ac.current_country_code = country.code
                self.db.save_aircraft(ac)
                all_aircrafts.append(ac)

            time.sleep(1)  # Защита от rate limit

        print(f"✅ Всего сохранено судов: {len(all_aircrafts)}")
        return all_aircrafts

    def run(self) -> None:
        """
        Полный цикл: загрузка стран → загрузка самолётов → сохранение в БД.
        Если координаты стран не получены — сбор самолётов отменяется.
        """
        countries = self.fetch_and_save_countries()
        if countries:
            self.fetch_and_save_aircrafts(countries)
        else:
            print("⚠️ Не удалось получить координаты стран, сбор самолётов отменён.")

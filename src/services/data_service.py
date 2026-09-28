"""Сервисный слой: связывает API и базу данных."""

from typing import List
from src.api.nominatim_api import NominatimAPI
from src.api.opensky_api import OpenSkyAPI
from src.database.db_manager import DBManager
from src.models.country import Country
from src.models.aircraft import Aircraft


class DataService:
    """Оркестрирует получение данных из API и запись в БД."""

    COUNTRIES = [
        ("Russia", "RU"),
        ("Belarus", "BY"),
        ("Kazakhstan", "KZ"),
        ("China", "CN"),
        ("Germany", "DE"),
        ("France", "FR"),
        ("United States", "US"),
        ("Japan", "JP"),
        ("Turkey", "TR"),
        ("India", "IN"),
    ]

    def __init__(self, db_config: dict):
        self.nominatim = NominatimAPI()
        self.opensky = OpenSkyAPI()
        self.db = DBManager(db_config)

    def fetch_and_save_countries(self) -> List[Country]:
        countries = []
        for name, code in self.COUNTRIES:
            country = self.nominatim.get_country_bounding_box(name, code)
            if country:
                countries.append(country)
                self.db.save_country(country)
        print(f"✅ Сохранено стран: {len(countries)}")
        return countries

    def fetch_and_save_aircrafts(self, countries: List[Country]) -> List[Aircraft]:
        all_aircrafts = []
        for country in countries:
            aircrafts = self.opensky.get_aircrafts_in_bbox(
                country.lamin, country.lomin, country.lamax, country.lomax
            )
            for ac in aircrafts:
                self.db.save_aircraft(ac)
                all_aircrafts.append(ac)
            print(f"🌍 {country.name}: найдено {len(aircrafts)} судов")
        print(f"✅ Всего сохранено судов: {len(all_aircrafts)}")
        return all_aircrafts

    def run(self):
        countries = self.fetch_and_save_countries()
        if countries:
            self.fetch_and_save_aircrafts(countries)
        else:
            print("⚠️ Не удалось получить координаты стран, сбор самолётов отменён.")

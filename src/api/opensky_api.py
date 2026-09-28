"""Модуль для получения данных о самолётах через OpenSky API."""

import requests
from typing import List
from src.models.aircraft import Aircraft


class OpenSkyAPI:
    """Клиент для работы с OpenSky Network REST API."""

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, username: str | None = None, password: str | None = None):
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)

    def get_aircrafts_in_bbox(
        self, lamin: float, lomin: float, lamax: float, lomax: float
    ) -> List[Aircraft]:
        params = {"lamin": lamin, "lomin": lomin, "lamax": lamax, "lomax": lomax}

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data or not data.get("states"):
                return []

            return [self._parse_state(state) for state in data["states"]]
        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка при получении данных OpenSky: {e}")
            return []

    @staticmethod
    def _parse_state(state: list) -> Aircraft:
        return Aircraft(
            icao24=state[0] or "",
            callsign=state[1].strip() if state[1] else None,
            origin_country=state[2] or "",
            latitude=state[6],
            longitude=state[5],
            velocity=state[9],
            baro_altitude=state[7],
            on_ground=bool(state[8]),
            true_track=state[10],
            vertical_rate=state[11],
        )

"""Модуль для получения данных о самолётах через OpenSky API."""

import requests
from typing import Any, List

from src.models.aircraft import Aircraft


class OpenSkyAPI:
    """Клиент для работы с OpenSky Network REST API."""

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, username: str | None = None, password: str | None = None):
        """
        Инициализирует HTTP-сессию. При наличии учётных данных OpenSky
        используется базовая авторизация (повышает лимит запросов).

        Args:
            username (str | None): Имя пользователя OpenSky (опционально).
            password (str | None): Пароль OpenSky (опционально).
        """
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)

    def get_aircrafts_in_bbox(self, lamin: float, lomin: float, lamax: float, lomax: float) -> List[Aircraft]:
        """
        Получает список воздушных судов в заданном bounding box через OpenSky API.

        Args:
            lamin (float): Минимальная широта.
            lomin (float): Минимальная долгота.
            lamax (float): Максимальная широта.
            lomax (float): Максимальная долгота.

        Returns:
            List[Aircraft]: Список объектов Aircraft. Пустой список, если
                            данных нет или произошла ошибка запроса.
        """
        params = {"lamin": lamin, "lomin": lomin, "lamax": lamax, "lomax": lomax}

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if not data or not data.get("states"):
                return []

            return [self._parse_state(state) for state in data["states"]]
        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка при получении данных OpenSky: {e}")
            return []

    @staticmethod
    def _parse_state(state: list[Any]) -> Aircraft:
        """
        Преобразует сырой массив состояний из OpenSky API в объект Aircraft.

        Индексы массива states (по документации OpenSky):
            0 — icao24, 1 — callsign, 2 — origin_country,
            5 — longitude, 6 — latitude, 7 — baro_altitude,
            8 — on_ground, 9 — velocity, 10 — true_track, 11 — vertical_rate.

        Args:
            state (list[Any]): Сырой массив данных одного судна из OpenSky.

        Returns:
            Aircraft: Объект воздушного судна с заполненными полями.
        """
        callsign_raw = state[1]

        return Aircraft(
            icao24=state[0] or "",
            callsign=callsign_raw,
            origin_country=state[2] or "",
            latitude=state[6],
            longitude=state[5],
            velocity=state[9],
            baro_altitude=state[7],
            on_ground=bool(state[8]),
            true_track=state[10],
            vertical_rate=state[11],
        )

"""Модуль клиента для работы с OpenSky Network API."""

import requests
from datetime import datetime
from typing import List, Optional, Tuple
from src.models.aircraft import Aircraft


class OpenSkyAPI:
    """
    Клиент для получения данных о воздушных судах через OpenSky Network.

    Использует публичный API. Для получения данных требуется указать
    географические границы (bounding box): lamin, lamax, lomin, lomax.
    """

    BASE_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Инициализация клиента OpenSky.

        Публичный API не требует авторизации, но если у тебя есть учётка,
        можно передать логин/пароль для увеличенных лимитов.

        Args:
            username (Optional[str]): Логин для OpenSky (если есть).
            password (Optional[str]): Пароль для OpenSky (если есть).
        """
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)

    def get_aircrafts_in_area(
        self, lamin: float, lamax: float, lomin: float, lomax: float
    ) -> List[Aircraft]:
        """
        Получает список воздушных судов в заданной географической области.

        OpenSky API возвращает массив states, где каждый элемент — список значений.
        Индексы:
          0: icao24, 1: callsign, 2: origin_country, 5: longitude, 6: latitude,
          7: baro_altitude, 8: on_ground, 9: velocity, 10: true_track,
          11: vertical_rate, 12: last_seen (timestamp)

        Args:
            lamin (float): Минимальная широта (юг).
            lamax (float): Максимальная широта (север).
            lomin (float): Минимальная долгота (запад).
            lomax (float): Максимальная долгота (восток).

        Returns:
            List[Aircraft]: Список объектов Aircraft.
        """
        params = {
            "lamin": lamin,
            "lamax": lamax,
            "lomin": lomin,
            "lomax": lomax,
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            return []

        states = data.get("states", [])
        aircrafts: List[Aircraft] = []

        for state in states:
            if not isinstance(state, list) or len(state) < 7:
                continue

            # Безопасное получение значений с дефолтными None
            icao24 = state[0] if len(state) > 0 else None
            callsign = state[1] if len(state) > 1 else None
            origin_country = state[2] if len(state) > 2 else None
            longitude = state[5] if len(state) > 5 else None
            latitude = state[6] if len(state) > 6 else None
            baro_altitude = state[7] if len(state) > 7 else None
            on_ground = bool(state[8]) if len(state) > 8 else False
            velocity = state[9] if len(state) > 9 else None
            true_track = state[10] if len(state) > 10 else None
            vertical_rate = state[11] if len(state) > 11 else None
            last_seen_ts = state[12] if len(state) > 12 else None

            last_seen = None
            if last_seen_ts is not None:
                try:
                    last_seen = datetime.fromtimestamp(last_seen_ts)
                except (ValueError, OSError):
                    last_seen = None

            aircraft = Aircraft(
                icao24=icao24 or "",
                callsign=callsign or "",
                origin_country=origin_country,
                longitude=longitude or 0.0,
                latitude=latitude or 0.0,
                baro_altitude=baro_altitude,
                on_ground=on_ground,
                velocity=velocity,
                true_track=true_track,
                vertical_rate=vertical_rate,
                last_seen=last_seen,
            )
            aircrafts.append(aircraft)

        return aircrafts

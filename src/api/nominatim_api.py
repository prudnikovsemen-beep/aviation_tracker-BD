"""Модуль клиента для работы с Nominatim API (OpenStreetMap)."""

import requests
from typing import List, Optional
from src.models.country import Country


class NominatimAPI:
    """
    Клиент для получения географических координат стран через Nominatim.

    Основная задача — получить bounding box (границы) страны, чтобы затем
    запрашивать самолёты в этом регионе через OpenSky API.
    """

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, user_agent: str):
        """
        Инициализация клиента.

        Args:
            user_agent (str): Значение заголовка User-Agent, обязательное для Nominatim.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get_country_bounding_box(self, country_name: str) -> Optional[Country]:
        """
        Получает границы (bounding box) для указанной страны.

        Nominatim возвращает bounding box в формате [юг, север, запад, восток].
        Мы преобразуем это в (lamin, lamax, lomin, lomax) для OpenSky.

        Args:
            country_name (str): Название страны (например, 'Russia', 'Kazakhstan').

        Returns:
            Optional[Country]: Объект Country с заполненными границами или None, если не найдено.
        """
        params = {
            "q": country_name,
            "format": "json",
            "limit": 1,
            "countrycodes": "",  # можно оставить пустым, чтобы искать по названию
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            place = data[0]
            # Nominatim boundingbox: [south, north, west, east]
            bounding_box = place.get("boundingbox")
            if not bounding_box or len(bounding_box) != 4:
                return None

            lamin, lamax, lomin, lomax = map(float, bounding_box)

            return Country(
                name=place.get("display_name", country_name),
                code=place.get("country_code"),
                lamin=lamin,
                lamax=lamax,
                lomin=lomin,
                lomax=lomax,
            )
        except (requests.RequestException, ValueError, IndexError, KeyError) as e:
            # Для курсовой лучше логировать ошибку, но пока просто возвращаем None
            return None

"""Модуль для получения географических координат стран через Nominatim API."""

import requests
from typing import Dict, Any

from src.models.country import Country


class NominatimAPI:
    """Клиент для работы с Nominatim OpenStreetMap API."""

    BASE_URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self, user_agent: str = "aviation_tracker/1.0"):
        """
        Инициализирует HTTP-сессию с заданным User-Agent.

        Args:
            user_agent (str): Идентификатор приложения для Nominatim API.
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get_country_bounding_box(self, country_name: str, country_code: str) -> Country | None:
        """
        Получает bounding box страны (мин/макс широту и долготу) через Nominatim API.

        Args:
            country_name (str): Название страны на английском (например, "Russia").
            country_code (str): Двухбуквенный код страны (например, "RU").

        Returns:
            Country | None: Объект Country с координатами границ, или None,
                            если данные не найдены или произошла ошибка.
        """
        params: Dict[str, Any] = {
            "q": country_name,
            "format": "json",
            "limit": 1,
            "countrycodes": country_code.lower(),
        }

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            item = data[0]
            bbox = item.get("boundingbox")
            if not bbox or len(bbox) < 4:
                return None

            return Country(
                name=country_name,
                code=country_code.upper(),
                lamin=float(bbox[0]),
                lamax=float(bbox[1]),
                lomin=float(bbox[2]),
                lomax=float(bbox[3]),
            )
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"Ошибка при получении координат для {country_name}: {e}")
            return None

"""Модуль с моделью Country для авиатрекера."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Country:
    """
    Модель страны для хранения географических и служебных данных.

    Используется для сохранения границ воздушного пространства (bounding box)
    и последующего запроса самолётов через OpenSky API.

    Attributes:
        name (str): Официальное название страны.
        code (Optional[str]): ISO-код страны (например, 'RU', 'KZ').
        lamin (float): Минимальная широта (южная граница).
        lamax (float): Максимальная широта (северная граница).
        lomin (float): Минимальная долгота (западная граница).
        lomax (float): Максимальная долгота (восточная граница).
    """

    name: str
    code: Optional[str] = None
    lamin: float = 0.0
    lamax: float = 0.0
    lomin: float = 0.0
    lomax: float = 0.0

    def get_bounding_box(self) -> tuple[float, float, float, float]:
        """
        Возвращает границы воздушного пространства страны в формате,
        подходящем для запроса к OpenSky API.

        Returns:
            tuple[float, float, float, float]: (lamin, lamax, lomin, lomax).
        """
        return self.lamin, self.lamax, self.lomin, self.lomax

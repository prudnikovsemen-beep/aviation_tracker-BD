"""Модуль с моделью Aircraft для авиатрекера."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Aircraft:
    """
    Модель воздушного судна на основе данных из OpenSky API states.

    Хранит ключевые параметры полёта: координаты, скорость, высоту,
    позывной и статус нахождения на земле.

    Attributes:
        icao24 (str): Уникальный идентификатор самолёта (ICAO 24-bit).
        callsign (str): Позывной воздушного судна.
        origin_country (Optional[str]): Страна регистрации/происхождения.
        longitude (float): Текущая долгота.
        latitude (float): Текущая широта.
        baro_altitude (Optional[float]): Барометрическая высота (м).
        on_ground (bool): Флаг, находится ли самолёт на земле.
        velocity (Optional[float]): Скорость (м/с).
        true_track (Optional[float]): Истинный курс (градусы).
        vertical_rate (Optional[float]): Вертикальная скорость (м/с).
        last_seen (Optional[datetime]): Время последнего обновления данных.
    """

    icao24: str
    callsign: str
    origin_country: Optional[str] = None
    longitude: float = 0.0
    latitude: float = 0.0
    baro_altitude: Optional[float] = None
    on_ground: bool = False
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    last_seen: Optional[datetime] = None

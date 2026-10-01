"""Модуль с моделью Aircraft для авиатрекера."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Aircraft:
    """
    Модель воздушного судна на основе данных из OpenSky API states.
    Поле current_country_code хранит код страны, в воздушном пространстве которой
    находится борт (определяется по bounding box координат).
    """

    icao24: str
    callsign: Optional[str] = None
    origin_country: Optional[str] = None
    current_country_code: Optional[str] = None  # <-- добавили: страна по координатам
    longitude: float = 0.0
    latitude: float = 0.0
    baro_altitude: Optional[float] = None
    on_ground: bool = False
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    last_seen: Optional[datetime] = None

    def __post_init__(self) -> None:
        """
        Гарантирует, что callsign всегда будет строкой (даже если передали None).
        Это убирает необходимость проверять callsign на None в остальной части кода.
        """
        if self.callsign is None:
            self.callsign = ""
        else:
            # На случай, если передали строку с пробелами — убираем лишние
            self.callsign = self.callsign.strip()

# tests/test_data_service_unit.py
from unittest.mock import patch, MagicMock
from src.services.data_service import DataService
from src.models.country import Country
from src.models.aircraft import Aircraft

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "test",
    "user": "postgres",
    "password": "ваш_пароль",
}


@patch("src.services.data_service.time.sleep")
@patch("src.services.data_service.DBManager")
@patch("src.services.data_service.OpenSkyAPI")
@patch("src.services.data_service.NominatimAPI")
def test_fetch_and_save_countries(mock_nominatim_cls, mock_opensky_cls, mock_db_cls, mock_sleep):
    # Настраиваем моки
    mock_nominatim = MagicMock()
    mock_nominatim.get_country_bounding_box.return_value = Country(
        name="Russia", code="RU", lamin=40.0, lamax=70.0, lomin=30.0, lomax=180.0
    )
    mock_nominatim_cls.return_value = mock_nominatim

    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    service = DataService(DB_CONFIG, debug_mode=True)

    # В debug-режиме список из 3 стран
    countries = service.fetch_and_save_countries()

    assert len(countries) == 3
    assert all(c.name in ("Russia", "China", "Turkey") for c in countries)
    # save_country должен вызываться для каждой найденной страны
    assert mock_db.save_country.call_count == 3


@patch("src.services.data_service.time.sleep")
@patch("src.services.data_service.DBManager")
@patch("src.services.data_service.OpenSkyAPI")
@patch("src.services.data_service.NominatimAPI")
def test_fetch_and_save_countries_skips_none(mock_nominatim_cls, mock_opensky_cls, mock_db_cls, mock_sleep):
    # Если Nominatim не нашёл страну — она не сохраняется
    mock_nominatim = MagicMock()
    mock_nominatim.get_country_bounding_box.return_value = None
    mock_nominatim_cls.return_value = mock_nominatim

    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    service = DataService(DB_CONFIG, debug_mode=True)
    countries = service.fetch_and_save_countries()

    assert len(countries) == 0
    mock_db.save_country.assert_not_called()


@patch("src.services.data_service.time.sleep")
@patch("src.services.data_service.DBManager")
@patch("src.services.data_service.OpenSkyAPI")
@patch("src.services.data_service.NominatimAPI")
def test_fetch_and_save_aircrafts(mock_nominatim_cls, mock_opensky_cls, mock_db_cls, mock_sleep):
    # Мокаем Nominatim
    mock_nominatim = MagicMock()
    mock_nominatim_cls.return_value = mock_nominatim

    # Мокаем OpenSky — возвращаем 2 самолёта
    mock_opensky = MagicMock()
    mock_opensky.get_aircrafts_in_bbox.return_value = [
        Aircraft(icao24="abc123", callsign="FLT1"),
        Aircraft(icao24="def456", callsign="FLT2"),
    ]
    mock_opensky_cls.return_value = mock_opensky

    # Мокаем DBManager
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value = mock_cur
    mock_db.get_connection.return_value = mock_conn
    mock_db_cls.return_value = mock_db

    service = DataService(DB_CONFIG, debug_mode=True)

    # Даём 2 страны
    countries = [
        Country(name="Russia", code="RU", lamin=40.0, lamax=70.0, lomin=30.0, lomax=180.0),
        Country(name="China", code="CN", lamin=18.0, lamax=54.0, lomin=73.0, lomax=135.0),
    ]

    aircrafts = service.fetch_and_save_aircrafts(countries)

    # 2 страны × 2 самолёта = 4
    assert len(aircrafts) == 4
    assert mock_db.save_aircraft.call_count == 4
    # TRUNCATE должен вызываться один раз
    mock_cur.execute.assert_called_once_with("TRUNCATE TABLE aircrafts RESTART IDENTITY;")
    # time.sleep должен вызываться для каждой страны
    assert mock_sleep.call_count == 2


@patch("src.services.data_service.time.sleep")
@patch("src.services.data_service.DBManager")
@patch("src.services.data_service.OpenSkyAPI")
@patch("src.services.data_service.NominatimAPI")
def test_run_full_flow(mock_nominatim_cls, mock_opensky_cls, mock_db_cls, mock_sleep):
    # Мокаем Nominatim — возвращаем реальную страну
    mock_nominatim = MagicMock()
    mock_nominatim.get_country_bounding_box.return_value = Country(
        name="Russia", code="RU", lamin=40.0, lamax=70.0, lomin=30.0, lomax=180.0
    )
    mock_nominatim_cls.return_value = mock_nominatim

    # Мокаем OpenSky — возвращаем 1 самолёт
    mock_opensky = MagicMock()
    mock_opensky.get_aircrafts_in_bbox.return_value = [
        Aircraft(icao24="abc123", callsign="FLT1"),
    ]
    mock_opensky_cls.return_value = mock_opensky

    # Мокаем DBManager
    mock_db = MagicMock()
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_cur.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value = mock_cur
    mock_db.get_connection.return_value = mock_conn
    mock_db_cls.return_value = mock_db

    service = DataService(DB_CONFIG, debug_mode=True)
    service.run()

    # Проверяем, что страны и самолёты сохранялись
    assert mock_db.save_country.call_count == 3  # 3 страны в debug-режиме
    assert mock_db.save_aircraft.call_count == 3  # 3 страны × 1 самолёт


@patch("src.services.data_service.time.sleep")
@patch("src.services.data_service.DBManager")
@patch("src.services.data_service.OpenSkyAPI")
@patch("src.services.data_service.NominatimAPI")
def test_run_no_countries(mock_nominatim_cls, mock_opensky_cls, mock_db_cls, mock_sleep):
    # Если Nominatim ничего не вернул — самолёты не запрашиваются
    mock_nominatim = MagicMock()
    mock_nominatim.get_country_bounding_box.return_value = None
    mock_nominatim_cls.return_value = mock_nominatim

    mock_opensky = MagicMock()
    mock_opensky_cls.return_value = mock_opensky

    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db

    service = DataService(DB_CONFIG, debug_mode=True)
    service.run()

    mock_opensky.get_aircrafts_in_bbox.assert_not_called()
    mock_db.save_aircraft.assert_not_called()

# tests/test_db_manager_unit.py
from unittest.mock import patch, MagicMock
from src.database.db_manager import DBManager
from src.models.country import Country
from src.models.aircraft import Aircraft

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "test",
    "user": "postgres",
    "password": "secret",
}


def _make_mock_connection():
    """Создаёт мок соединения, который работает как контекстный менеджер."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    # with conn as conn: -> conn.__enter__() возвращает сам conn
    mock_conn.__enter__.return_value = mock_conn
    # with conn.cursor() as cur: -> cursor().__enter__() возвращает сам курсор
    mock_cur.__enter__.return_value = mock_cur
    mock_conn.cursor.return_value = mock_cur
    return mock_conn, mock_cur


@patch("src.database.db_manager.psycopg2")
def test_get_connection(mock_psycopg):
    mock_conn = MagicMock()
    mock_psycopg.connect.return_value = mock_conn

    db = DBManager(DB_CONFIG)
    conn = db.get_connection()

    assert conn is mock_conn
    mock_psycopg.connect.assert_called_once_with(
        host="localhost", port=5432, dbname="test", user="postgres", password="secret"
    )


@patch("src.database.db_manager.psycopg2")
def test_save_country(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    db = DBManager(DB_CONFIG)
    country = Country(name="USA", code="US", lamin=35.0, lamax=45.0, lomin=-120.0, lomax=-110.0)
    db.save_country(country)

    mock_cur.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("src.database.db_manager.psycopg2")
def test_save_aircraft(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    db = DBManager(DB_CONFIG)
    aircraft = Aircraft(
        icao24="abcd1234", callsign="FLT101", origin_country="USA",
        latitude=37.0, longitude=-120.0, velocity=250.0, baro_altitude=1000.0,
        on_ground=False, true_track=90.0, vertical_rate=5.0,
    )
    db.save_aircraft(aircraft)

    mock_cur.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch("src.database.db_manager.psycopg2")
def test_get_countries_and_aeroplanes_count(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    # Имитируем ответ БД: две строки с двумя колонками
    mock_cur.description = [("country_name",), ("aircraft_count",)]
    mock_cur.fetchall.return_value = [("USA", 5), ("Canada", 3)]

    db = DBManager(DB_CONFIG)
    result = db.get_countries_and_aeroplanes_count()

    assert len(result) == 2
    assert result[0]["country_name"] == "USA"
    assert result[0]["aircraft_count"] == 5
    assert result[1]["country_name"] == "Canada"


@patch("src.database.db_manager.psycopg2")
def test_get_all_aeroplanes(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.description = [("icao24",), ("callsign",)]
    mock_cur.fetchall.return_value = [("abcd1234", "FLT101"), ("efgh5678", "FLT202")]

    db = DBManager(DB_CONFIG)
    result = db.get_all_aeroplanes()

    assert len(result) == 2
    assert result[0]["icao24"] == "abcd1234"
    assert result[1]["callsign"] == "FLT202"


@patch("src.database.db_manager.psycopg2")
def test_get_avg_speed(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.fetchone.return_value = (250.5,)

    db = DBManager(DB_CONFIG)
    result = db.get_avg_speed()

    assert result == 250.5


@patch("src.database.db_manager.psycopg2")
def test_get_avg_speed_none(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.fetchone.return_value = (None,)

    db = DBManager(DB_CONFIG)
    result = db.get_avg_speed()

    assert result is None


@patch("src.database.db_manager.psycopg2")
def test_get_aeroplanes_with_higher_speed(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    # Первый вызов — get_avg_speed, второй — основной запрос
    mock_cur.fetchone.return_value = (200.0,)
    mock_cur.description = [("icao24",), ("callsign",)]
    mock_cur.fetchall.return_value = [("abcd1234", "FLT101")]

    db = DBManager(DB_CONFIG)
    result = db.get_aeroplanes_with_higher_speed()

    assert len(result) == 1
    assert result[0]["callsign"] == "FLT101"


@patch("src.database.db_manager.psycopg2")
def test_get_aeroplanes_with_higher_speed_no_avg(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.fetchone.return_value = (None,)

    db = DBManager(DB_CONFIG)
    result = db.get_aeroplanes_with_higher_speed()

    assert result == []


@patch("src.database.db_manager.psycopg2")
def test_get_aeroplanes_with_keyword(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.description = [("icao24",), ("callsign",)]
    mock_cur.fetchall.return_value = [("abcd1234", "FLT101")]

    db = DBManager(DB_CONFIG)
    result = db.get_aeroplanes_with_keyword("FLT")

    assert len(result) == 1
    assert result[0]["callsign"] == "FLT101"


@patch("src.database.db_manager.psycopg2")
def test_get_country_by_name_found(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.fetchone.return_value = ("USA", "US", 35.0, 45.0, -120.0, -110.0)

    db = DBManager(DB_CONFIG)
    country = db.get_country_by_name("USA")

    assert country is not None
    assert country.name == "USA"
    assert country.code == "US"
    assert country.lamin == 35.0


@patch("src.database.db_manager.psycopg2")
def test_get_country_by_name_not_found(mock_psycopg):
    mock_conn, mock_cur = _make_mock_connection()
    mock_psycopg.connect.return_value = mock_conn

    mock_cur.fetchone.return_value = None

    db = DBManager(DB_CONFIG)
    country = db.get_country_by_name("UnknownCountry")

    assert country is None

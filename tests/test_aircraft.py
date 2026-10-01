from src.models.aircraft import Aircraft

def test_callsign_none_becomes_empty_string():
    """Проверяем, что None в callsign превращается в пустую строку."""
    aircraft = Aircraft(icao24="abcd1234", callsign=None)
    assert aircraft.callsign == ""

def test_callsign_strip_works():
    """Проверяем, что лишние пробелы убираются."""
    aircraft = Aircraft(icao24="abcd1234", callsign="  FLIGHT123  ")
    assert aircraft.callsign == "FLIGHT123"

def test_minimal_valid_aircraft():
    """Проверяем создание объекта с минимальным набором данных."""
    aircraft = Aircraft(icao24="abcd1234")
    assert aircraft.icao24 == "abcd1234"
    assert aircraft.callsign == ""

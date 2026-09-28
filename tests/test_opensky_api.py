# tests/test_opensky_api.py
from unittest.mock import patch, MagicMock
from src.api.opensky_api import OpenSkyAPI

@patch("src.api.opensky_api.requests.Session")
def test_get_aircrafts_in_bbox_success(mock_session_cls):
    # Подменяем ответ API на «фейковый»
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "states": [
            ["icao1", "FLT101", "USA", None, None, -120.0, 37.0, 1000.0, False, 250.0, 90.0, 5.0],
            ["icao2", None, "CAN", None, None, -75.0, 45.0, None, True, None, None, None],
        ]
    }
    mock_session = MagicMock()
    mock_session.get.return_value = mock_resp
    mock_session_cls.return_value = mock_session

    api = OpenSkyAPI()
    result = api.get_aircrafts_in_bbox(30.0, -130.0, 40.0, -110.0)

    assert len(result) == 2
    assert result[0].icao24 == "icao1"
    assert result[0].callsign == "FLT101"
    # Проверяем, что None превратился в пустую строку (благодаря __post_init__)
    assert result[1].callsign == ""

@patch("src.api.opensky_api.requests.Session")
def test_get_aircrafts_in_bbox_empty_response(mock_session_cls):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}  # API вернул пустоту
    mock_session = MagicMock()
    mock_session.get.return_value = mock_resp
    mock_session_cls.return_value = mock_session

    api = OpenSkyAPI()
    result = api.get_aircrafts_in_bbox(30.0, -130.0, 40.0, -110.0)

    assert result == []

# tests/test_nominatim_api.py
from unittest.mock import patch, MagicMock
from src.api.nominatim_api import NominatimAPI
from src.models.country import Country

@patch("src.api.nominatim_api.requests.Session")
def test_get_country_bounding_box_success(mock_session_cls):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [
        {
            "boundingbox": ["35.0", "45.0", "-120.0", "-110.0"],
        }
    ]
    mock_session = MagicMock()
    mock_session.get.return_value = mock_resp
    mock_session_cls.return_value = mock_session

    api = NominatimAPI()
    country = api.get_country_bounding_box("USA", "US")

    assert country is not None
    assert country.lamin == 35.0
    assert country.lomax == -110.0

@patch("src.api.nominatim_api.requests.Session")
def test_get_country_bounding_box_no_data(mock_session_cls):
    mock_resp = MagicMock()
    mock_resp.json.return_value = []  # API ничего не нашёл
    mock_session = MagicMock()
    mock_session.get.return_value = mock_resp
    mock_session_cls.return_value = mock_session

    api = NominatimAPI()
    country = api.get_country_bounding_box("UnknownCountry", "XX")

    assert country is None

import pytest
from . import app
from weather.weather import Weather


@pytest.fixture
def weather(app):
    """Fixture to create a Weather instance with active app context."""
    return Weather()


def test_getting_cities(weather):
    cities = weather.get_cities()
    assert len(cities) == 10

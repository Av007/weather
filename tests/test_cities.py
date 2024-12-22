from . import app
from weather.cities import Cities, City


def test_get_single_city(app):
    cities = Cities(['Paris'])
    assert cities.get_cities_coord() == [City('Paris', {
            'lat':  2.3200410217200766,
            'long': 48.8588897,
        })]

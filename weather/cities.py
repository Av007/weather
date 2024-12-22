from os import getenv
import logging
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor
from flask import current_app
from .gateway import APIGateway


class City:
    """
    City entity model class
    """
    def __init__(self, name, coordinates):
        self.long = coordinates['long']
        self.lat = coordinates['lat']
        self.name = name

    def __repr__(self):
        return f"<City(name={self.name}, lat={self.lat}, long={self.long})>"

    def to_dict(self):
        """Convert City instance to a serializable dictionary."""
        return {
            'name': self.name,
            'coordinates': {
                'long': self.long,
                'lat': self.lat
            }
        }

    def __eq__(self, other):
        if isinstance(other, City):
            return self.name == other.name and self.lat == other.lat and self.long == other.long
        return False

    @classmethod
    def from_dict(cls, data):
        """Create a City instance from a dictionary."""
        return cls(data['name'], data['coordinates'])


class Cities(APIGateway):
    """
    Country model class
    """
    def __init__(self, cities_list):
        if not cities_list:
            raise Exception('Specify at least 1 city name')
        self.cache = current_app.extensions['cache']
        self.cities_list = cities_list
        self.url = getenv('cities_endpoint')
        self.cities = [
            {"City": "New York",
             "Latitude": 40.7128,
             "Longitude": -74.0060},
            {"City": "Tokyo",
             "Latitude": 35.6895,
             "Longitude": 139.6917},
            {"City": "London",
             "Latitude": 51.5074,
             "Longitude": -0.1278},
            {"City": "Paris",
             "Latitude": 48.8566,
             "Longitude": 2.3522},
            {"City": "Berlin",
             "Latitude": 52.5200,
             "Longitude": 13.4050},
            {"City": "Sydney",
             "Latitude": -33.8688,
             "Longitude": 151.2093},
            {"City": "Mumbai",
             "Latitude": 19.0760,
             "Longitude": 72.8777},
            {"City": "Cape Town",
             "Latitude": -33.9249,
             "Longitude": 18.4241},
            {"City": "Moscow",
             "Latitude": 55.7558,
             "Longitude": 37.6173},
            {"City": "Rio de Janeiro",
             "Latitude": -22.9068,
             "Longitude": -43.1729}
        ]

    def get_all(self):
        cities = self.cache.get("cities")
        if not cities:
            logging.warning('cache not exists, please run cache:run')
            cities = [
                City(city['City'], {
                    'lat': city['Latitude'],
                    'long': city['Longitude']
                }) for city in self.cities
            ]
        return cities

    def get_cities_coord(self):
        semaphore = Semaphore(self.max_concurrent_requests)

        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            futures = [executor.submit(self.get_item, city, semaphore) for city in self.cities_list]

        data = []
        for future in futures:
            item = future.result()
            if item is not None:
                data.append(item)

        logging.info('writing cache data')
        self.cache['cities'] = data
        return data

    def get_item(self, city_name, semaphore):
        url = f"{getenv('cities_endpoint')}search?city={city_name}&format=geocodejson"
        data = self.fetch_data(url, semaphore)
        return self.transform(data, city_name)

    def transform(self, data, city_name):
        lat, long = data['features'][0]['geometry']['coordinates']
        return City(city_name, {
            'lat': lat,
            'long': long
        })

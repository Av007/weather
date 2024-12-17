from os import getenv, path
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor
from pandas import DataFrame, concat
from requests import get, exceptions


class Weather:
    """
    Weather model class
    """
    def __init__(self):
        self.url = getenv('url')
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

    def get_item(self, city, semaphore):
        """
        Fetching and transform data item
        :param city:
        :param semaphore:
        :return:
        """
        data = self.fetch_data(city, semaphore)
        return self.transform(data, city['City'])

    def fetch_data(self, city, semaphore):
        """
        Fetching data from public API
        :param city:
        :param semaphore:
        :return:
        """
        url = f"{self.url}?latitude={city['Latitude']}&longitude={city['Longitude']}" \
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"

        with semaphore:
            try:
                response = get(url)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response.json()
            except exceptions.RequestException as e:
                print(f"Error fetching data from {url}: {e}")
                return None

    def transform(self, data, city_name):
        """
        Transform data using panda data frame
        :param data:
        :param city_name:
        :return:
        """
        df = DataFrame(data['current'], index=[0])

        df.insert(0, 'City', city_name)
        df = df.drop('time', axis=1)
        df = df.drop('interval', axis=1)

        df['temperature_2m_f'] = (df['temperature_2m'] * 9 / 5) + 32
        # Convert Celsius to Fahrenheit
        df['temperature_2m_f'] = (df['temperature_2m'] * 9 / 5) + 32

        # Convert m/s to mph
        df['wind_speed_10m_mph'] = df['wind_speed_10m'] * 2.237

        return df.round(1)

    def scrape_data(self, filters):
        """
        Scraping data process
        :param filters:
        :return:
        """
        max_concurrent_requests = int(getenv('concurrent_requests')) or 5
        semaphore = Semaphore(max_concurrent_requests)

        with ThreadPoolExecutor(max_workers=max_concurrent_requests) as executor:
            futures = [executor.submit(self.get_item, city, semaphore) for city in self.cities]

        dataframes = []
        for future in futures:
            df = future.result()
            if df is not None:
                dataframes.append(df)

        if dataframes:
            final_df = concat(dataframes, ignore_index=True)

            if filters == 'max_temp':
                final_df = final_df.sort_values('temperature_2m', ascending = False)
            if filters == 'min_hum':
                final_df = final_df.sort_values(by='relative_humidity_2m')

            new_column_names = {
                'temperature_2m': 'Temperature\n(C)',
                'relative_humidity_2m': 'Humidity(%)',
                'wind_speed_10m': 'Wind Speed\n(m/s)',
                'temperature_2m_f': 'Temperature\n(F)',
                'wind_speed_10m_mph': 'Wind Speed\n(mph)',
                'city': 'City',
            }

            final_df = final_df.rename(columns=new_column_names)
            final_df = final_df.reset_index(drop=True)

            file = path.join('report', getenv('filename'))
            final_df.to_csv(file, index=False)

            return final_df.to_dict()

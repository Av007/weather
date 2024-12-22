import logging
from os import getenv
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor
from matplotlib import pyplot as plt
import matplotlib
from pandas import DataFrame, concat, read_csv
from .gateway import APIGateway
from .cities import Cities
from .helper import FileHelper


class Weather(APIGateway):
    """
    Weather model class
    """
    def __init__(self):
        self.helper = FileHelper()
        self.url = getenv('forecast_endpoint')
        self.cities = ['New York', 'Tokyo', 'London', 'Paris', 'Berlin', 'Sydney', 'Mumbai', 'Cape Town', 'Moscow', 'Rio de Janeiro']

    def get_item(self, city, semaphore):
        """
        Fetching and transform data item
        :param city: City
        :param semaphore: Semaphore
        :return: DataFrame
        """
        url = f"{self.url}?latitude={city.lat}&longitude={city.long}" \
              f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        data = self.fetch_data(url, semaphore)
        return self.transform(data, city.name)

    def transform(self, data, city_name):
        """
        Transform data using panda data frame
        :param data: dict
        :param city_name:
        :return: DataFrame
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
        :param filters: dict
        :return: dict
        """
        cities = Cities(self.cities)
        semaphore = Semaphore(self.max_concurrent_requests)

        with ThreadPoolExecutor(max_workers=self.max_concurrent_requests) as executor:
            futures = [executor.submit(self.get_item, city, semaphore) for city in cities.get_all()]

        dataframes = []
        for future in futures:
            df = future.result()
            if df is not None:
                dataframes.append(df)

        final_df = concat(dataframes, ignore_index=True)

        final_df = self.format(final_df, filters)

        self.helper.write_file(final_df)

        return final_df.to_dict()

    def format(self, dataframe, filters):
        if filters == 'max_temp':
            dataframe = dataframe.sort_values('temperature_2m', ascending=False)
        elif filters == 'min_hum':
            dataframe = dataframe.sort_values(by='relative_humidity_2m')

        new_column_names = {
            'temperature_2m': 'Temperature\n(C)',
            'relative_humidity_2m': 'Humidity(%)',
            'wind_speed_10m': 'Wind Speed\n(m/s)',
            'temperature_2m_f': 'Temperature\n(F)',
            'wind_speed_10m_mph': 'Wind Speed\n(mph)',
            'city': 'City',
        }

        dataframe = dataframe.rename(columns=new_column_names)
        dataframe = dataframe.reset_index(drop=True)

        return dataframe

    def get_image_graph(self):
        matplotlib.use('Agg')
        try:
            df = read_csv(self.helper.file_name())
        except FileNotFoundError as e:
            logging.error(f"Issue with file {e}")
            return None

        fig, ax = plt.subplots()
        ax.barh(df.iloc[:, 0], df.iloc[:, 4], color='coral')
        ax.set_title('Temperature')
        ax.set_xlabel('Cities')
        ax.set_ylabel('temp')
        plt.close()

        return fig

    def download(self):
        return self.helper.file_name()

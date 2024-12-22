from requests import get, exceptions
from os import getenv
from abc import ABC, abstractmethod
import logging


class APIGateway(ABC):
    """Abstract method that requests API using Semaphore Threads"""
    max_concurrent_requests = int(getenv('concurrent_requests')) or 5

    @abstractmethod
    def get_item(self, name, semaphore):
        pass

    @abstractmethod
    def transform(self, data, city_name):
        pass

    def format(self, data, meta):
        return data

    def fetch_data(self, url, semaphore):
        """
        Fetching data from public API
        :param url: string
        :param semaphore:
        :return:
        """
        with semaphore:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; AcmeInc/1.0)"
                }
                response = get(url, headers=headers)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response.json()
            except exceptions.RequestException as e:
                logging.error(f"Error fetching data from {url}: {e}")
                return None

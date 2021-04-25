from utils.functions import time, get_parameters_string
from utils.headers import nba_headers
import requests as r


class NBAEndpoint:
    """ Create object pointing to specified endpoint from stats.nba.com """
    # find endpoint documentation at https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints
    def __init__(self,
                 endpoint: str):
        self.endpoint = endpoint
        self.headers = nba_headers
        self.response = None

    def send_request(self,
                     parameters: dict):
        """ Ingests and converts parameters to full URL and saves the latest response within the object """
        parameters_string = get_parameters_string(parameters)
        url = f'https://stats.nba.com/stats/{self.endpoint}/?{parameters_string}'

        self.response = r.get(url, headers=self.headers).json()

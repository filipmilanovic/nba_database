from utils.functions import get_parameters_string
from utils.headers import nba_headers
import requests as r


class NBAEndpoint:
    """ Create object pointing to specified endpoint from stats.nba.com """
    # find endpoint documentation at https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints
    def __init__(self,
                 endpoint: str):
        self.endpoint = endpoint
        self.session = self.start_session()
        self.tries = 3
        self.response = None

    def start_session(self):
        if 'self.session' in locals():
            self.close_session()
        session = r.session()
        session.headers.update(nba_headers)

        return session

    def send_request(self,
                     parameters: dict):
        """ Ingests and converts parameters to full URL and saves the latest response within the object """
        parameters_string = get_parameters_string(parameters)
        url = f'https://stats.nba.com/stats/{self.endpoint}/?{parameters_string}'

        self.tries = 3

        while self.tries > 0:
            try:
                self.response = self.session.get(url, timeout=5).json()
                self.tries = 0
            except (r.exceptions.ConnectTimeout, r.exceptions.ReadTimeout):
                # restart Session and retry if time-out
                self.session = self.start_session()
                self.tries -= 1
                continue

    def close_session(self):
        self.session.close()

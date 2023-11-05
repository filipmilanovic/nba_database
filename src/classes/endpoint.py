import requests as r


class NBAEndpoint:
    """ Create object pointing to specified endpoint from stats.nba.com """
    # find endpoint documentation at https://github.com/swar/nba_api/tree/master/docs/nba_api/stats/endpoints
    def __init__(self,
                 endpoint: str,
                 header: dict):
        self.endpoint = endpoint
        self.header = header
        self.parameters = None
        self.url = None
        self.session = self.start_session()
        self.tries = 3
        self.response = None

    def start_session(self):
        if 'self.session' in locals():
            self.close_session()
        session = r.session()
        session.headers.update(self.header)

        return session
    
    def set_endpoint_parameters(self,
                                parameters: dict):
        parameter_list = [f'{i}={parameters[i]}' for i in parameters.keys()]
        self.parameters = '&'.join(parameter_list).replace(' ', '+')
    
    def set_endpoint_url(self):
        self.url = f'https://stats.nba.com/stats/{self.endpoint}/?{self.parameters}'

    def send_request(self,
                     parameters: dict,
                     tries=3):
        """ Ingests and converts parameters to full URL and saves the latest response within the object """
        self.set_endpoint_parameters(parameters)
        self.set_endpoint_url()

        self.tries = tries

        while self.tries > 0:
            try:
                self.response = self.session.get(self.url, timeout=5).json()
                self.tries = 0

                return self.response
            except (r.exceptions.ConnectTimeout, r.exceptions.ReadTimeout):
                # restart Session and retry if time-out
                self.session = self.start_session()
                self.tries -= 1
                continue

    def close_session(self):
        self.session.close()

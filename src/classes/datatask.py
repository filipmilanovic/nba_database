
from classes.datamodel import DataModel
from classes.endpoint import NBAEndpoint

class DataTask:
    """ Create object used to generate a task """
    def __init__(self,
                 target: str,
                 parameters: dict,
                 header: dict,
                 sql_parameters: dict):
        
        self.target = target
        self.parameters = parameters
        self.header = header
        self.sql_parameters = sql_parameters
        self.access_point = None
        self.data_model = None
    
    def create_endpoint(self):
        self.access_point = NBAEndpoint(endpoint=self.parameters['endpoint'],
                                        header=self.header)
        print(f'Created {self.target} access point')

    def send_endpoint_request(self):
        self.access_point.send_request(self.parameters['parameters'])
        print(f'Sent data request to {self.target} endpoint')
    
    def create_data_model(self):
        self.data_model = DataModel(self.target,
                                    self.parameters,
                                    self.sql_parameters)
        print(f'Created {self.target} data model')

    def get_response_data(self):
        self.data_model.get_response_components(self.access_point)
        print(f'Moved {self.target} response to {self.target} data model')
    
    def clean_response_data(self):
        self.data_model.get_key_indices()
        self.data_model.parse_data()
        print(f'Cleaned {self.target} data')

    def write_raw_data(self):
        self.data_model.create_raw_table()
        self.data_model.load_raw_data()
        print(f'Loaded {self.target} data in postgres')

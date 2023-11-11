""" Creates the DataModel object """
import datetime as dt
import hashlib
import sqlalchemy as sql

class DataModel:
    """ Create object used to prepare data for postgres ingestion """
    def __init__(self,
                 target_table: str,
                 parameters: dict,
                 **kwargs):

        self.target_table = target_table
        self.parameters = parameters
        self.kwargs = kwargs
        self.response_fields = None
        self.response_values = None
        self.unique_fields = None
        self.parsed_data = None

    def get_response_components(self,
                                endpoint):
        """
        Takes response from the NBAEndpoint object, then extracts the relevant
        data components (i.e. response values and corresponding fields,
        if required, using parameters.json)

        Args:
            endpoint (_type_): the response from the relevant NBAEndpoint object
        """
        # if the response deviates from the header/rowset standard, have to
        # manually define the keys used in the response
        if self.parameters.get('response_keys'):
            response = endpoint.response
            for key in self.parameters['response_keys']:
                response = response.get(key)
            self.response_values = response
        else:
            self.response_fields = endpoint.response['resultSets'][0]['headers']
            self.response_values = endpoint.response['resultSets'][0]['rowSet']

    def get_key_indices(self):
        """
        Uses parameters.json to get the relevant field or index required
        to generate unique keys from the data
        """
        # if the response deviates from the header/rowset standard, then
        # response is already dict, so we just need the key name
        # otherwise we have to find the corresponding index
        self.unique_fields = {
            f'{key}_INDEX': key
                if self.parameters.get('response_keys')
                else self.response_fields.index(key)
            for key in self.parameters['unique_keys']
        }

    def parse_data(self):
        """
        Generates a json-style object with a unique id for each element in
        the raw response, as well as the corresponding element
        """
        self.parsed_data = [
            {
                # since nba API doesn't guarantee unique keys, we need to
                # manually generate them
                'id':
                    hashlib.md5(
                        bytes(
                            ' '.join(
                                [
                                    str(row[field])
                                    for field in self.unique_fields.values()
                                 ]
                                ),
                            encoding='utf-8'
                        )
                    ).hexdigest(),
                'raw_data':
                    # if the response deviates from the header/rowset standard
                    # then it's already a dict
                    row[self.parameters['data_key']]
                    if self.parameters.get('response_keys')
                    # otherwise generate the dict ourselves
                    else {
                        self.response_fields[i]: row[i]
                        for i in range(len(self.response_fields))
                    }
            }
            for row in self.response_values
        ]

    def create_raw_table(self):
        """
        Creates the nba.raw table if it does not already exist.
        """
        sql.Table(self.target_table,
            self.kwargs['meta'],
            sql.Column('id', sql.VARCHAR, primary_key=True),
            sql.Column('raw_data', sql.JSON),
            sql.Column('row_created_at', sql.DateTime, default=dt.datetime.now())
        )

        self.kwargs['meta'].create_all(self.kwargs['eng'])

    def load_raw_data(self):
        """
        Inserts the parsed data, matchin id and raw_data to the corresponding
        fields
        """
        insert_stmt = sql.dialects.postgresql.insert(
            self.kwargs['meta'].tables[f'raw.{self.target_table}']
        ).values(self.parsed_data)

        insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])

        self.kwargs['conn'].execute(insert_stmt)
        self.kwargs['conn'].commit()

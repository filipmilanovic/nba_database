
import datetime as dt
import hashlib
import sqlalchemy as sql

class DataModel:
    """ Create object used as interfact to postgres data model """
    def __init__(self,
                 target_table: str,
                 parameters: dict,
                 **kwargs):
        
        self.target_table = target_table
        self.parameters = parameters
        self.eng = kwargs['eng']
        self.meta = kwargs['meta']
        self.conn = kwargs['conn']
        self.response_fields = None
        self.response_values = None
        self.key_indices = {}
        self.parsed_data = None
        self.model = None

    def get_response_components(self,
                                endpoint):
        # if the response deviates from the header/rowset standard, have to manually define the keys used in the response
        if self.parameters.get('response_keys'):
            response = endpoint.response
            for key in self.parameters['response_keys']:
                response = response.get(key)
            self.response_values = response
        else:
            self.response_fields = endpoint.response['resultSets'][0]['headers']
            self.response_values = endpoint.response['resultSets'][0]['rowSet']
    
    def get_key_indices(self):
        # if the response deviates from the header/rowset standard, then response is already dict
        if self.parameters.get('response_keys'):
            pass
        else:
            self.key_indices = {f'{key}_INDEX': self.response_fields.index(key) for key in self.parameters['unique_keys']}

    def parse_data(self):
        if self.parameters.get('response_keys'):
            self.parsed_data = [
                {
                    'id':
                        hashlib.md5(
                            bytes(' '.join([str(row[index]) for index in self.parameters['unique_keys']]), encoding='utf-8')
                        ).hexdigest(),
                    'raw_data':
                        row[self.parameters['data_key']]
                }
                for row in self.response_values
            ]
        else:
            self.parsed_data = [
                {
                    'id':
                        hashlib.md5(
                            bytes(' '.join([str(row[index]) for index in self.key_indices.values()]), encoding='utf-8')
                        ).hexdigest(),
                    'raw_data':
                        {
                            self.response_fields[i]: row[i] for i in range(len(self.response_fields))
                        }
                }
                for row in self.response_values
            ]
    
    def create_raw_table(self):
        self.model = sql.Table(self.target_table,
            self.meta,
            sql.Column('id', sql.VARCHAR, primary_key=True),
            sql.Column('raw_data', sql.JSON),
            sql.Column('row_created_at', sql.DateTime, default=dt.datetime.now())
        )
        
        self.meta.create_all(self.eng)
    
    def load_raw_data(self):
        insert_stmt = sql.dialects.postgresql.insert(self.meta.tables[f'raw.{self.target_table}']).values(self.parsed_data)

        insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['id'])

        self.conn.execute(insert_stmt)
        self.conn.commit()

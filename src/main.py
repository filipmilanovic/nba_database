""" hello """
import datetime as dt
import hashlib
import json
import sqlalchemy as sql

# import requests as r
from classes.endpoint import NBAEndpoint
from classes.datamodel import DataModel


## get core parameters
with open('src/utils/header.json', 'r') as file:
    header = json.load(file)

with open('src/utils/parameters.json', 'r') as file:
    parameters = json.load(file)

## Create postgres connection
eng = sql.create_engine('postgresql://user:password@127.0.0.1:5432/nba', echo=False)
conn = eng.connect()
meta = sql.MetaData(schema='raw')

sql_parameters = {
    'eng': eng,
    'conn': conn,
    'meta': meta
}

if not conn.dialect.has_schema(conn, 'raw'):
    conn.execute(sql.schema.CreateSchema('raw'))
    conn.commit()


## run specific job
TARGET_TABLE = 'draft'

target_endpoint = parameters[TARGET_TABLE]['endpoint']
target_parameters = parameters[TARGET_TABLE]['parameters']
# target_parameters['Season'] = 2020

TargetEndpoint = NBAEndpoint(endpoint=target_endpoint,
                             header=header)

TargetEndpoint.send_request(target_parameters)

draft_model = DataModel(TARGET_TABLE,
                        **sql_parameters)

draft_model.get_response_components(TargetEndpoint)

draft_model.get_key_indices(['PERSON_ID', 'SEASON'])

draft_model.parse_data()

draft_model.create_raw_table()

draft_model.load_raw_data()




# # TARGET_TABLE = 'transactions'
# # TABLE_PRIMARY_KEY = 'transaction_id'

# # url = 'https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json'

# # response = r.request(
# #     method='GET',
# #     url=url,
# #     headers=header
# # )

# # print(response.text)

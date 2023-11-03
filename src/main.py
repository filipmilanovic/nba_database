""" hello """
import json
import sqlalchemy as sql

# import requests as r
from classes.endpoint import NBAEndpoint


with open('src/utils/header.json', 'r') as file:
    header = json.load(file)

with open('src/utils/parameters.json', 'r') as file:
    parameters = json.load(file)

TARGET_TABLE = 'draft'

target_endpoint = parameters[TARGET_TABLE]['endpoint']
target_parameters = parameters[TARGET_TABLE]['parameters']
# target_parameters['Season'] = 2020

TargetEndpoint = NBAEndpoint(endpoint=target_endpoint,
                             header=header)

TargetEndpoint.send_request(target_parameters)

eng = sql.create_engine('postgresql://user:password@127.0.0.1:5432/nba', echo=False)
conn = eng.connect()
meta = sql.MetaData()

draft = sql.Table('draft',
    meta,
    sql.Column('raw_data', sql.JSON())
)

meta.create_all(eng)


data = {
    'raw_data': TargetEndpoint.response
}

conn.execute(meta.tables[TARGET_TABLE].insert(), data)
conn.commit()



# TARGET_TABLE = 'transactions'
# TABLE_PRIMARY_KEY = 'transaction_id'

# url = 'https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json'

# response = r.request(
#     method='GET',
#     url=url,
#     headers=header
# )

# print(response.text)

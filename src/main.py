""" hello """
import json
import sqlalchemy as sql

from classes.datatask import DataTask

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

## loop through endpoints to bring to sql
for target in parameters.keys():
    if target == 'games':
        Task = DataTask(target=target,
                        parameters=parameters[target],
                        header=header,
                        sql_parameters=sql_parameters)

        Task.create_endpoint()
        Task.send_endpoint_request()
        Task.create_data_model()
        Task.get_response_data()
        Task.clean_response_data()
        Task.write_raw_data()

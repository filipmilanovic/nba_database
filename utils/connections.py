# SETTING UP SQL CONNECTIONS
import pandas as pd
import sqlalchemy as sql
from utils.colours import *
from utils.environment import *
from utils.functions import get_distinct_ids
from utils.params import AS_UPSERT
from sqlalchemy.exc import ProgrammingError


def get_connection(db: str):
    """ set up MySQL connection """
    try:
        eng = sql.create_engine(f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{db}?charset=utf8mb4')
        conn = eng.connect()
        meta = sql.MetaData(eng)
        print(Colour.green + f'Established SQL connection to {db} schema' + Colour.end)
    except sql.exc.OperationalError:
        print(Colour.red + f"Couldn't establish SQL connection to {db}" + Colour.end)
        eng, meta, conn = None, None, None

    return eng, meta, conn


def get_write_query(metadata, connection, data: list, target_table: str, delete_query=None):
    if AS_UPSERT:
        connection.execute(delete_query)
    if data:
        connection.execute(metadata.tables[target_table].insert(), data)
        status = Colour.green + 'DB (Success)' + Colour.end
    else:
        status = 'DB (Nothing to write)'

    return status


def get_delete_query(metadata, engine, target_table: str, column: str, values: list):
    metadata.reflect(bind=engine)
    table = metadata.tables[target_table]

    output = table.delete().where(table.c[column].in_(values))

    return output


def write_data(engine, metadata, connection, data: list, target_table: str, primary_key: str):
    """ write data to the DB """
    distinct_ids = get_distinct_ids(data, primary_key)

    if AS_UPSERT:
        delete_query = get_delete_query(metadata=metadata,
                                        engine=engine,
                                        target_table=target_table,
                                        column=primary_key,
                                        values=distinct_ids)
    else:
        delete_query = None

    status = get_write_query(metadata=metadata,
                             connection=connection,
                             data=data,
                             target_table=target_table,
                             delete_query=delete_query)

    return status


def get_table_query(metadata, engine, name, column, cond):
    metadata.reflect(bind=engine)
    table = metadata.tables[name]

    output = sql.sql.select([table]).where(table.c[column].in_(cond))
    return output


def get_column_query(metadata, engine, name, column, cond_col=None, cond_val=None):
    metadata.reflect(bind=engine)
    table = metadata.tables[name]
    if cond_col:
        output = sql.sql.select([table.c[column]]).where(table.c[cond_col].in_(cond_val)).distinct()
    else:
        output = sql.sql.select([table.c[column]]).distinct()
    return output


def get_join_query(metadata, engine, left, right, column=False, cond=False):
    metadata.reflect(bind=engine)
    left_table = metadata.tables[left]
    right_table = metadata.tables[right]
    join = left_table.join(right=right_table, onclause=left_table.c.game_id == right_table.c.game_id)

    try:
        output = sql.sql.select('*').select_from(join).where(left_table.c[column].in_(cond))
    except KeyError:
        output = sql.sql.select('*').select_from(join)

    return output


def check_db_duplicates(data,
                        use_headers: bool,
                        data_key: str,
                        target_table: str,
                        target_key: str,
                        metadata,
                        engine,
                        connection):
    """ check for existing observations in the DB """
    if not AS_UPSERT:
        # find rows where data already exists in DB
        selectable = get_column_query(metadata, engine, target_table, target_key)
        skip = pd.read_sql(sql=selectable, con=connection)[target_key].tolist()
        if use_headers:
            # get location for key in each row of data
            headers = data['headers']
            rows = data['rowSet']
            header_loc = headers.index(data_key)

            data['rowSet'] = [row for row in rows if str(row[header_loc]) not in skip]
        else:
            # data frame conversion helps with speed for larger checks
            check_keys = pd.DataFrame(data)
            data = check_keys[~check_keys[data_key].isin(skip)].to_dict(orient='records')

    output = data

    return output


def get_query(query_path: str, file_name: str, extension='sql'):
    query_location = f'{query_path}{file_name}.{extension}'
    with open(query_location, 'r+') as f:
        return f.read()

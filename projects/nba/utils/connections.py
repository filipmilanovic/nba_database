# SETTING UP SQL CONNECTIONS
import sqlalchemy as sql
from modelling.projects.nba.utils.colours import *
from modelling.projects.nba.utils.environment import *
from sqlalchemy.exc import ProgrammingError


# Set up MySQL Connections
def get_connection(db):
    try:
        engine = sql.create_engine(f'mysql://{user}:{password}@{host}/{db}?charset=utf8mb4')
        connection = engine.connect()
        metadata = sql.MetaData(engine)
        print(Colour.green + f'Established SQL connection to {db} schema' + Colour.end)
    except sql.exc.OperationalError:
        print(Colour.red + f"Couldn't establish SQL connection to {db}" + Colour.end)
        engine, metadata, connection = None, None, None

    return engine, metadata, connection


# Set up generic queries
def get_table_query(metadata, engine, name, column, cond):
    metadata.reflect(bind=engine)
    table = metadata.tables[name]

    output = sql.sql.select([table]).where(table.c[column].in_(cond))
    return output


def get_column_query(metadata, engine, name, column):
    metadata.reflect(bind=engine)
    table = metadata.tables[name]
    output = sql.sql.select([table.c[column]]).distinct()
    return output


def get_delete_query(metadata, engine, name, column, series):
    metadata.reflect(bind=engine)
    table = metadata.tables[name]

    output = table.delete().where(table.c[column].in_(series))
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

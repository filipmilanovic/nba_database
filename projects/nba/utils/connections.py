# SETTING UP SQL CONNECTIONS
from modelling.projects.nba.utils.colours import *
from modelling.projects.nba.utils.environment import *
import sqlalchemy as sql
from sqlalchemy.exc import ProgrammingError, OperationalError, NoSuchTableError
from sqlalchemy.sql.expression import func


# Set up MySQL Connections
try:
    engine = sql.create_engine('mysql://' + USER + ':' + PASSWORD
                               + '@' + HOST + '/' + DATABASE + '?charset=utf8mb4')
    connection = engine.connect()
    metadata = sql.MetaData(engine)
    print(Colour.green + 'Established SQL connection to nba schema' + Colour.end)
except sql.exc.OperationalError:
    print(Colour.red + "Couldn't establish SQL connection" + Colour.end)

try:
    engine_raw = sql.create_engine('mysql://' + USER + ':' + PASSWORD
                                   + '@' + HOST + '/' + DATABASE_RAW + '?charset=utf8mb4')
    connection_raw = engine_raw.connect()
    metadata_raw = sql.MetaData(engine_raw)
    print(Colour.green + 'Established SQL connection to nba_raw schema' + Colour.end)
except sql.exc.OperationalError:
    print(Colour.red + "Couldn't establish SQL connection" + Colour.end)

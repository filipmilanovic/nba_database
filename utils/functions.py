# DEFINING FUNCTIONS FOR USE IN PROJECT
import pandas as pd
import pytz
from sqlalchemy.exc import OperationalError, NoSuchTableError
import sys
import time
import us
from utils.colours import *
from utils.connections import sql, get_column_query, get_delete_query
from utils.params import REBUILD_DB

start_time = time.time()


# Useful functions
def progress(iteration, iterations, iteration_name, lapsed, sql_status=''):
    # rewrite on same line
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%% %s %s %s" % ('='*round((iteration+1)/(iterations/20)),
                                                (iteration+1)/iterations*100,
                                                iteration_name,
                                                lapsed + ' seconds lapsed',
                                                sql_status))
    sys.stdout.flush()


def time_lapsed():
    return str('{0:.2f}'.format(time.time() - start_time))


# Load data
def load_data(df, sql_engine, meta, chunk_size=None):
    output = []
    # try SQL, then try CSV
    try:
        df_sql = sql.Table(f'{df}', meta, autoload=True, autoload_with=sql_engine)
        output = pd.read_sql(sql=sql.select([df_sql]), con=sql_engine, chunksize=chunk_size)
        print(Colour.green + f'Loaded {df} from DB' + Colour.end)
    except NoSuchTableError:
        print(Colour.red + f'Table {df} does not exist in DB' + Colour.end)
    except NameError:
        print(Colour.red + f'Could not load table {df} from DB' + Colour.end)

    return output


# Write data
def write_data(df,
               name,
               sql_engine,
               db_schema,
               if_exists='replace',
               index=True):

    # write to sql
    try:
        df.to_sql(name, con=sql_engine, schema=db_schema, if_exists=if_exists, index=index)
        status_sql = Colour.green + 'DB (Success)' + Colour.end
    except OperationalError:
        status_sql = Colour.red + 'DB (Failed)' + Colour.end

    status = {"sql": status_sql}

    return status


def handle_db_duplicates(data,
                         use_headers: bool,
                         data_key: str,
                         db_table: str,
                         db_key: str,
                         metadata,
                         engine,
                         connection):
    """ check data to skip or delete """
    if use_headers:
        # get location for key in each row of data
        headers = data['headers']
        rows = data['rowSet']
        header_loc = headers.index(data_key)

        index = [row[header_loc] for row in rows]
    else:
        index = [key[data_key] for key in data]

    if REBUILD_DB:
        # clear rows in DB where data already exists
        selectable = get_delete_query(metadata, engine, db_table, db_key, index)
        connection.execute(selectable)
    else:
        # skip rows where data already exists in DB
        selectable = get_column_query(metadata, engine, db_table, db_key)
        skip = pd.read_sql(sql=selectable, con=connection)[db_key].tolist()

        if use_headers:
            data['rowSet'] = [row for row in rows if row[header_loc] not in skip]
        else:
            data = [row for row in data if row[data_key] not in skip]

    output = data

    return output


#  Data cleaning functions
def left(x, length):
    return x[:length]


def right(x, length):
    return x[-length:]


def mid(x, start, length):
    return x[start:start+length]


def if_none(x, y):
    if x is None:
        output = y
    else:
        output = x
    return output


def find_occurrence(x, y, n):
    output = y.find(x)
    while output >= 0 and n > 1:
        output = y.find(x, output+len(x))
        n -= 1
    return output


def insert_row(df, index, values):
    # get rows from before desired index
    df_before = df[df.index < index]

    # append the desired row
    df_before.loc[index] = values

    # add 1 to index of rows after index
    df_after = df[df.index >= index]
    df_after.index += 1

    # join together
    output = pd.concat((df_before, df_after))

    return output


def swap_rows(df, i, j, direction):
    temp = df.loc[i].copy()

    if direction == 'forward':
        for row in range(i, j):
            df.loc[row] = df.loc[row+1]

        df.loc[j] = temp

    elif direction == 'back':
        for row in reversed(range(j, i+1)):
            df.loc[row] = df.loc[row-1]

        df.loc[j] = temp

    return df, j


def get_parameters_string(param_dict: dict):
    """ take dictionary of parameters and convert to string to add to URL """
    param_list = [f'{i}={param_dict[i]}' for i in list(param_dict.keys())]
    output = '&'.join(param_list).replace(' ', '+')

    return output


def get_sleep_time(iteration_start_time, target_duration):
    """ get duration of an iteration, then wait until target time reached """
    target_time = iteration_start_time + target_duration
    sleep_time = target_time - time.time()
    output = max(sleep_time, 0)

    return output


def convert_timezone(utc_time, state: str):
    new_tz = get_timezone(state).time_zones[0]
    output = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(new_tz)).replace(tzinfo=None)

    return output


def get_timezone(state: str):
    output = us.states.lookup(state)

    return output

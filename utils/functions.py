# DEFINING FUNCTIONS FOR USE IN PROJECT
import pandas as pd
import sys
import time
from utils.connections import sql
from utils.colours import *
from sqlalchemy.exc import OperationalError, NoSuchTableError

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

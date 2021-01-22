# DEFINING FUNCTIONS FOR USE IN PROJECT

from modelling.projects.nba.utils.colours import Colour
from modelling.projects.nba.utils.connections import *
from modelling.projects.nba.utils.path import *
import pandas as pd
import sqlalchemy as sql
import sys


# Useful functions
def progress(iteration, iterations, iteration_name, lapsed, sql_status, csv_status):
    # rewrite on same line
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%% %s %s %s %s" % ('='*round((iteration+1)/(iterations/20)),
                                                   (iteration+1)/iterations*100,
                                                   iteration_name,
                                                   lapsed + ' seconds lapsed',
                                                   sql_status,
                                                   csv_status))
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
        print(Colour.green + f'Loaded {df} from SQL' + Colour.end)
    except NoSuchTableError:
        print(Colour.red + f'Table {df} does not exist in DB' + Colour.end)
    except NameError:
        print(Colour.red + f'Could not load table {df} from SQL' + Colour.end)
        print(Colour.green + "Trying from CSV" + Colour.end)
        try:
            output = pd.read_csv(str(p) + f'/data/scraping/output/{df}.csv', sep=',', index_col=False)
            print(Colour.green + f'Loaded {df} from CSV' + Colour.end)
        except FileNotFoundError:
            print(Colour.red + f'Could not load table {df} from CSV' + Colour.end)
            quit()
    return output


# Write data
def write_data(df,
               name,
               to_csv,
               sql_engine,
               db_schema,
               if_exists='replace',
               index=True):
    if to_csv:
        try:
            df.to_csv(str(p) + f'/data/output/{name}.csv', sep=',', index=index)
            status_csv = Colour.green + 'CSV (Success)' + Colour.end
        except FileNotFoundError:
            status_csv = Colour.red + 'CSV (Path does not exist) ' + Colour.end
        except PermissionError:
            status_csv = Colour.red + 'CSV (File already opened) ' + Colour.end
    else:
        status_csv = Colour.red + 'CSV (Excluded)' + Colour.end

    # write to sql
    try:
        df.to_sql(name, con=sql_engine, schema=db_schema, if_exists=if_exists, index=index)
        status_sql = Colour.green + 'MySQL (Success)' + Colour.end
    except OperationalError:
        status_sql = Colour.red + 'MySQL (Failed)' + Colour.end

    status = {"sql": status_sql,
              "csv": status_csv}

    return status


# Set up dataframe
def initialise_df(table_name, columns, sql_engine, meta):
    # set up basic dataframe by loading from SQL or CSV if exists, or generating empty one
    try:
        df = load_data(df=table_name,
                       sql_engine=sql_engine,
                       meta=meta)
    except (NoSuchTableError, OperationalError, NameError):
        print(Colour.green + f'Building table {table_name} from scratch' + Colour.end)
        df = pd.DataFrame(columns=columns)

    return df


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


def get_seconds(x):
    minutes = x.minute
    seconds = x.second
    output = minutes*60 + seconds
    return output

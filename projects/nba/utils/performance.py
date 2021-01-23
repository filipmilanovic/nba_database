from modelling.projects import *  # high level packages
from modelling.projects.nba.utils.connections import sql
from modelling.projects.nba.utils.environment import *
from modelling.projects.nba.utils.colours import *
from sqlalchemy.exc import OperationalError
import inspect

# write performance of functions to DB
PERFORMANCE_TEST = False

if PERFORMANCE_TEST:
    # create connection to performance schema
    try:
        engine_perf = sql.create_engine('mysql://' + USER + ':' + PASSWORD
                                        + '@' + HOST + '/' + DATABASE_PERF + '?charset=utf8mb4')
        connection_perf = engine_perf.connect()
        metadata_perf = sql.MetaData(engine_perf)
        print(Colour.green + 'Established SQL connection to performance schema' + Colour.end)
    except sql.exc.OperationalError:
        print(Colour.red + "Couldn't establish SQL connection" + Colour.end)


performance = []


def log_performance():
    if PERFORMANCE_TEST:
        # get timestamp of call
        timestamp = time.time()

        # get caller method name
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        string = caller_frame[1][3]

        # create log row
        row = [timestamp, string]

        performance.append(row)
    return performance


def write_performance():
    if PERFORMANCE_TEST:
        output = pd.DataFrame(performance,
                              columns=['timestamp_at', 'function'])
        running_time = [output.timestamp_at[i] - output.timestamp_at[i - 1] for i in output.index if i > 0]
        output.loc[1:len(running_time), 'running_time'] = running_time

        output.to_sql('performance',
                      con=engine_perf,
                      schema='performance',
                      if_exists='replace',
                      index=False)

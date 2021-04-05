from modelling import *  # high level packages
from modelling.utils.connections import get_connection
from modelling.utils.environment import *
import inspect

# write performance of functions to DB
PERFORMANCE_TEST = False

if PERFORMANCE_TEST:
    # create connection to performance schema
    engine_perf, metadata_perf, connection_perf = get_connection(database_perf)

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

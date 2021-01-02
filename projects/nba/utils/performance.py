from modelling.projects import *  # high level packages
from modelling.projects.nba.utils.connections import *
import inspect

# write performance of functions to DB
PERFORMANCE_TEST = True

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
                      con=engine,
                      schema='performance',
                      if_exists='replace',
                      index=False)

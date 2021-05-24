from hashlib import sha256
import pytz
import sys
import time
import us


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
#
#
# #  Data cleaning functions
# def left(x, length):
#     return x[:length]
#
#
# def right(x, length):
#     return x[-length:]
#
#
# def mid(x, start, length):
#     return x[start:start+length]
#
#
# def if_none(x, y):
#     if x is None:
#         output = y
#     else:
#         output = x
#     return output
#
#
# def find_occurrence(x, y, n):
#     output = y.find(x)
#     while output >= 0 and n > 1:
#         output = y.find(x, output+len(x))
#         n -= 1
#     return output
#
#
# def insert_row(df, index, values):
#     # get rows from before desired index
#     df_before = df[df.index < index]
#
#     # append the desired row
#     df_before.loc[index] = values
#
#     # add 1 to index of rows after index
#     df_after = df[df.index >= index]
#     df_after.index += 1
#
#     # join together
#     output = pd.concat((df_before, df_after))
#
#     return output
#
#
# def swap_rows(df, i, j, direction):
#     temp = df.loc[i].copy()
#
#     if direction == 'forward':
#         for row in range(i, j):
#             df.loc[row] = df.loc[row+1]
#
#         df.loc[j] = temp
#
#     elif direction == 'back':
#         for row in reversed(range(j, i+1)):
#             df.loc[row] = df.loc[row-1]
#
#         df.loc[j] = temp
#
#     return df, j


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
    """ convert a utc timezone to a timezone based on the desired US state (two-letter abbreviation) """
    new_tz = get_timezone(state).time_zones[0]
    output = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(new_tz)).replace(tzinfo=None)

    return output


def get_timezone(state: str):
    """ get the name of a timezone for a given US state """
    output = us.states.lookup(state)

    return output


def get_distinct_ids(data: list, key: str):
    """ return the distinct values of a desired key in a list of dictionaries """
    output = [row[key] for row in data]

    return output


def get_hash(obj, length: int):
    bytes_obj = obj.encode('utf-8')
    hash_obj = sha256()
    hash_obj.update(bytes_obj)
    output = hash_obj.hexdigest()[0:length]

    return output

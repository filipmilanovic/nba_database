from data import *


def all_playoffs_data():
    """ set up iterations to get all data """
    iterations = list(range(len(season_range)))
    for iteration in iterations:
        get_season_data(iteration)


def get_season_data(iteration: int):
    """ get data for the season """
    iteration_start_time = time.time()

    season = season_range[iteration]

    generate_playoffs_json(season)
    series_logs = get_series_logs(playoffs_generator.response, season)

    status = write_data(engine, metadata, connection, series_logs, TARGET_TABLE, TABLE_PRIMARY_KEY)

    progress(iteration=iteration,
             iterations=len(season_range),
             iteration_name='Season ' + str(season_range[iteration]),
             lapsed=time_lapsed(),
             sql_status=status)

    # sleep to avoid hitting rate limit on requests
    sleep_time = get_sleep_time(iteration_start_time, 1)

    time.sleep(sleep_time)


def generate_playoffs_json(season: int):
    """ get the game logs for a given season """
    parameters_season = get_request_parameters(season)
    playoffs_generator.send_request(parameters_season)


def get_request_parameters(season: int):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'SeasonYear': season - 1,
              'State': '2'}

    return output


def get_series_logs(json, season: int):
    """ create list of games dicts from json """
    logs = json['bracket']['playoffBracketSeries']

    series_data = [get_series_data(series, season) for series in logs]
    output = check_db_duplicates(series_data, False, 'series_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def get_series_data(series_info: dict, season: int):
    """ convert raw data to a tidied dictionary """
    # set 0s as null
    output = {'series_id': get_series_id(series_info['seriesId'],
                                         str(series_info['highSeedId']),
                                         str(series_info['lowSeedId']),
                                         season),
              'conference': series_info['seriesConference'],
              'playoff_round': series_info['roundNumber'],
              'higher_seed_team_id': none_if(series_info['highSeedId'], 0),
              'higher_seed': none_if(series_info['highSeedRank'], 0),
              'lower_seed_team_id': none_if(series_info['lowSeedId'], 0),
              'lower_seed': none_if(series_info['lowSeedRank'], 0)
              }

    return output


def get_series_id(series_id: str, high_team_id: str, low_team_id: str, season: int):
    """ clean the series IDs into a numeric only string"""
    # team data is missing prior to 2019, so have to deal with these 0s separately
    if high_team_id != '0':
        remove_team_id = series_id.replace(high_team_id, '').replace(low_team_id, '')
    else:
        remove_team_id = series_id.replace('0000000000', '')
    # commonplayoffseries returns something like 004190010, while playoffbracket returns something like 004201910
    fixed_season = remove_team_id.replace(str(season - 1), f'{"{:02d}".format(season-2001+(season<2001)*100)}00')
    output = fixed_season.replace('_', '')

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_playoffs(metadata)

    TARGET_TABLE = 'playoffs'
    TABLE_PRIMARY_KEY = 'series_id'
    QUERY_PATH = f'{ROOT_PATH}/queries/data/{TARGET_TABLE}/'

    playoffs_generator = NBAEndpoint(endpoint='playoffbracket')

    season_range = pd.Series(range(START_SEASON, END_SEASON + 1))

    all_playoffs_data()

    query = get_query(QUERY_PATH, 'add_teams_info', 'sql')
    connection.execute(query)
    connection.execute('COMMIT')

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

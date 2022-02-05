from data import *


def all_lineup_data():
    """ set up iterations to get all data """
    iterations = list(range(len(season_range)))
    for iteration in iterations:
        get_season_data(iteration)


def get_season_data(iteration: int):
    """ get lineup data for a season """
    iteration_start_time = time.time()

    season = season_range[iteration]

    for season_type in season_types:
        status = get_season_type_data(season, season_type)

        progress(iteration=iteration,
                 iterations=len(season_range),
                 iteration_name=f'Season {str(season_range[iteration])} {season_type}',
                 lapsed=time_lapsed(),
                 sql_status=status)

        # sleep to avoid hitting rate limit on requests
        sleep_time = get_sleep_time(iteration_start_time, 1)

        time.sleep(sleep_time)


def get_season_type_data(season: int, season_type: str):
    """ get data for season type """
    generate_playoffs_json(season, season_type)
    game_logs = get_game_logs(game_log_generator.response)

    status = write_data(engine, metadata, connection, game_logs, TARGET_TABLE, TABLE_PRIMARY_KEY)

    return status


def generate_playoffs_json(season: int, season_type: str):
    """ generate json of draft picks """
    parameters = get_request_parameters(season, season_type)
    game_log_generator.send_request(parameters)


def get_request_parameters(season: int, season_type: str):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'Season': get_season_text(season),
              'SeasonType': season_type}

    return output


def get_game_logs(json):
    """ create list of games dicts from json """
    data = json['resultSets'][0]

    columns = data['headers']
    rows = data['rowSet']
    season_loc = columns.index('SEASON_YEAR')

    game_log_data = [dict(zip(columns, row)) for row in rows if int(row[season_loc][0:4]) >= START_SEASON - 1]

    players_games = [get_players_games(player_game) for player_game in game_log_data]

    # only check for duplicates if data not empty
    if players_games:
        output = check_db_duplicates(players_games, False, 'lineup_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                     metadata, engine, connection)
    else:
        output = []

    return output


def get_players_games(player_game: dict):
    """ convert raw data to a tidied dictionary """
    output = {'lineup_id': int(player_game['GAME_ID']) * 10000000 + int(player_game['PLAYER_ID']),
              'game_id': player_game['GAME_ID'],
              'team_id': player_game['TEAM_ID'] + 1,
              'player_id': player_game['PLAYER_ID'],
              'seconds': int(player_game['MIN']*60)
              }

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_lineups(metadata)

    TARGET_TABLE = 'lineups'
    TABLE_PRIMARY_KEY = 'lineup_id'

    game_log_generator = NBAEndpoint(endpoint='playergamelogs')

    season_range = pd.Series(range(START_SEASON, END_SEASON + 1))
    season_types = ['Regular Season', 'Playoffs', 'PlayIn']

    all_lineup_data()

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

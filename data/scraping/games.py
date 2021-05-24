from data import *


def all_games_data():
    """ set up iterations to get all data """
    iterations = list(range(len(season_range)))
    for iteration in iterations:
        get_season_data(iteration)


def get_season_data(iteration: int):
    """ get data for the season """
    iteration_start_time = time.time()

    season = season_range[iteration]

    generate_game_logs_json(season)
    generate_playoffs_json(season)

    # clean raw game logs
    game_logs = get_game_logs(game_generator.response)

    # clean game data for writing
    games = get_games(game_logs, season)

    status = write_data(engine, metadata, connection, games, TARGET_TABLE, TABLE_PRIMARY_KEY)

    progress(iteration=iteration,
             iterations=len(season_range),
             iteration_name='Season ' + str(season_range[iteration]),
             lapsed=time_lapsed(),
             sql_status=status)

    # sleep to avoid hitting rate limit on requests
    sleep_time = get_sleep_time(iteration_start_time, 2)

    time.sleep(sleep_time)


def generate_game_logs_json(season: int):
    """ get the game logs for a given season """
    games_parameters_season = get_games_request_parameters(season)
    game_generator.send_request(games_parameters_season)


def get_games_request_parameters(season: int):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'Season': season - 1}

    return output


def generate_playoffs_json(season: int):
    """ get the playoffs series' for a given season """
    playoffs_parameters_season = get_playoffs_request_parameters(season)
    playoffs_generator.send_request(playoffs_parameters_season)


def get_playoffs_request_parameters(season: int):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'Season': season - 1}

    return output


def get_game_logs(json):
    """ create list of games dicts from json """
    logs = json['leagueSchedule']['gameDates']
    game_log = [row for row in [rows['games'] for rows in logs] for row in row]

    output = check_db_duplicates(game_log, False, 'gameId', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def get_games(data: dict, season: int):
    """ convert game logs to final games table and exclude non-competitive games"""
    output = [get_game_data(game, season) for game in data
              # remove All-Star teams and errors
              if game['homeTeam']['teamId'] not in list(range(1610616800, 1610616900)) + [0]
              # from season 2018 onwards, API returns regular season week number, and playoffs game number
              and ((game['weekNumber'] > 0
                    or game['seriesGameNumber'] != '')
                   # before season 2018, a manual input dictionary for season start dates has been added
                   or ((season <= 2017)
                       and (get_home_time(game, season) >= get_season_start_date(season))))]

    return output


def get_game_data(game_dict: dict, season: int):
    """ get dictionary of game information """
    playoff_info = get_playoff_info(game_dict)

    # playoff data is dirty up to 2001
    if season <= 2001:
        playoff_info['SERIES_ID'] = None
        playoff_info['GAME_NUM'] = None

    output = {'game_id': game_dict['gameId'],
              'game_time': get_home_time(game_dict, season),
              'arena': game_dict['arenaName'],
              'national_broadcast': get_national_broadcaster(game_dict),
              'home_team_id': game_dict['homeTeam']['teamId'],
              'home_score': game_dict['homeTeam']['score'],
              'away_team_id': game_dict['awayTeam']['teamId'],
              'away_score': game_dict['awayTeam']['score'],
              'overtime': get_ot_info(game_dict['gameStatusText']),
              'season': season,
              'is_playoffs': (playoff_info['GAME_ID'] is not None) * 1,
              'series_id': playoff_info['SERIES_ID'],
              'series_game': playoff_info['GAME_NUM']
              }

    return output


def get_playoff_info(game_dict: dict):
    """ get information of playoff series """
    data = playoffs_generator.response['resultSets'][0]
    columns = data['headers']
    rows = data['rowSet']
    game_id_loc = columns.index('GAME_ID')

    output = dict.fromkeys(columns)

    dict_generator = (row for row in rows if row[game_id_loc] == game_dict['gameId'])
    for row in dict_generator:
        output = dict(zip(columns, row))

    return output


def get_national_broadcaster(game_dict: dict):
    """ get national broadcasting information """
    try:
        output = game_dict['broadcasters']['nationalBroadcasters'][0]['broadcasterDisplay']
    except IndexError:
        output = None

    return output


def get_ot_info(game_status_text: str):
    """ extract number of OTs """
    output = re.search(r'Final/(.*)', game_status_text)

    if output:
        output = output.group(1)

    return output


def get_home_time(game_dict: dict, season: int):
    """ get localised datetime for game"""
    # prior to 2003, homeTeamTime not population
    if season <= 2003:
        game_time_utc = dt.strptime(game_dict['gameDateTimeUTC'], '%Y-%m-%dT%H:%M:%SZ')
        state = game_dict['arenaState']

        # conversion errors caused by international pre-season games, so just set to UTC and it will be excluded
        try:
            output = convert_timezone(game_time_utc, state)
        except AttributeError:
            output = game_time_utc
    else:
        output = dt.strptime(game_dict['homeTeamTime'], '%Y-%m-%dT%H:%M:%SZ')

    return output


def get_season_start_date(season: int):
    """ get the season start date, or set to start of year to avoid equation errors """
    try:
        output = season_start_dates[season]
    except KeyError:
        output = dt.datetime(season, 1, 1)

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(MYSQL_DATABASE)
    create_table_games(engine, metadata)

    TARGET_TABLE = 'games'
    TABLE_PRIMARY_KEY = 'game_id'

    game_generator = NBAEndpoint(endpoint='scheduleLeaguev2')
    playoffs_generator = NBAEndpoint(endpoint='commonplayoffseries')

    # pick up date range from parameters
    season_range = pd.Series(range(START_SEASON, END_SEASON + 1))

    all_games_data()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

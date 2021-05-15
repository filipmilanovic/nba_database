# SCRAPING GAME DATA
from data import *


def all_game_data():
    """ set up iterations to get all data """
    iterations = list(range(len(season_range)))
    for iteration in iterations:
        get_season_data(iteration)


def get_season_data(iteration: int):
    """ get data for the season """
    iteration_start_time = time.time()

    season = season_range[iteration]

    # get game logs
    generate_game_logs_json(season)
    game_logs = get_game_logs(game_generator.response)

    # extract game information
    games = get_games(game_logs, season)

    write_season_data(games, iteration)

    # sleep to avoid hitting rate limit on requests
    sleep_time = get_sleep_time(iteration_start_time, 1)

    time.sleep(sleep_time)


def generate_game_logs_json(season: int):
    """ get the game logs for a given season type """
    # build parameters for regular season request
    parameters_regular_season = get_request_parameters(season)
    game_generator.send_request(parameters_regular_season)


def get_request_parameters(season: int):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'Season': season - 1}

    return output


def get_game_logs(json):
    """ create list of games dicts from json """
    logs = json['leagueSchedule']['gameDates']
    game_log = [row for row in [rows['games'] for rows in logs] for row in row]

    output = handle_db_duplicates(game_log, False, 'gameId', 'games', 'game_id', metadata, engine, connection)

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
              'is_playoffs': len(playoff_info)/6
              }

    return output


def get_playoff_info(game_dict: dict):
    """ get game number of playoff series """
    try:
        output = game_dict['seriesGameNumber']
    except IndexError:
        output = None

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
        game_time_utc = get_datetime(game_dict['gameDateTimeUTC'])
        state = game_dict['arenaState']

        # conversion errors caused by international pre-season games, so just set to UTC and it will be excluded
        try:
            output = convert_timezone(game_time_utc, state)
        except AttributeError:
            output = game_time_utc
    else:
        output = get_datetime(game_dict['homeTeamTime'])

    return output


def get_datetime(date_str: str):
    output = dt.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

    return output


def get_season_start_date(season: int):
    """ get the season start date, or set to start of year to avoid equation errors """
    try:
        output = season_start_dates[season]
    except KeyError:
        output = dt.datetime(season, 1, 1)

    return output


def write_season_data(data: list, iteration: int):
    """ write season data to the DB """
    status = write_data(df=pd.DataFrame(data),
                        name='games',
                        sql_engine=engine,
                        db_schema='nba',
                        if_exists='append',
                        index=False)

    progress(iteration=iteration,
             iterations=len(season_range),
             iteration_name='Season ' + str(season_range[iteration]),
             lapsed=time_lapsed(),
             sql_status=status['sql'])


if __name__ == '__main__':
    engine, metadata, connection = get_connection(MYSQL_DATABASE)
    create_table_games(engine, metadata)

    columns = [c.name for c in sql.Table('games', metadata, autoload=True).columns]

    game_generator = NBAEndpoint(endpoint='scheduleLeaguev2')

    # pick up date range from parameters
    season_range = pd.Series(range(start_season_games, end_season_games + 1))

    all_game_data()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

from data.scripts import *


def all_standings_data():
    """ set up iterations to get all scripts """
    iterations = list(range(len(season_range)))
    for iteration in iterations:
        get_season_data(iteration)


def get_season_data(iteration: int):
    """ get scripts for the season """
    iteration_start_time = time.time()

    season = season_range[iteration]

    generate_standings_json(season)
    standings = get_standings(standings_generator.response, season)

    status = write_data(engine, metadata, connection, standings, TARGET_TABLE, TABLE_PRIMARY_KEY)

    progress(iteration=iteration,
             iterations=len(season_range),
             iteration_name='Season ' + str(season_range[iteration]),
             lapsed=time_lapsed(),
             sql_status=status)

    # sleep to avoid hitting rate limit on requests
    sleep_time = get_sleep_time(iteration_start_time, 1)

    time.sleep(sleep_time)


def generate_standings_json(season: int):
    """ get the standings for a given season """
    parameters_season = get_request_parameters(season)
    standings_generator.send_request(parameters_season)


def get_request_parameters(season: int):
    """ generate the parameters for the request """
    output = {'LeagueID': '00',
              'Season': season - 1,
              'SeasonType': 'Regular Season'}

    return output


def get_standings(json, season: int):
    """ create standings """
    data = json['resultSets'][0]
    columns = data['headers']
    rows = data['rowSet']

    standings_data = [get_standings_data(dict(zip(columns, team)), season) for team in rows]

    output = check_db_duplicates(standings_data, False, 'team_season_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def get_standings_data(team_dict: dict, season: int):
    """ take team/season dict and output cleaned dict """
    output = {'team_season_id': team_dict['TeamID'] + season * 10000000000,
              'season': season,
              'team_id': team_dict['TeamID'],
              'wins': team_dict['WINS'],
              'losses': team_dict['LOSSES'],
              'playoff_seed': team_dict['PlayoffRank'],
              'league_rank': team_dict['LeagueRank']}

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_standings(metadata)

    TARGET_TABLE = 'standings'
    TABLE_PRIMARY_KEY = 'team_season_id'
    QUERY_PATH = f'{ROOT_PATH}/queries/scripts/{TARGET_TABLE}/'

    standings_generator = NBAEndpoint(endpoint='leaguestandingsv3')

    season_range = pd.Series(range(START_SEASON, END_SEASON + 1))

    all_standings_data()

    query = get_query(QUERY_PATH, 'fix_seeds', 'sql')
    connection.execute(query)
    connection.execute('COMMIT')

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

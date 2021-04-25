# SCRAPING GAME DATA
from data import *


def all_game_data():
    """ set up iterations to get all data """
    iterations = list(range(len(season_range)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(season_data, iterations)
        executor.shutdown()


def season_data(iteration):
    """ get data for the season """
    season = season_range[iteration]

    # get regular season games
    generate_logs_json(season, 0)
    logs_regular_season = get_logs(game_generator.response)
    games_regular_season = get_games(logs_regular_season, season, 0)

    # get playoff games
    generate_logs_json(season, 1)
    log_playoffs = get_logs(game_generator.response)
    playoffs_regular_season = get_games(log_playoffs, season, 1)

    output = games_regular_season.append(playoffs_regular_season)

    write_season_data(output, iteration)

    # sleep to avoid hitting rate limit on requests
    time.sleep(2)


def generate_logs_json(season, is_playoffs):
    """ get the game logs for a given season type """
    # build parameters for regular season request
    parameters_regular_season = get_request_parameters(season, is_playoffs)
    game_generator.send_request(parameters_regular_season)


def get_request_parameters(season, is_playoffs):
    """ generate the parameters for the request """
    output = {'Counter': '0',
              'Direction': 'DESC',
              'LeagueID': '00',
              'PlayerOrTeam': 'T',
              'Season': season - 1,
              'SeasonType': season_type[is_playoffs],
              'Sorter': 'DATE'}

    return output


def get_logs(json):
    """ create data frame of games from json """
    logs = json['resultSets'][0]
    logs_columns = logs['headers']
    logs_rows = logs['rowSet']

    logs_df = pd.DataFrame.from_dict(data=logs_rows)
    logs_df.columns = logs_columns

    output = check_db_duplicates(logs_df, 'GAME_ID', 'games', 'game_id', metadata, engine, connection)

    return output


def get_games(df, season, is_playoffs):
    """ convert game logs to final games table """
    df['IS_HOME'] = 1 - df['MATCHUP'].str.contains('@')

    output = pd.DataFrame(columns=columns)

    output[['game_id', 'game_date']] = get_game_id_date(df)
    output[['home_team_id', 'home_score']] = get_team_data(df=df, is_home=True)
    output[['away_team_id', 'away_score']] = get_team_data(df=df, is_home=False)
    output['season'] = [int(season)] * len(output)
    output['is_playoffs'] = [is_playoffs] * len(output)

    return output


def get_game_id_date(df):
    """ get distinct game ID and game date """
    df_subset = df[['GAME_ID', 'GAME_DATE']]
    output = df_subset.drop_duplicates(subset='GAME_ID').reset_index(drop=True)

    return output


def get_team_data(df, is_home):
    """ get team ID and score for the game """
    output = df.loc[df['IS_HOME'] == is_home, ['TEAM_ID', 'PTS']].reset_index(drop=True)

    return output


def write_season_data(df, iteration):
    """ write season data to the DB """
    status = write_data(df=df,
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
    engine, metadata, connection = get_connection(database)
    create_table_games(engine, metadata)

    columns = [c.name for c in sql.Table('games', metadata, autoload=True).columns]

    game_generator = NBAEndpoint(endpoint='leaguegamelog')

    # pick up date range from parameters
    season_range = pd.Series(range(start_season_games, end_season_games + 1))

    all_game_data()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

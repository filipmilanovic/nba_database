from data import *


def get_seasons_teams():
    """ generate teams by season, then get team detail for each season """
    generate_seasons_teams_json()
    tidy_dict = tidy_seasons_teams(seasons_teams_generator.response)
    output = check_db_duplicates(tidy_dict, False, 'team_season_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def generate_seasons_teams_json():
    """ get all season and team combinations """
    parameters_seasons_teams = get_seasons_teams_parameters()
    seasons_teams_generator.send_request(parameters_seasons_teams)
    seasons_teams_generator.close_session()


def get_seasons_teams_parameters():
    """ generate the parameters for the request """
    output = {'LeagueID': '00'}

    return output


def tidy_seasons_teams(json: dict):
    """ get the json of season_teams and output tidied dictionary """
    teams = json['resultSets'][0]
    teams_columns = teams['headers']
    teams_rows = teams['rowSet']
    output = []

    for team in teams_rows:
        data_dict = dict(zip(teams_columns, team))
        season_team = get_season_team_dict(data_dict)
        output += [{'team_season_id': season_team['team_id'] + season * 10000000000,
                    'team_id': season_team['team_id'],
                    'season': season}
                   for season in range(season_team['start_year'], season_team['end_year'] + 1)]

    return output


def get_season_team_dict(data_dict: dict):
    """ convert raw data to tidied dictionary """
    output = {
        'team_id': data_dict['TEAM_ID'],
        'start_year': max(int(data_dict['MIN_YEAR']) + 1, START_SEASON),
        'end_year': min(int(data_dict['MAX_YEAR']) + 1, END_SEASON)
    }

    return output


def get_teams(seasons_teams_list):
    """ get team information by season and write to db """
    iterations = list(range(len(seasons_teams_list)))

    for iteration in iterations:
        iteration_start_time = time.time()

        season_team = seasons_teams_list[iteration]

        try:
            team_info = get_team_info(season_team)
        except IndexError:
            print(f"team_id {season_team['team_id']} doesn't return anything in {season_team['season']}")
            continue

        team_dict = get_team_dict(team_info, season_team['season'])

        status = write_data(engine, metadata, connection, [team_dict], TARGET_TABLE, TABLE_PRIMARY_KEY)

        progress(iteration=iteration,
                 iterations=len(iterations),
                 iteration_name=f'{team_dict["team_name"]} {team_dict["season"]}',
                 lapsed=time_lapsed(),
                 sql_status=status)

        # sleep to avoid rate limits
        sleep_time = get_sleep_time(iteration_start_time, 1)

        time.sleep(sleep_time)


def get_team_info(team_season: dict):
    """ get dictionary of team information """
    generate_team_json(team_season)

    json = team_generator.response

    team_info = json['resultSets'][0]
    data_columns = team_info['headers']
    data_rows = team_info['rowSet'][0]

    output = dict(zip(data_columns, data_rows))

    return output


def generate_team_json(team_parameters: dict):
    """ generate json for a specific team and season combination """
    request_parameters = get_request_parameters(team_parameters)
    team_generator.send_request(request_parameters)


def get_request_parameters(team_parameters: dict):
    """ generate the parameters for the request """
    team_id = team_parameters['team_id']
    season = team_parameters['season']
    output = {'LeagueID': '00',
              'TeamID': team_id,
              'Season': season - 1,
              'SeasonType': 'Regular Season'}

    return output


def get_team_dict(data_dict: dict, season: int):
    """ convert raw data to a tidied dictionary """
    output = {
        'team_season_id': data_dict['TEAM_ID'] + season * 10000000000,
        'team_id': data_dict['TEAM_ID'],
        'team_name': data_dict['TEAM_CITY'] + ' ' + data_dict['TEAM_NAME'],
        'abbreviation': data_dict['TEAM_ABBREVIATION'],
        'conference': data_dict['TEAM_CONFERENCE'],
        'division': data_dict['TEAM_DIVISION'],
        'season': season
    }

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(MYSQL_DATABASE)
    create_table_teams(engine, metadata)

    TARGET_TABLE = 'teams'
    TABLE_PRIMARY_KEY = 'team_season_id'

    seasons_teams_generator = NBAEndpoint(endpoint='commonteamyears')
    team_generator = NBAEndpoint(endpoint='teaminfocommon')

    # get list of team_id and season pairs
    seasons_teams = get_seasons_teams()

    # get team information by season
    get_teams(seasons_teams)

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

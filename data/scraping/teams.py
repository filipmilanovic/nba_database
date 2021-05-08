# CONVERTING TEAMS TO DATAFRAME
## GRAB HISTORICAL NAMES AND ARENA
## ADD REBUILD_DB HANDLING
from data import *
from sqlalchemy.exc import IntegrityError


def all_team_data():
    """ generate teams by season, then get team detail for each season """
    generate_teams_seasons_json()
    teams_seasons = get_teams_seasons(team_season_generator.response)

    iterations = len(teams_seasons)

    for iteration in range(iterations):
        iteration_start_time = time.time()

        team_info = get_team_info(teams_seasons[iteration])
        season = teams_seasons[iteration][1]
        team_dict = get_team_dict(team_info, season)

        write_team_data(team_dict, iteration, iterations)

        # sleep to avoid rate limits
        sleep_time = get_sleep_time(iteration_start_time, 1)

        time.sleep(sleep_time)


def generate_teams_seasons_json():
    parameters_team_season = get_teams_seasons_parameters()
    team_season_generator.send_request(parameters_team_season)
    team_season_generator.close_session()


def get_teams_seasons_parameters():
    """ generate the parameters for the request """
    output = {'LeagueID': '00'}

    return output


def get_teams_seasons(json):
    teams = json['resultSets'][0]
    teams_columns = teams['headers']
    teams_rows = teams['rowSet']

    output = []

    for i in teams_rows:
        data_dict = dict(zip(teams_columns, i))
        team_season = get_team_season_dict(data_dict)
        output += [(team_season['team_id'], year) for year in range(team_season['start_year'], team_season['end_year'])]
        output = list(set(output))

    return output


def get_team_season_dict(data_dict):
    output = {
        'team_id': data_dict['TEAM_ID'],
        'start_year': max(int(data_dict['START_YEAR']), start_season_games),
        'end_year': int(data_dict['END_YEAR'])
    }

    return output


def get_team_info(teams_seasons):
    generate_team_json(teams_seasons)

    json = team_generator.response
    team_season = json['resultSets'][0]

    data_columns = team_season['headers']
    data_rows = team_season['rowSet'][0]
    output = dict(zip(data_columns, data_rows))

    return output


def generate_team_json(team_parameters):
    parameters_teams = get_request_parameters(team_parameters)
    team_generator.send_request(parameters_teams)


def get_request_parameters(team_parameters):
    """ generate the parameters for the request """
    team_id = team_parameters[0]
    season = team_parameters[1]
    output = {'TeamID': team_id,
              'Season': season}

    return output


def get_team_dict(data_dict, season):
    output = {
        'team_season_id': data_dict['TEAM_ID'] * 10000 + season,
        'team_id': data_dict['TEAM_ID'],
        'team_name': data_dict['CITY'] + ' ' + data_dict['NICKNAME'],
        'team_short_name': data_dict['ABBREVIATION'],
        'season': season + 1,
        'arena': get_arena(data_dict)
    }

    return output


def get_arena(data_dict):
    output = data_dict['ARENA']

    return output


def write_team_data(team_info, iteration, iterations):
    try:
        connection.execute(metadata.tables['teams'].insert(), [team_info])
        status_sql = Colour.green + 'DB (Success)' + Colour.end
    except IntegrityError:
        status_sql = Colour.red + 'DB (Already Exists)' + Colour.end

    progress(iteration=iteration,
             iterations=iterations,
             iteration_name=f'{team_info["team_name"]} {team_info["season"]}',
             lapsed=time_lapsed(),
             sql_status=status_sql)


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    create_table_teams(engine, metadata)

    columns = [c.name for c in sql.Table('teams', metadata, autoload=True).columns]

    team_season_generator = NBAEndpoint(endpoint='franchisehistory')
    team_generator = NBAEndpoint(endpoint='teamdetails')

    all_team_data()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Team Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

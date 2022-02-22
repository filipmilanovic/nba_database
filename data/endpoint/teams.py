import sys
import time

from utils.colours import Colour
from utils.connections import check_db_duplicates, create_table, write_data
from utils.endpoint import NBAEndpoint
from utils.functions import get_sleep_time, progress, start_time, time_lapsed
from utils.params import REBUILD_TABLES, START_SEASON, END_SEASON


def get_seasons_teams(conn, target_table, primary_key):
    """ generate teams by season, then get team detail for each season """
    generate_seasons_teams_json()
    tidy_dict = tidy_seasons_teams(seasons_teams_generator.response)
    output = check_db_duplicates(conn, target_table, primary_key, 'team_season_id', tidy_dict, False, REBUILD_TABLES)

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
    """ convert raw scripts to tidied dictionary """
    output = {
        'team_id': data_dict['TEAM_ID'],
        'start_year': max(int(data_dict['MIN_YEAR']) + 1, START_SEASON),
        'end_year': min(int(data_dict['MAX_YEAR']) + 1, END_SEASON)
    }

    return output


def get_teams(seasons_teams_list, conn, target_table, primary_key):
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

        write_data(conn, target_table, primary_key, [team_dict], 'row', REBUILD_TABLES)

        progress(iteration=iteration,
                 iterations=len(iterations),
                 iteration_name=f'{team_dict["team_name"]} {team_dict["season"]}',
                 lapsed=time_lapsed())

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
    """ convert raw scripts to a tidied dictionary """
    output = {
        'team_season_id': str(data_dict['TEAM_ID'] + season * 10000000000),
        'team_id': str(data_dict['TEAM_ID']),
        'team_name': data_dict['TEAM_CITY'] + ' ' + data_dict['TEAM_NAME'],
        'abbreviation': data_dict['TEAM_ABBREVIATION'],
        'conference': data_dict['TEAM_CONFERENCE'],
        'division': data_dict['TEAM_DIVISION'],
        'season': str(season)
    }

    return output


def run_teams(target_table, primary_key, conn):
    create_table(conn, 'teams', REBUILD_TABLES)

    global seasons_teams_generator
    seasons_teams_generator = NBAEndpoint(endpoint='commonteamyears')

    global team_generator
    team_generator = NBAEndpoint(endpoint='teaminfocommon')

    seasons_teams = get_seasons_teams(conn, target_table, primary_key)

    get_teams(seasons_teams, conn, target_table, primary_key)

    sys.stdout.write('\n')

    return Colour.green + f'Table {target_table} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time)) \
           + ' seconds taken' + Colour.end

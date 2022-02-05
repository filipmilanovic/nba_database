from data import *


def get_players_data():
    """ get data for the season """
    generate_players_json()
    data = player_generator.response['resultSets'][0]

    deduplicated_data = check_db_duplicates(data, True, 'PERSON_ID', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                            metadata, engine, connection)

    output = clean_players_data(deduplicated_data)

    return output


def generate_players_json():
    """ get all player data for a given season """
    parameters_players = get_request_parameters()
    player_generator.send_request(parameters_players)


def get_request_parameters():
    """ generate the parameters for the request """
    output = {'Historical': 1,
              'LeagueID': '00',
              'Season': END_SEASON}

    return output


def clean_players_data(data_dict: dict):
    """ iterate through player information and clean """
    columns = data_dict['headers']
    rows = data_dict['rowSet']

    output = [get_player_dict(columns, row) for row in rows]

    return output


def get_player_dict(columns: list, data: list):
    """ take list of keys and values, then output cleaned dict"""
    player_info = dict(zip(columns, data))
    output = {'player_id': player_info['PERSON_ID'],
              'player_name': player_info['PLAYER_FIRST_NAME'] + ' ' + player_info['PLAYER_LAST_NAME'],
              'height': get_height(player_info['HEIGHT']),
              'weight': get_weight(player_info['WEIGHT']),
              'country': player_info['COUNTRY'],
              'college': player_info['COLLEGE'],
              'position': player_info['POSITION'],
              'latest_team_id': player_info['TEAM_ID']}

    return output


def get_height(height: str):
    """ convert height from ft-inch to cm"""
    try:
        inches = int(re.search(r'(\d)-', height).group(1))*12 + int(re.search(r'-(\d+)', height).group(1))
        output = int(inches*2.54)
    except TypeError:
        output = None

    return output


def get_weight(weight: int):
    """ convert weight from lbs to kgs """
    try:
        output = int(int(weight)/2.205)
    except (TypeError, ValueError):
        output = None

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_players(metadata)

    TARGET_TABLE = 'players'
    TABLE_PRIMARY_KEY = 'player_id'

    player_generator = NBAEndpoint(endpoint='playerindex')

    season_range = pd.Series(range(START_SEASON, END_SEASON + 1))

    players_data = get_players_data()

    write_data(engine, metadata, connection, players_data, TARGET_TABLE, TABLE_PRIMARY_KEY)

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

from data.scripts import *


def get_draft_data():
    """ get draft scripts """
    generate_playoffs_json()
    draft_info = get_draft_info(draft_generator.response)

    write_data(engine, metadata, connection, draft_info, TARGET_TABLE, TABLE_PRIMARY_KEY)


def generate_playoffs_json():
    """ generate json of draft picks """
    parameters = get_request_parameters()
    draft_generator.send_request(parameters)


def get_request_parameters():
    """ generate the parameters for the request """
    output = {'LeagueID': '00'}

    return output


def get_draft_info(json):
    """ create list of games dicts from json """
    data = json['resultSets'][0]

    columns = data['headers']
    rows = data['rowSet']

    draft_data = [dict(zip(columns, row)) for row in rows]
    draft_dict = [get_draft_dict(pick) for pick in draft_data
                  if (pick['OVERALL_PICK'] != 0)
                  and (pick['DRAFT_TYPE'] == 'Draft')]

    output = check_db_duplicates(draft_dict, False, 'draft_id', TARGET_TABLE, TABLE_PRIMARY_KEY,
                                 metadata, engine, connection)

    return output


def get_draft_dict(pick_dict: dict):
    """ convert raw scripts to a tidied dictionary """
    output = {'draft_id': str(pick_dict['PERSON_ID'] + (int(pick_dict['SEASON']) + 1) * 10000000),
              'player_id': pick_dict['PERSON_ID'],
              'season': int(pick_dict['SEASON']) + 1,
              'round_number': pick_dict['ROUND_NUMBER'],
              'round_pick': pick_dict['ROUND_PICK'],
              'overall_pick': pick_dict['OVERALL_PICK'],
              'team_id': pick_dict['TEAM_ID'],
              'previous_team': pick_dict['ORGANIZATION']
              }

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_draft(metadata)

    TARGET_TABLE = 'draft'
    TABLE_PRIMARY_KEY = 'draft_id'
    QUERY_PATH = f'{ROOT_PATH}/queries/scripts/{TARGET_TABLE}/'

    draft_generator = NBAEndpoint(endpoint='drafthistory')

    get_draft_data()

    query = get_query(QUERY_PATH, 'keep_latest_pick', 'sql')
    connection.execute(query)
    connection.execute('COMMIT')

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

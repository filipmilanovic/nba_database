from data import *


def all_play_data():
    """ get play data """
    for iteration in range(len(game_ids)):
    # for iteration in [0]:
        iteration_start_time = time.time()
        game_id = game_ids[iteration]
        # game_id = {'game_id': '0020000004'}
        generate_plays_json(game_id['game_id'])
        data = play_generator.response['resultSets'][0]

        game_plays = get_game_plays(data)

        status = write_data(engine, metadata, connection, game_plays, TARGET_TABLE, TABLE_PRIMARY_KEY)

        progress(iteration=iteration,
                 iterations=len(game_ids),
                 iteration_name=f'{game_id["game_id"]}',
                 lapsed=time_lapsed(),
                 sql_status=status)

        # sleep to avoid rate limits
        sleep_time = get_sleep_time(iteration_start_time, 1)

        time.sleep(sleep_time)


def generate_plays_json(game_id: str):
    """ generate json of draft picks """
    parameters = get_request_parameters(game_id)
    play_generator.send_request(parameters)


def get_request_parameters(game_id: str):
    """ generate the parameters for the request """
    output = {'GameID': game_id,
              'StartPeriod': 1,
              'EndPeriod': 10}

    return output


def get_game_plays(json):
    """ convert json to list of play dicts """
    columns = json['headers']
    rows = json['rowSet']

    play_list = [play for plays in [add_paired_events([dict(zip(columns, row))]) for row in rows] for play in plays]

    output = [get_clean_play(play_list[play], play_list[play-1], play) for play in range(len(play_list))]

    return output


def add_paired_events(play: list):
    """ convert paired events into two separate events (MISS + BLOCK, Turnover + STEAL, Double Foul) """
    play_dict = play[0]
    home_event = play_dict['HOMEDESCRIPTION']
    away_event = play_dict['VISITORDESCRIPTION']
    neutral_event = play_dict['NEUTRALDESCRIPTION']

    # there is only one home or away event
    if len([event for event in [home_event, away_event] if event]) == 1:
        # the 'secondary' event types are Assist
        if 'AST' in (home_event or away_event):
            output = get_assist_event(play_dict, home_event)
        else:
            output = play
    # there is only one neutral event
    elif neutral_event:
        # check for double fouls, note that home/away doesn't matter since relying on team_id for cleaning
        if 'Double' in neutral_event:
            output = get_double_foul_event(play_dict, neutral_event)
        else:
            output = play
    # otherwise there is both a home and an away event
    else:
        for team_event in [home_event, away_event]:
            output = get_paired_events(play_dict, team_event, home_event)
        exit()
    return output


def get_assist_event(play_dict: dict, home_event: str):
    if home_event:
        fix_team = 'home'
    else:
        fix_team = 'visitor'

    paired_event = clean_paired_event(play_dict, 'AST', fix_team, 'PLAYER2', 'PLAYER1')
    output = [play_dict, paired_event]

    return output


def get_double_foul_event(play_dict: dict, neutral_event: str):
    foul_type = re.search(r'Double (\w)', neutral_event).group(1)
    first_play = clean_paired_event(play_dict, f'{foul_type}.FOUL', 'neutral', 'PLAYER1', 'PLAYER2')
    second_play = clean_paired_event(play_dict, f'{foul_type}.FOUL', 'neutral', 'PLAYER2', 'PLAYER1')

    output = [first_play, second_play]

    return output


def get_paired_events(play_dict: dict, team_event: str, home_event: str):
    # print(team_event)
    # print(home_event)
    if team_event == home_event:
        fix_team = 'visitor'
    else:
        fix_team = 'home'
    print(play_dict)
    print(fix_team)
    # the 'secondary' event types are Blocks and Steals
    if 'BLOCK' in team_event:
        paired_event = clean_paired_event(play_dict, None, fix_team, 'PLAYER3', 'PLAYER1')
        output = [play_dict, paired_event]
        print(output)
    elif 'STEAL' in team_event:
        paired_event = clean_paired_event(play_dict, None, fix_team, 'PLAYER2', 'PLAYER1')
        output = [play_dict, paired_event]
    else:
        output = [play_dict]

    return output


def clean_paired_event(play_dict: dict, description, team: str, first_player: str, second_player: str):
    """ clean up description and player/team info for paired events """
    output = dict(play_dict)
    output[f'{team.upper()}DESCRIPTION'] = description

    output['PLAYER1_ID'] = play_dict[f'{first_player}_ID']
    output['PLAYER2_ID'] = play_dict[f'{second_player}_ID']
    output['PLAYER1_TEAM_ID'] = play_dict[f'{first_player}_TEAM_ID']
    output['PLAYER2_TEAM_ID'] = play_dict[f'{second_player}_TEAM_ID']

    return output


def get_clean_play(play: dict, previous_play: dict, play_number: int):
    event_info = get_event_info(play, previous_play)

    # check if latest information has been initialised then set as global variables
    if 'latest_game_id' not in globals():
        global latest_game_id
        latest_game_id = play['GAME_ID']

        global latest_score
        latest_score = '0 - 0'

    if play['GAME_ID'] != latest_game_id:
        latest_game_id = play['GAME_ID']
        latest_score = '0 - 0'
    elif play['SCORE']:
        latest_score = play['SCORE']

    team_id = play['PLAYER1_TEAM_ID'] or play['PLAYER1_ID']

    output = {'play_id': f"{play['GAME_ID']}{'{:04d}'.format(play_number)}",
              'game_id': play['GAME_ID'],
              'period': play['PERIOD'],
              'game_clock': play['PCTIMESTRING'],
              'score': latest_score,
              'team_id': none_zero.get(team_id, team_id),
              'player_id': play['PLAYER1_ID'] if play['PLAYER1_TEAM_ID'] is not None else None,
              'event_name': event_info['name'],
              'event_value': event_info['value'],
              'event_detail': event_info['detail']
              }

    return output


def get_event_info(play_dict: dict, previous_play_dict: dict):
    play = play_dict['HOMEDESCRIPTION'] or play_dict['VISITORDESCRIPTION'] or play_dict['NEUTRALDESCRIPTION']
    output = {'name': '',
              'value': 0,
              'detail': ''}

    if 'PTS' in play:
        shot_info = get_shot_info(play)
        output = {'name': f'{shot_info["shot_type"]} Make',
                  'value': shot_info['shot_value'],
                  'detail': shot_info['shot_detail']}
    elif 'AST' in play:
        output = {'name': 'Assist',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'MISS' in play:
        shot_info = get_shot_info(play)
        output = {'name': f'{shot_info["shot_type"]} Miss',
                  'value': shot_info['shot_value'],
                  'detail': shot_info['shot_detail']}
    elif any(event in play for event in ['REBOUND', 'Rebound']):
        output = {'name': f'{get_rebound_type(play_dict, previous_play_dict)} Rebound',
                  'value': 1,
                  'detail': ''}
    elif 'Turnover' in play:
        output = {'name': 'Turnover',
                  'value': 1,
                  'detail': ''}
    elif any(event in play for event in ['FOUL', 'Foul']):
        output = {'name': f'{get_foul_type(play, play_dict)} Foul',
                  'value': 1,
                  'detail': ''}
    elif 'SUB' in play:
        output = {'name': 'Substitution',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'Timeout' in play:
        output = {'name': f'{get_timeout_type(play)} Timeout',
                  'value': 1,
                  'detail': ''}
    elif 'BLOCK' in play:
        output = {'name': 'Block',
                  'value': 1,
                  'detail': ''}
    elif 'STEAL' in play:
        output = {'name': 'Steal',
                  'value': 1,
                  'detail': ''}
    elif 'Violation' in play:
        output = {'name': f'{get_violation_type(play)}',
                  'value': 1,
                  'detail': ''}
    elif 'Start of' in play:
        output = {'name': 'Period Start',
                  'value': None,
                  'detail': ''}
    elif 'End of' in play:
        output = {'name': 'Period End',
                  'value': None,
                  'detail': ''}
    elif 'Jump Ball' in play:
        output = {'name': 'Jump Ball',
                  'value': 1,
                  'detail': ''}
    elif 'Ejection' in play:
        output = {'name': 'Ejection',
                  'value': None,
                  'detail': ''}

    return output


def get_shot_info(event: str):
    if 'Free Throw' in event:
        shot_type = 'FT'
        shot_value = 1
        shot_detail = ''
        # shot_detail = re.search(r'Free Throw (\d)', event).group(1)
    else:
        shot_type = 'FG'
        if '3PT' in event:
            shot_value = 3
        else:
            shot_value = 2
        shot_detail = ''

    output = {'shot_type': shot_type,
              'shot_value': shot_value,
              'shot_detail': shot_detail}

    return output


def get_rebound_type(play_dict: dict, previous_play_dict: dict):
    previous_play = previous_play_dict['HOMEDESCRIPTION']\
                    or previous_play_dict['VISITORDESCRIPTION']\
                    or previous_play_dict['NEUTRALDESCRIPTION']

    if 'MISS' in previous_play:
        if (play_dict['PLAYER1_TEAM_ID'] or play_dict['PLAYER1_ID']) == previous_play_dict['PLAYER1_TEAM_ID']:
            output = 'Offensive'
        else:
            output = 'Defensive'
    elif 'BLOCK' in previous_play:
        if (play_dict['PLAYER1_TEAM_ID'] or play_dict['PLAYER1_ID']) == previous_play_dict['PLAYER1_TEAM_ID']:
            output = 'Defensive'
        else:
            output = 'Offensive'
    else:
        # This is likely an error, but for simplicity, assume this is a misplaced offensive rebound on a tip-shot
        output = 'Offensive'

    return output


def get_foul_type(play: str, play_dict: dict):
    if 'Def. 3 Sec' in play:
        foul_key = 'D'
    elif play_dict['PLAYER1_ID'] >= 1610612700:
        foul_key = 'Team'
    else:
        foul_key = re.search(r'([A-Z.]+)\.(FOUL|Foul)', play).group(1)

    output = foul_types[foul_key]

    return output


def get_timeout_type(play: str):
    output = re.search(r'Timeout: (\w+)', play).group(1)

    return output


def get_violation_type(play: str):
    output = re.search(r'Violation:(.*)', play).group(1)

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(MYSQL_DATABASE)
    create_table_plays(engine, metadata)

    TARGET_TABLE = 'plays'
    TABLE_PRIMARY_KEY = 'play_id'
    # QUERY_PATH = f'{DATA_PATH}/queries/{TARGET_TABLE}/'

    play_generator = NBAEndpoint(endpoint='playbyplayv2')

    season_range = range(START_SEASON, END_SEASON + 1)

    games_query = get_column_query(metadata, engine, 'games', 'game_id', 'season', season_range)
    games_result = connection.execute(games_query)

    # extract game_ids as dict to enable standard checking of existing data in DB
    all_game_ids = [{'game_id': row[0]} for row in games_result]
    game_ids = check_db_duplicates(all_game_ids, False, 'game_id', TARGET_TABLE, 'game_id',
                                   metadata, engine, connection)

    all_play_data()

    # query = get_query(QUERY_PATH, 'keep_latest_pick', 'sql')
    # connection.execute(query)
    # connection.execute('COMMIT')

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

from data import *


def all_play_data():
    """ loop through game_ids, generating and cleaning data, then write """
    for iteration in range(len(game_ids)):
        iteration_start_time = time.time()
        game_id = game_ids[iteration]

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

    # each play is checked for a 'paired' event, which is then added as a subsequent play
    play_list = [play for plays in [add_paired_event([dict(zip(columns, row))]) for row in rows] for play in plays]

    output = [get_clean_play(play_list[play], play_list[play-1], play) for play in range(len(play_list))]

    return output


def add_paired_event(play: list):
    """ convert paired events into two separate events """
    play_dict = play[0]
    home_event = play_dict['HOMEDESCRIPTION']
    away_event = play_dict['VISITORDESCRIPTION']
    neutral_event = play_dict['NEUTRALDESCRIPTION']

    # there is only one home or away event
    if len([event for event in [home_event, away_event] if event]) == 1:
        # the 'secondary' event types are Assists
        if 'AST' in (home_event or away_event).upper():
            output = get_assist_event(play_dict, home_event)
        else:
            output = play
    # there is only one neutral event
    elif neutral_event:
        # the event types are Double Fouls
        if 'DOUBLE' in neutral_event.upper():
            output = get_double_foul_event(play_dict, neutral_event)
        else:
            output = play
    # there is both a home and an away event
    else:
        # ignore if bad data
        if not home_event and not away_event:
            output = []
        # the event types are block/miss and steal/turnover
        elif any(play_type in home_event.upper() for play_type in ['BLOCK', 'STEAL']):
            fix_team_1 = 'home'
            fix_team_2 = 'visitor'
            output = get_paired_events(play_dict, home_event, fix_team_1, fix_team_2)
        elif any(play_type in away_event.upper() for play_type in ['BLOCK', 'STEAL']):
            fix_team_1 = 'visitor'
            fix_team_2 = 'home'
            output = get_paired_events(play_dict, away_event, fix_team_1, fix_team_2)
        else:
            output = play

    return output


def get_assist_event(play_dict: dict, home_event: str):
    """ match a secondary assist event with the make event """
    if home_event:
        fix_team = 'home'
    else:
        fix_team = 'visitor'

    paired_event = clean_paired_event(play_dict, 'AST', fix_team, 'PLAYER2', 'PLAYER1')
    output = [play_dict, paired_event]

    return output


def get_double_foul_event(play_dict: dict, neutral_event: str):
    """ get both events from a double Foul """
    foul_type = re.search(r'DOUBLE[ .](\w)', neutral_event.upper()).group(1)
    first_play = clean_paired_event(play_dict, f'{foul_type}.FOUL', 'neutral', 'PLAYER1', 'PLAYER2')
    second_play = clean_paired_event(play_dict, f'{foul_type}.FOUL', 'neutral', 'PLAYER2', 'PLAYER1')

    output = [first_play, second_play]

    return output


def get_paired_events(play_dict: dict, team_event: str, fix_team_1: str, fix_team_2: str):
    """ get both paired events from Miss + Block and Turnover + Steal """
    if 'BLOCK' in team_event:
        first_event = clean_paired_event(play_dict, None, fix_team_1, 'PLAYER1', 'PLAYER3')
        second_event = clean_paired_event(play_dict, None, fix_team_2, 'PLAYER3', 'PLAYER1')
        output = [first_event, second_event]
    elif 'STEAL' in team_event:
        first_event = clean_paired_event(play_dict, None, fix_team_1, 'PLAYER1', 'PLAYER2')
        second_event = clean_paired_event(play_dict, None, fix_team_2, 'PLAYER2', 'PLAYER1')
        output = [first_event, second_event]
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
    """ convert raw play dict into a cleaned play dict """
    event_info = get_event_info(play, previous_play)

    # check if latest information has been initialised and set as global variables if not
    if 'latest_game_id' not in globals():
        global latest_game_id
        latest_game_id = play['GAME_ID']

        global latest_score
        latest_score = '0 - 0'

    # reset the game score where current play game_id has changed
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
              'event_detail': event_info['detail'],
              'possession': event_info.get('possession', 0)
              }

    return output


def get_event_info(play_dict: dict, previous_play_dict: dict):
    """ get row-level event information """
    play = play_dict['HOMEDESCRIPTION'] or play_dict['VISITORDESCRIPTION'] or play_dict['NEUTRALDESCRIPTION']
    output = {'name': '',
              'value': 0,
              'detail': ''}

    if 'PTS' in play:  # shot makes
        shot_info = get_shot_info(play, play_dict['EVENTMSGACTIONTYPE'])
        output = {'name': f'{shot_info["shot_type"]} Make',
                  'value': shot_info['shot_value'],
                  'detail': shot_info['shot_detail'],
                  'possession': shot_info['possession']}
    elif 'AST' in play:  # assists
        output = {'name': 'Assist',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'MISS' in play:  # shot misses
        shot_info = get_shot_info(play, play_dict['EVENTMSGACTIONTYPE'])  # EVENTMSGTYPE == 1
        output = {'name': f'{shot_info["shot_type"]} Miss',
                  'value': shot_info['shot_value'],
                  'detail': shot_info['shot_detail'],
                  'possession': shot_info['possession']}
    elif any(event in play for event in ['REBOUND', 'Rebound']):  # rebound
        rebound_info = get_rebound_info(play_dict, previous_play_dict)
        output = {'name': f'{rebound_info["event_type"]} Rebound',
                  'value': 1,
                  'detail': rebound_info['shooter']}
    elif 'Turnover' in play:  # turnovers
        output = {'name': 'Turnover',
                  'value': 1,
                  'detail': play_dict['EVENTMSGACTIONTYPE'],  # EVENTMSGTYPE == 5
                  'possession': 1}
    elif any(event in play for event in ['FOUL', 'Foul', 'Unsportsmanlike']):  # fouls
        output = {'name': 'Foul',
                  'value': 1,
                  'detail': f'{get_foul_type(play, play_dict)}'}
    elif 'SUB' in play:  # substitutions
        output = {'name': 'Substitution',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'Timeout' in play:  # timeouts
        output = {'name': 'Timeout',
                  'value': 1,
                  'detail': f'{get_timeout_type(play)}'}
    elif 'BLOCK' in play:  # blocks
        output = {'name': 'Block',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'STEAL' in play:  # steals
        output = {'name': 'Steal',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'Violation' in play:  # violations
        output = {'name': 'Violation',
                  'value': 1,
                  'detail': get_violation_type(play)}
    elif 'Start of' in play:  # period starts
        output = {'name': 'Period Start',
                  'value': None,
                  'detail': None}
    elif 'End of' in play:  # period ends
        output = {'name': 'Period End',
                  'value': None,
                  'detail': None}
    elif 'Jump Ball' in play:  # jump balls
        output = {'name': 'Jump Ball',
                  'value': 1,
                  'detail': play_dict['PLAYER2_ID']}
    elif 'Ejection' in play:  # ejections
        output = {'name': 'Ejection',
                  'value': None,
                  'detail': None}
    elif 'Taunting' in play:  # taunting technicals
        output = {'name': 'Taunting',
                  'value': None,
                  'detail': None}
    elif play in ['Short', 'Regular']:  # bugged timeouts in endpoint
        output = {'name': 'Timeout',
                  'value': 1,
                  'detail': play}

    return output


def get_shot_info(event: str, event_id: int):
    """ get the detail of a shot """
    if 'Free Throw' in event:
        shot_type = 'FT'
        shot_value = 1
        try:
            shot_detail = re.search(r'(\d) of (\d)', event).group(1)
            if re.search(r'(\d) of (\d)', event).group(1) == re.search(r'(\d) of (\d)', event).group(2):
                possession = 1
            else:
                possession = 0
        # (\d) of (\d) sometimes doesn't exist where there is only 1 technical free throw
        except AttributeError:
            shot_detail = 1
            possession = 0
    else:
        shot_type = 'FG'
        if '3PT' in event:
            shot_value = 3
        else:
            shot_value = 2
        shot_detail = event_id
        possession = 1

    output = {'shot_type': shot_type,
              'shot_value': shot_value,
              'shot_detail': shot_detail,
              'possession': possession}

    return output


def get_rebound_info(play_dict: dict, previous_play_dict: dict):
    """ get the detail of a rebound """
    previous_play = previous_play_dict['HOMEDESCRIPTION'] or previous_play_dict['VISITORDESCRIPTION'] or previous_play_dict['NEUTRALDESCRIPTION']

    if 'MISS' in previous_play:
        # TEAM_ID shows up as PLAYER_ID if it's a team rebound
        if (play_dict['PLAYER1_TEAM_ID'] or play_dict['PLAYER1_ID']) == previous_play_dict['PLAYER1_TEAM_ID']:
            event_type = 'Offensive'
        else:
            event_type = 'Defensive'
        shooter = previous_play_dict['PLAYER1_ID']
    elif 'BLOCK' in previous_play:
        if (play_dict['PLAYER1_TEAM_ID'] or play_dict['PLAYER1_ID']) == previous_play_dict['PLAYER1_TEAM_ID']:
            event_type = 'Defensive'
        else:
            event_type = 'Offensive'
        shooter = previous_play_dict['PLAYER2_ID']
    else:
        # This is likely an error, but for simplicity, assume this is a misplaced offensive rebound on a tip-shot
        event_type = 'Offensive'
        shooter = None

    output = {'event_type': event_type,
              'shooter': shooter}

    return output


def get_foul_type(event: str, play_dict: dict):
    """ get the detail of a foul """
    if 'Def. 3 Sec' in event:
        foul_key = 'D'
    elif play_dict['PLAYER1_ID'] >= 1610612700:
        foul_key = 'Team'
    else:
        if match := re.search(r'([A-Z.]+)\.(FOUL|Foul)', event):
            foul_key = match.group(1)
        elif match := re.search(r'Foul: *([A-z-]+)', event):
            foul_key = match.group(1)
        elif 'Non-Unsportsmanlike' in event:
            foul_key = 'Non-Unsportsmanlike'
        else:
            print(event)
            print('FOUL NOT VALID')
            foul_key = None
            exit()

    output = foul_types[foul_key]

    return output


def get_timeout_type(event: str):
    """ get the detail of a timeout """
    output = re.search(r'Timeout: *(\w+)', event).group(1).strip()

    return output


def get_violation_type(event: str):
    """ get the detail of a violation"""
    output = re.search(r'Violation: *(.*)', event).group(1).strip()

    return output


if __name__ == '__main__':
    engine, metadata, connection = get_connection(os.environ['MYSQL_DATABASE'])
    create_table_plays(engine, metadata)

    TARGET_TABLE = 'plays'
    TABLE_PRIMARY_KEY = 'play_id'

    play_generator = NBAEndpoint(endpoint='playbyplayv2')

    season_range = range(START_SEASON, END_SEASON + 1)

    games_query = get_column_query(metadata, engine, 'games', 'game_id', 'season', season_range)
    games_result = connection.execute(games_query)

    # extract game_ids as dict to enable standard checking of existing data in DB
    all_game_ids = [{'game_id': row[0]} for row in games_result]
    game_ids = check_db_duplicates(all_game_ids, False, 'game_id', TARGET_TABLE, 'game_id',
                                   metadata, engine, connection)

    all_play_data()

    sys.stdout.write('\n')

    print(Colour.green + f'Table {TARGET_TABLE} loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

# CLEAN RAW PLAYS DATA
from modelling.projects.nba import *  # import broadly used python packages
from modelling.projects.nba.utils import *  # import user defined utilities


# LOADING AND TIDYING OF RAW PLAYS TEXT
# get the plays for specified game
def get_raw_plays(plays_raw, games, game_id):
    home_team = games.loc[games['game_id'] == game_id, 'home_team'].item()
    away_team = games.loc[games['game_id'] == game_id, 'away_team'].item()

    # define global team_names to be used
    global team_names
    team_names = {'home_team': home_team, 'away_team': away_team}

    output = plays_raw.loc[plays_raw['game_id'] == game_id]

    # remove line breaks from strings
    output['plays'] = play_remove_line_break(output['plays'])

    # remove box score table headers
    output = output[~output['plays'].str.match(r'Time(.*)Score')].reset_index()

    # return time from strings then remove from raw plays
    output['time'] = get_time(output['plays'])
    output['plays'] = play_remove_time(output['plays'])

    # return home/away team using score positions in raw plays then remove
    output['teams'] = get_teams(output['plays'])
    output['plays'] = play_remove_score(output['plays'])
    output['plays'] = play_remove_score_added(output['plays'])

    # remove any loose whitespace
    output['plays'] = output['plays'].str.strip()

    log_performance()
    return output


# cleans line break from raw plays
def play_remove_line_break(x):
    output = x.str.replace(r'\n', '')

    log_performance()
    return output


# cleans out +d score from raw plays
def play_remove_score_added(x):
    output = x.str.replace(r'(\+[0-9])', '')

    log_performance()
    return output


# cleans out scoreboard from raw plays
def play_remove_score(x):
    output = x.str.replace(r'\d+-+\d+', '')

    log_performance()
    return output


# cleans out time remaining from raw plays
def play_remove_time(x):
    output = x.str.replace(r'\d+:\d+\.\d', '')

    log_performance()
    return output


# FILLING BASIC PLAY INFORMATION
# get play_id for key
def get_play_id(df):
    play_id = df.index.to_series().apply('{:0>4}'.format)
    output = df['game_id'].str.cat(play_id, sep='')
    return output


# get the period of the game based on the 'start of period' line
def get_quarter(play):
    period = re.search(r'Start of (.*)', play).group(1)
    if 'overtime' in period:
        output = 'OT' + str(left(period, 1))
    else:
        output = re.search(r'(.*) quarter', period).group(1)

    log_performance()
    return output


# get the time of the play
def get_time(series):
    output = series.str.extract(r'(\d+:\d+\.\d)', expand=False)
    output = output.str.replace(r'\.0', '')

    log_performance()
    return output


def get_score(df):
    home_points = (df.loc[df['event'].str.contains(' Make')
                          & (df['team_id'] == team_names['home_team']),
                          'event_value']).reindex(range(len(df))).fillna(0)
    home_cumulative = home_points.astype('int').cumsum().astype('str')

    away_points = (df.loc[df['event'].str.contains(' Make')
                          & (df['team_id'] == team_names['away_team']),
                          'event_value']).reindex(range(len(df))).fillna(0)
    away_cumulative = away_points.astype('int').cumsum().astype('str')

    output = home_cumulative.str.cat(away_cumulative, sep='-')

    log_performance()
    return output


# find team_id based on the location of the actual play to the score in the raw text line (away before, home after)
def get_teams(series):
    # find location of score in the strings
    scores = series.str.extract(r'(\d+-+\d+)', expand=False)
    score_location = pd.Series([series[i].find(str(scores[i])) for i in range(len(series))])

    # set mapping conditions
    conditions = [score_location == -1, score_location == 2]
    teams = [None, team_names['home_team']]

    # generate column of teams
    output = np.select(conditions, teams, default=team_names['away_team'])

    log_performance()
    return output


def get_team_id(row, reverse=False):
    # set as initial team_id
    output = row['teams']

    # in some cases (steals, blocks, some fouls), the play appears on the 'wrong' side
    if reverse:
        output = list(team_names.values())[team_names['home_team'] == output]

    log_performance()
    return output


# GET EVENT_DETAIL FOR SHOTS
# get the amount of points a shot was worth
def get_shot_value(play):
    if 'free throw' in play:
        # FTs worth 1 point
        output = 1
    elif match := re.search(r'(\d)-pt', play):
        # FGs worth amount given in play
        output = match.group(1)
    else:
        output = None

    log_performance()
    return output


# get distance of shot, or which free throw it was
def get_shot_detail(play):
    if match := re.search(r'free throw (\d)', play):
        # get which number in sequence of FTs
        output = match.group(1)
    elif 'technical' in play:
        # get if technical FT
        output = 1
    elif match := re.search(r'(\d+) ft', play):
        # get distance of shot if FG
        output = match.group(1)
    else:
        output = 0

    log_performance()
    return output


# PRODUCE ROWS FOR EACH DIFFERENT TYPE OF EVENT
# Produce the 'Period Start' line in order to get the correct period
def get_period_start(row):
    play = row['plays']
    game_id = row['game_id']
    output = [None,  # play_id
              game_id,  # game_id,
              get_quarter(play),  # period
              row['time'],  # time
              None,  # score
              None,  # team_id
              None,  # player_id
              'Period Start',  # event
              None,  # event_value
              None,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# Produce the 'Period End' line in order to get the correct period end
def get_period_end(row):
    game_id = row['game_id']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              '0:00',  # time
              None,  # score
              None,  # team_id
              None,  # player_id
              'Period End',  # event
              None,  # event_value
              None,  # event_detail
              1  # possession
              ]

    log_performance()
    return output


# get data for a jump ball
def get_jump_ball_data(games_lineups, row):
    game_id = row['game_id']
    player_1 = row['player_1']
    player_2 = row['player_2']
    player_3 = row['player_3']
    # find team that controlled the tip
    try:
        winning_team_id = games_lineups.team_id[(games_lineups.game_id == game_id) &
                                                (games_lineups.player_id == player_3)].item()
    # very rare issue where jump ball ends out of bounds, just default to home team
    except ValueError:
        winning_team_id = get_team_id(row)
    # find which player from that team competed for the jump ball
    winning_team_players = games_lineups.player_id[(games_lineups.game_id == game_id) &
                                                   (games_lineups.team_id == winning_team_id) &
                                                   (games_lineups.player_id == player_1)]
    # if player_id found in winning team, then sat that player as player_id, then set other as event_detail
    if len(winning_team_players) > 0:
        winning_player_id = player_1
        losing_player_id = player_2
    else:
        winning_player_id = player_2
        losing_player_id = player_1
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              winning_team_id,  # team_id
              winning_player_id,  # player_id
              'Jump Ball',  # event
              1,  # event_value
              losing_player_id,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# get necessary data for a shot attempt
def get_shot_attempt_data(row, shot_type):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']

    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              str(shot_type) + ' Shot',  # event
              get_shot_value(play),  # event_value
              get_shot_detail(play),  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# get necessary data for a made shot
def get_shot_make_data(row, shot_type):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']

    # flag end of possession
    possession = 1
    # FT end of possession if the final shot of a sequence
    if shot_type == 'FT' and 'technical' not in row['plays']:
        sequence = re.search(r'(\d) of \d', play).group(1)
        ft_number = re.search(r'\d of (\d)', play).group(1)
        possession = possession * (sequence == ft_number)

    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              str(shot_type) + ' Make',  # event
              get_shot_value(play),  # event_value
              get_shot_detail(play),  # event_detail
              possession  # possession
              ]

    log_performance()
    return output


# get necessary data for a missed shot
def get_shot_miss_data(row, shot_type):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']

    # flag end of possession
    possession = 1
    # FT end of possession if the final shot of a sequence
    if shot_type == 'FT' and 'technical' not in row['plays']:
        sequence = re.search(r'(\d) of \d', play).group(1)
        ft_number = re.search(r'\d of (\d)', play).group(1)
        possession = possession * (sequence == ft_number)

    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              str(shot_type) + ' Miss',  # event
              get_shot_value(play),  # event_value
              get_shot_detail(play),  # event_detail
              possession  # possession
              ]

    log_performance()
    return output


# get which player assisted if there was a made shot
def get_assist_data(row):
    game_id = row['game_id']
    shooter_id = row['player_1']
    player_id = row['player_2']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              'Assist',  # event
              1,  # event_value
              shooter_id,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# get which player blocked a shot
def get_block_data(row):
    game_id = row['game_id']
    shooter_id = row['player_1']
    player_id = row['player_2']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row, True),  # team_id
              player_id,  # player_id
              'Block',  # event
              1,  # event_value
              shooter_id,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# combine all shot related information to produce detailed rows of data
def get_shot_data(row):
    play = row['plays']
    output = []
    # label FT or FG
    if 'free throw' in play:
        shot_type = 'FT'
    else:
        shot_type = 'FG'

    # get row for shot attempt
    shot = get_shot_attempt_data(row, shot_type)

    # get row for shot miss
    if ' misses' in play:
        miss = get_shot_miss_data(row, shot_type)
        output = [shot] + [miss]

        # get row for block if shot blocked
        if 'block by' in play:
            block = get_block_data(row)
            output = [shot] + [miss] + [block]

    # get row for shot make
    elif ' makes' in play:
        make = get_shot_make_data(row, shot_type)
        output = [shot] + [make]

        # get row for assist if applicable
        if 'assist by' in play:
            assist = get_assist_data(row)
            output = [shot] + [make] + [assist]

    log_performance()
    return output


# get who rebounded the ball, with whose shot they rebounded
def get_rebound_data(row, last_row, second_last_row):
    game_id = row['game_id']
    play = row['plays']
    last_play = last_row['plays']
    player_id = row['player_1']

    # there is a bug with rare missing shot info, or sub occurs after FT miss so the shooter isn't picked up
    if any(x in last_play for x in [' misses', 'block by']):
        shooter = last_row['player_1']
    elif any(x in second_last_row['plays'] for x in [' misses', 'block by']):
        shooter = second_last_row['player_1']
    else:
        shooter = None

    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              re.search(r'(.*) rebound', play).group(0),  # event
              1,  # event_value
              shooter,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


def get_turnover_data(row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    detail = if_none(re.search(r'\((.*);', play), re.search(r'\((.*)\)', play))
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              'Turnover',  # event
              1,  # event_value
              detail.group(1),  # event_detail
              1  # possession
              ]

    log_performance()
    return output


def get_steal_data(row):
    game_id = row['game_id']
    turnover_player_id = row['player_1']
    player_id = row['player_2']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row, True),  # team_id
              player_id,  # player_id
              'Steal',  # event
              1,  # event_value
              turnover_player_id,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


def get_foul_data(row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    fouled_player_id = row['player_2']

    # find foul types which should 'reverse' the team_id
    reversed_fouls = ['Away from play foul',
                      'Clear path foul',
                      'Def 3 sec tech foul',
                      'Double technical foul',
                      'Elbow foul',
                      'Flagrant foul',
                      'Hanging tech foul',
                      'Ill def tech foul',
                      'Inbound foul',
                      'Non unsport tech foul',
                      'Offensive charge foul',
                      'Personal foul',
                      'Personal block foul',
                      'Personal take foul',
                      'Shooting foul',
                      'Shooting block foul',
                      'Taunting technical foul']
    event = re.search(r'(.*) foul', play).group(0)
    reverse = any(x in event for x in reversed_fouls)

    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row, reverse),  # team_id
              player_id,  # player_id
              event,  # event
              1,  # event_value
              fouled_player_id,  # event_detail
              0  # possession
              ]

    log_performance()
    return output


def get_violation_data(row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              'Violation',  # event
              1,  # event_value
              re.search(r'\((.*)\)', play).group(1),  # event_detail
              0  # possession
              ]

    log_performance()
    return output


def get_substitution_data(row):
    game_id = row['game_id']
    player_id = row['player_1']
    sub_player_id = row['player_2']
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              player_id,  # player_id
              'Substitution',  # event
              1,  # event_value
              sub_player_id,  # event_detail
              0  # possession
              ]

    if sub_player_id is None:
        output = []

    log_performance()
    return output


def get_timeout_data(row):
    game_id = row['game_id']
    play = row['plays']
    detail = re.search(r'(20 second|full|Official|no) timeout', play).group(1)
    output = [None,  # play_id
              game_id,  # game_id,
              None,  # period
              row['time'],  # time
              None,  # score
              get_team_id(row),  # team_id
              None,  # player_id
              'Timeout',  # event
              1,  # event_value
              detail.capitalize(),  # event_detail
              0  # possession
              ]

    log_performance()
    return output


# iterate through plays to produce base event details
def clean_plays(cols, games_lineups, df):
    output = []
    for i in range(len(df)):
        play = df.loc[i, 'plays']
        row = df.loc[i]
        if 'Start of ' in play:
            output = output + [get_period_start(row)]
        elif 'End of ' in play:
            output = output + [get_period_end(row)]
        elif all(x in play for x in ['Jump ball', 'possession']):
            output = output + [get_jump_ball_data(games_lineups, row)]
        elif any(x in play for x in [' makes ', ' misses ']):
            output = output + get_shot_data(row)
        elif ' rebound ' in play:
            output = output + [get_rebound_data(row, df.loc[i-1], df.loc[i-2])]
        elif 'Turnover ' in play:
            output = output + [get_turnover_data(row)]
            if 'steal by' in play:
                output = output + [get_steal_data(row)]
        elif ' foul ' in play:
            output = output + [get_foul_data(row)]
        elif 'Violation' in play:
            output = output + [get_violation_data(row)]
        elif 'enters the game' in play:
            output = [i for i in output + [get_substitution_data(row)] if i]
        elif 'timeout' in play:
            output = output + [get_timeout_data(row)]

    output = pd.DataFrame(output, columns=cols)

    log_performance()
    return output


# any additional tidying goes here
def period_start_end_teams(df):
    # get list of teams
    teams = [i for i in set(df['team_id']) if i is not None]

    # get index of period start rows
    period_start = df.index[df['event'] == 'Period Start']

    # get data from next row
    for i in period_start:
        df.loc[i, 'team_id'] = df.loc[i+1, 'team_id']

    # get index of period end rows
    period_end = df.index[df.event == 'Period End']

    # get data from previous row
    for i in period_end:
        if df.loc[i-1, 'possession'] == 1 or df.loc[i-1, 'event'] == 'Assist':
            team_id = teams[teams != df.loc[i-1, 'team_id']]
        else:
            team_id = df.loc[i-1, 'team_id']
        df.loc[i, 'team_id'] = team_id

    log_performance()
    return df


def fix_jump_ball_order(df):
    """ if jump ball comes before period start, swap the rows """
    for i in df.index[df['event'] == 'Jump Ball']:
        if df.loc[i+1, 'event'] == 'Period Start':
            df, index = swap_rows(df, i, i+1, 'forward')

    return df


def fix_substitution_order(df):
    """ if player subs on at the same time as performing an action, put the sub before the play """
    # get all sub events and loop through
    sub_events = df.loc[df['event'] == 'Substitution']

    for row in sub_events.iterrows():
        # find current position of sub event
        i = df.index[(df['period'] == row[1]['period']) &
                     (df['time'] == row[1]['time']) &
                     (df['player_id'] == row[1]['player_id']) &
                     (df['event'] == 'Substitution')][0]

        # get relevant event details
        event_period = df.loc[i, 'period']
        event_time = df.loc[i, 'time']
        subbed_in = df.loc[i, 'player_id']
        subbed_out = df.loc[i, 'event_detail']

        # fix for events after player subs out
        events_out = df[(df['period'] == event_period) & (df['time'] == event_time) & (df.index > i)]

        # get all events involving the player after subbing out
        fix_table = events_out[((events_out['player_id'] == subbed_out) |
                                (events_out['event_detail'] == subbed_out)) &
                               ~events_out['event'].str.contains('foul')]

        # use latest play to fix if fixing forwards
        if not fix_table.empty:
            # if another event involves the player subbing back in, skip it
            fix_index = fix_table.index[(fix_table['player_id'] == subbed_out) &
                                        (fix_table['event'] == 'Substitution')]

            # set sub to after the latest event
            if fix_index.empty:
                df, i = swap_rows(df, i, fix_table.index[len(fix_table)-1], 'forward')
            else:
                pass

        # fix for events before player subbing in
        events_in = df[(df['period'] == event_period) & (df['time'] == event_time) & (df.index < i)]

        # get all events involving the player before subbing in
        fix_table = events_in[((events_in['player_id'] == subbed_in) |
                               (events_in['event_detail'] == subbed_in)) &
                              ~events_in['event'].str.contains('foul')]

        # use earliest play to fix if fixing backwards
        if not fix_table.empty:
            # if player was just subbed out, then set to play after
            fix_index = fix_table.index[(fix_table['event_detail'] == subbed_in) &
                                        (fix_table['event'] == 'Substitution')] + 1

            if fix_index.empty:
                # set sub to before the earliest event
                df, i = swap_rows(df, i, fix_table.index[0], 'back')
            else:
                pass

    return df


def fix_incorrect_team(df, lineups):
    """ if player-team combination doesn't make sense, drop it """
    # drop plays without a player
    df_players = df.dropna(axis=0, subset=['player_id'])

    # perform join to be able to find null roles, and reset index to keep matched to original
    drop_table = pd.merge(left=df_players,
                          right=lineups,
                          how='left',
                          on=['game_id', 'player_id', 'team_id']).set_index(df_players.index)

    # ignore substitutions as these often seem to be a BBall Ref issue, and do not seem to have negative impact
    drop_index = drop_table.index[(drop_table['role'].isnull()) &
                                  (drop_table['event'] != 'Substitution')]

    df = df[~df.index.isin(list(drop_index))].reset_index(drop=True)

    return df


def manual_period_fix(df, game_id):
    """ if a game has a non-standard bug, or missing information, manually update it """
    if game_id == '201311270DAL':
        # this game was missing a sub in the 4th
        index = df.index[(df['time'] == '5:49') & (df['event'] == 'Timeout')]
        row_to_add = [None, game_id, None, '5:49', None, 'DAL', 'blairde01', 'Substitution', 1, 'dalemsa01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201401010MIN':
        # this game was missing a sub in 4th
        index = df.index[(df['time'] == '7:34') & (df['player_id'] == 'rubiori01') & (df['event'] == 'Substitution')]
        row_to_add = [None, game_id, None, '7:34', None, 'MIN', 'martike02', 'Substitution', 1, 'shvedal01', 0]
        df = insert_row(df, index[0]+1, row_to_add)
    elif game_id == '201503150LAL':
        # this game was missing a sub in 4th
        index = df.index[(df['time'] == '6:41') & (df['event'] == 'Defensive rebound')]
        row_to_add = [None, game_id, None, '6:41', None, 'ATL', 'jenkijo01', 'Substitution', 1, 'bazemke01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201503160GSW':
        # this game was missing period start/end signifiers
        df.loc[(df['time'] == '11:42') & (df['event'] == 'FG Shot') & (df['event_detail'] == '2'), 'period'] = '2nd'
        df.loc[(df['time'] == '11:40') & (df['event'] == 'FG Shot') & (df['event_detail'] == '20'), 'period'] = '3rd'
        df.loc[(df['time'] == '12:00') & (df['event'] == 'FT Shot') & (df['event_detail'] == '2'), 'period'] = '4th'
    elif game_id == '201505050GSW':
        # this game was missing a sub in the 4th
        index = df.index[(df['time'] == '1:03') & (df['event'] == 'Timeout')]
        row_to_add = [None, game_id, None, '1:03', None, 'MEM', 'greenje02', 'Substitution', 1, 'conlemi01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201601030NYK':
        # this game was missing many subs in 2nd - will add them in reverse order
        # Horford for Taveres at 2:07
        index = df.index[(df['time'] == '2:07') & (df['event'] == 'FT Make') & (df['event_detail'] == '1')]
        row_to_add = [None, game_id, None, '2:07', None, 'ATL', 'horfoal01', 'Substitution', 1, 'tavarwa01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        # Porzingis for Williams at 3:07
        index = df.index[(df['time'] == '3:07') & (df['event'] == 'Shooting foul')]
        row_to_add = [None, game_id, None, '3:07', None, 'NYK', 'porzikr01', 'Substitution', 1, 'willide02', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        # multiple subs at 5:36 and one at 5:28 (consecutive subs)
        index = df.index[(df['time'] == '5:36') & (df['event'] == 'Timeout')]
        row_to_add = [None, game_id, None, '5:28', None, 'NYK', 'lopezro01', 'Substitution', 1, 'porzikr01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        row_to_add = [None, game_id, None, '5:36', None, 'ATL', 'tavarwa01', 'Substitution', 1, 'horfoal01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        row_to_add = [None, game_id, None, '5:36', None, 'NYK', 'caldejo01', 'Substitution', 1, 'grantje02', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        row_to_add = [None, game_id, None, '5:36', None, 'ATL', 'bazemke01', 'Substitution', 1, 'pattela01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        row_to_add = [None, game_id, None, '5:36', None, 'ATL', 'sefolth01', 'Substitution', 1, 'korveky01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        # Millsap for Scott at 7:10
        index = df.index[(df['time'] == '7:10') & (df['event'] == 'Substitution')]
        row_to_add = [None, game_id, None, '7:10', None, 'ATL', 'millspa01', 'Substitution', 1, 'scottmi01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        # two subs at 8:05
        index = df.index[(df['time'] == '8:05') & (df['event'] == 'Timeout')]
        row_to_add = [None, game_id, None, '8:05', None, 'NYK', 'afflaar01', 'Substitution', 1, 'thomala01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
        row_to_add = [None, game_id, None, '8:05', None, 'ATL', 'teaguje01', 'Substitution', 1, 'macksh01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201610300HOU':
        # subs in wrong order after period end, so moved them around
        move_from = df.index[(df['time'] == '0:00') & (df['player_id'] == 'poweldw01')]
        move_to = df.index[(df['time'] == '0:00') & (df['event'] == 'Timeout')]
        df, i = swap_rows(df, move_from[0], move_to[0], 'back')
    elif game_id == '201710250PHI':
        # this game had a false sub in the 4th
        index = df.index[(df['time'] == '5:20') & (df['player_id'] == 'hardeja01') & (df['event'] == 'Substitution')]
        df = df.drop(index.tolist()).reset_index(drop=True)
    elif game_id == '201710280MEM':
        # this game had two false subs in the 2nd
        index = df.index[((df['time'] == '7:48') & (df['player_id'] == 'hardeja01')
                         & (df['event_detail'] == 'capelca01')) |
                         ((df['time'] == '7:48') & (df['player_id'] == 'arizatr01')
                          & (df['event_detail'] == 'brownbo02'))]
        df = df.drop(index.tolist()).reset_index(drop=True)
    elif game_id == '201712230IND':
        # duplicate subs at the end
        index = df.index[(df['time'] == '0:00') & (df['player_id'] == 'holliro01')
                         & (df['event_detail'] == 'zellety01')]
        df = df.drop(index.tolist())
        index = df.index[(df['time'] == '0:00') & (df['player_id'] == 'harrijo01')
                         & (df['event_detail'] == 'allenja01')]
        df = df.drop(index.tolist()).reset_index(drop=True)
    elif game_id == '201801280HOU':
        # this game was missing a sub in 2nd
        index = df.index[(df['time'] == '12:00') & (df['event'] == 'FT Make')]
        row_to_add = [None, game_id, None, '11:59', None, 'PHO', 'jacksjo02', 'Substitution', 1, 'bookede01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201802090DET':
        # this game was missing a sub in 3rd
        index = df.index[(df['time'] == '12:00') & (df['event'] == 'FT Make')]
        row_to_add = [None, game_id, None, '11:59', None, 'DET', 'griffbl01', 'Substitution', 1, 'tollian01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '201803150DEN':
        # this game had a false sub in the 4th
        index = df.index[(df['time'] == '6:22') & (df['player_id'] == 'chandwi01') & (df['event'] == 'Substitution')]
        df = df.drop(index.tolist()).reset_index(drop=True)
    elif game_id == '201901280LAC':
        # this game was missing a sub in 3rd
        index = df.index[(df['time'] == '12:00') & (df['event'] == 'FT Make')]
        row_to_add = [None, game_id, None, '12:00', None, 'LAC', 'gilgesh01', 'Substitution', 1, 'willilo02', 0]
        df = insert_row(df, index[0] + 1, row_to_add)
    elif game_id == '202001040LAC':
        # this game was missing a sub in 3rd
        index = df.index[(df['time'] == '12:00') & (df['event'] == 'FT Make')]
        row_to_add = [None, game_id, None, '12:00', None, 'MEM', 'brookdi01', 'Substitution', 1, 'meltode01', 0]
        df = insert_row(df, index[0] + 1, row_to_add)

    return df


def write_game_plays(ns, queue):
    game_ids = ns.game_ids
    plays_raw = ns.plays_raw
    games = ns.games
    games_lineups = ns.games_lineups
    columns = ns.columns
    while not queue.empty():
        game_start = time.process_time()

        iteration = queue.get()

        # grab raw plays data for the given game_id from plays_raw table
        game_plays_raw = get_raw_plays(plays_raw, games, game_ids[iteration])

        # base tidying up of events, details, period start and time
        game_plays = clean_plays(columns, games_lineups, game_plays_raw).reset_index(drop=True)

        # check that Start of period comes before Jump ball
        game_plays = fix_jump_ball_order(game_plays)

        # set up manual fixes for games with bugs
        game_plays = manual_period_fix(game_plays, game_ids[iteration])

        # fill down period from start of period row
        game_plays['period'] = game_plays['period'].fillna(method='ffill').fillna('1st')

        # tidying up team_id for period start and end
        game_plays = period_start_end_teams(game_plays)

        # tidy substitution order
        game_plays = fix_substitution_order(game_plays)

        # check incorrect team situations
        game_plays = fix_incorrect_team(game_plays, games_lineups)

        # generate column of scores
        game_plays['score'] = get_score(game_plays)

        # get play_id
        game_plays['play_id'] = get_play_id(game_plays)

        cleaning_time = time.process_time() - game_start

        # write to DB and get status
        status = write_data(df=game_plays,
                            name='plays',
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        time_taken = 'Cleaned in ' + "{:.2f}".format(cleaning_time) + ' seconds, '\
                     'Total ' + time_lapsed()

        # show progress of loop
        progress(iteration=iteration,
                 iterations=len(game_ids),
                 iteration_name=game_ids[iteration],
                 lapsed=time_taken,
                 sql_status=status['sql'])

        write_performance()


def write_season_plays(queue):
    # set up processes
    processes = [Process(target=write_game_plays, name=f'Process-{i}', args=(name_space, queue,)) for i in range(8)]
    [proc.start() for proc in processes]
    [proc.join() for proc in processes]

    sys.stdout.write('\n')


def get_season_game_ids(season):
    games = name_space.games

    # set games to be cleaned
    game_ids = games.loc[games['season'] == season, 'game_id'].reset_index(drop=True)

    # if skipping already cleaned games, then check and exclude games already in plays table
    if SKIP_SCRAPED_GAMES:
        # get selectable object sql query to get already scraped plays
        selectable = get_column_query(metadata, engine, 'plays', 'game_id')
        skip_games = pd.read_sql(sql=selectable, con=connection)['game_id']

        # skip already scraped game_ids
        game_ids = game_ids[~game_ids.isin(skip_games)].reset_index(drop=True)
    else:
        # clear rows where play data already exists
        selectable = get_delete_query(metadata, engine, 'plays', 'game_id', game_ids)
        connection.execute(selectable)

    log_performance()
    return game_ids


def get_plays_raw_query(series):
    metadata_raw.reflect(bind=engine_raw)
    table = metadata_raw.tables['plays_raw']

    output = table.select().where(table.c.game_id.in_(series))

    log_performance()
    return output


def write_all_plays(series):
    # iterate through seasons
    for season in series:
        # share game_ids for the season across processes
        name_space.game_ids = get_season_game_ids(season)

        # load lineups to assist with assigning players to teams
        games_lineups_query = get_table_query(metadata, engine, 'games_lineups', 'game_id', name_space.game_ids)
        name_space.games_lineups = pd.read_sql(sql=games_lineups_query, con=engine)

        # get selectable object sql query to get raw plays for the season
        selectable = get_plays_raw_query(name_space.game_ids)

        # share seasons raw plays across processes
        name_space.plays_raw = pd.read_sql(sql=selectable, con=engine_raw)

        # create game_id queue
        q = manager.Queue()
        [q.put(i) for i in name_space.game_ids.index]

        if not q.empty():
            write_season_plays(q)

        print(f'Completed season {season}')


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    engine_raw, metadata_raw, connection_raw = get_connection(database_raw)
    create_table_plays(engine, metadata)

    # create manager for sharing data across processes
    manager = Manager()
    name_space = manager.Namespace()

    # generate base columns
    name_space.columns = ['play_id', 'game_id', 'period', 'time', 'score', 'team_id', 'player_id',
                          'event', 'event_value', 'event_detail', 'possession']

    # load games table to access game_ids
    name_space.games = load_data(df='games',
                                 sql_engine=engine,
                                 meta=metadata)

    # get seasons from games table to iterate
    seasons = pd.Series(range(start_season_games, end_season_games+1))

    write_all_plays(seasons)

    print(Colour.green + 'Plays Data Cleaned ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

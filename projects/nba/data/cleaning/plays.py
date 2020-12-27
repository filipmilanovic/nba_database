# CLEAN RAW PLAYS DATA
from modelling.projects.nba import *  # import all project specific utils


# get the plays for specified game
def get_raw_plays(game_id):
    output = plays_raw.loc[plays_raw.game_id == game_id].reset_index()
    return output


def play_remove_line_break(x):
    output = re.sub(r'\n', '', x)
    return output


def play_remove_score_added(x):
    output = re.sub(r'(\+[0-9])', '', x)
    return output


def play_remove_score(x):
    output = re.sub(r'\d+(-)+\d+', '', x)
    return output


def play_remove_time(x):
    output = re.sub(r'\d+:\d+\.\d', '', x)
    return output


# clean the raw play text to just show the play
def get_play(x):
    play_no_line_break = play_remove_line_break(x)
    play_no_score_added = play_remove_score_added(play_no_line_break)
    play_no_score = play_remove_score(play_no_score_added)
    play = play_remove_time(play_no_score)
    output = play.strip()
    return output


# get the quarter of the game based on the 'start of quarter' line
def get_quarter(x):
    play = get_play(x)
    quarter = re.search(r'Start of (.*)', play).group(1)
    if 'overtime' in quarter:
        output = 'OT' + str(left(quarter, 1))
    else:
        output = re.search(r'(.*) quarter', quarter).group(1)
    return output


# get the time of the play
def get_time(x):
    output = mid(x, 1, x.find('.') - 1)
    return output


def get_home_score(x):
    output = int(re.search('(\d+)-', x).group(1))
    return output


def get_away_score(x):
    output = int(re.search('-(\d+)', x).group(1))
    return output


def get_score(x):
    game_id = list(set(x.game_id))[0]
    home_team = games.home_team[games.game_id == game_id].item()
    away_team = games.away_team[games.game_id == game_id].item()
    output = []
    for i in range(len(x)):
        try:
            last_home_score = get_home_score(output[i-1])
            last_away_score = get_away_score(output[i-1])
        except IndexError:
            last_home_score = 0
            last_away_score = 0
        if ' Make' in x.event[i]:
            home_score = last_home_score + int(x.event_value[i]) * (x.team_id[i] == home_team) * 1
            away_score = last_away_score + int(x.event_value[i]) * (x.team_id[i] == away_team) * 1
            output.append(str(home_score) + '-' + str(away_score))
        else:
            output.append(str(last_home_score) + '-' + str(last_away_score))
    return output


# find team_id based on the location of the actual play to the score in the raw text line
def get_team_id(x, game_id, reverse=False):
    play_no_line_break = play_remove_line_break(x)
    play_no_score_added = play_remove_score_added(play_no_line_break)
    play_no_time = play_remove_time(play_no_score_added)
    play = play_no_time.strip()
    score = re.search(r'\d+(-)+\d+', play).group(0)
    if len(re.search(f'{score}(.*)', play).group(1)) > 1:
        output = games.home_team[games.game_id == game_id].item()
        # in some cases (steals, blocks, some fouls), the play appears on the 'wrong' side
        if reverse:
            output = games.away_team[games.game_id == game_id].item()
    else:
        output = games.away_team[games.game_id == game_id].item()
        if reverse:
            output = games.home_team[games.game_id == game_id].item()
    return output


# get the amount of points a shot was worth
def get_shot_value(x):
    if 'free throw' in x:
        output = 1
    elif match := re.search(r'(\d)-pt', x):
        output = match.group(1)
    else:
        output = None
    return output


# get distance of shot, or which free throw it was
def get_shot_detail(x):
    if match := re.search(r'free throw (\d)', x):
        output = match.group(1)
    elif 'technical' in x:
        output = 1
    elif match := re.search(r'(\d+) ft', x):
        output = match.group(1)
    else:
        output = 0
    return output


# Produce the 'start of quarter' line in order to get the correct quarter in (will be removed)
def get_quarter_start(x, game_id):
    play = x
    array = [game_id,  # game_id
             get_quarter(play),  # quarter
             get_time(play),  # time
             None,  # score
             None,  # team
             None,  # player
             None,  # event
             None,  # event_value
             None,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


# get data for a jump ball
def get_jump_ball_data(x, player_1, player_2, player_3, game_id):
    # find team that controlled the tip
    winning_team_id = games_lineups.team_id[(games_lineups.game_id == game_id) &
                                            (games_lineups.player_id == player_3)].item()
    # find which player from that team competed for the jump ball
    winning_team_players = games_lineups.player_id[(games_lineups.game_id == game_id) &
                                                   (games_lineups.team_id == winning_team_id) &
                                                   (games_lineups.player_id == player_1)]
    if len(winning_team_players) > 0:
        winning_player_id = player_1
        losing_player_id = player_2
    else:
        winning_player_id = player_2
        losing_player_id = player_1
    play = x
    array = [game_id,  # game_id
             None,  # quarter
             get_time(play),  # time
             None,  # score
             winning_team_id,  # team
             winning_player_id,  # player_id
             'Jump Ball',  # event
             1,  # event_value
             losing_player_id,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


# get necessary data for a shot attempt
def get_shot_attempt_data(x, shot_type, player_id, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             str(shot_type) + ' Shot',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get necessary data for a made shot
def get_shot_make_data(x, shot_type, player_id, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             str(shot_type) + ' Make',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get necessary data for a missed shot
def get_shot_miss_data(x, shot_type, player_id, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             str(shot_type) + ' Miss',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get which player assisted if there was a made shot
def get_assist_data(x, shooter_id, player_id, game_id):
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             'Assist',  # event
             1,  # event_value
             shooter_id,  # event_detail
             None  # possession
             ]
    output = array
    return output


# get which player blocked a shot
def get_block_data(x, shooter_id, player_id, game_id):
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id, True),  # team_id
             player_id,  # player_id
             'Block',  # event
             1,  # event_value
             shooter_id,  # event_detail
             None  # possession
             ]
    output = array
    return output


# combine all shot related information to produce detailed rows of data
def get_shot_data(x, shooter_id, other_player_id, game_id):
    arrays = []
    if 'free throw' in x:
        shot_type = 'FT'
    else:
        shot_type = 'FG'
    shot = get_shot_attempt_data(x, shot_type, shooter_id, game_id)
    if ' misses' in x:
        miss = get_shot_miss_data(x, shot_type, shooter_id, game_id)
        arrays = [shot, miss]
        if 'block by' in x:
            block = get_block_data(x, shooter_id, other_player_id, game_id)
            arrays = [shot, miss, block]
    elif ' makes' in x:
        make = get_shot_make_data(x, shot_type, shooter_id, game_id)
        arrays = [shot, make]
        if 'assist by' in x:
            assist = get_assist_data(x, shooter_id, other_player_id, game_id)
            arrays = [shot, make, assist]
    output = pd.DataFrame(arrays, columns=columns)
    return output


# get who rebounded the ball, with whose shot they rebounded
def get_rebound_data(x, y, player_id, game_id):
    shooter = None
    play = get_play(x)
    # there is a bug with rare missing shot info, or sub occurs after FT miss so the shooter isn't picked up
    if y.event.item() is None:
        shooter = None
    elif 'Miss' in y.event.item():
        shooter = y.player_id.item()
    elif 'Block' in y.event.item():
        shooter = y.event_detail.item()
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             re.search(r'(.*) rebound', play).group(0),  # event
             1,  # event_value
             shooter,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_turnover_data(x, player_id, game_id):
    play = get_play(x)
    detail = if_none(re.search(r'\((.*);', play), re.search(r'\((.*)\)', play))
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             'Turnover',  # event
             1,  # event_value
             detail.group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_steal_data(x, turnover_player_id, player_id, game_id):
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id, True),  # team_id
             player_id,  # player_id
             'Steal',  # event
             1,  # event_value
             turnover_player_id,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_foul_data(x, player_id, fouled_player_id, game_id):
    play = get_play(x)

    # find foul types which should 'reverse' the team_id
    reversed_fouls = ['Away from play foul',
                      'Clear path foul',
                      'Def 3 sec tech foul',
                      'Flagrant foul',
                      'Inbound foul',
                      'Offensive charge foul',
                      'Personal foul',
                      'Personal block foul',
                      'Personal take foul',
                      'Shooting foul',
                      'Shooting block foul']
    event = re.search(r'(.*) foul', play).group(0)
    reverse = any(x in event for x in reversed_fouls)

    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id, reverse),  # team_id
             player_id,  # player
             event,  # event
             1,  # event_value
             fouled_player_id,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_violation_data(x, player_id, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id,
             'Violation',  # event
             1,  # event_value
             re.search(r'\((.*)\)', play).group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_substitution_data(x, player_id, sub_player_id, game_id):
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team_id
             player_id,  # player_id
             'Substitution',  # event
             1,  # event_value
             sub_player_id,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_timeout_data(x, game_id):
    play = get_play(x)
    detail = re.search(r'(20 second|full|Official) timeout', play).group(1)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             get_team_id(x, game_id),  # team
             None,  # player
             'Timeout',  # event
             1,  # event_value
             detail.capitalize(),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def clean_plays(df):
    output = pd.DataFrame(columns=columns)
    for i in range(len(df.plays)):
        game_id = df.game_id[i]
        if 'Start of ' in df.plays[i]:
            output = output.append(get_quarter_start(df.plays[i], game_id))
        elif all(x in df.plays[i] for x in ['Jump ball', 'possession']):
            output = output.append(get_jump_ball_data(df.plays[i], df.player_1[i], df.player_2[i], df.player_3[i],
                                                      game_id))
        elif any(x in df.plays[i] for x in [' makes ', ' misses ']):
            output = output.append(get_shot_data(df.plays[i], df.player_1[i], df.player_2[i], game_id))
        elif ' rebound ' in df.plays[i]:
            output = output.append(get_rebound_data(df.plays[i], output.tail(1), df.player_1[i], game_id))
        elif 'Turnover ' in df.plays[i]:
            output = output.append(get_turnover_data(df.plays[i], df.player_1[i], game_id))
            if 'steal by' in df.plays[i]:
                output = output.append(get_steal_data(df.plays[i], df.player_1[i], df.player_2[i], game_id))
        elif ' foul ' in df.plays[i]:
            output = output.append(get_foul_data(df.plays[i], df.player_1[i], df.player_2[i], game_id))
        elif 'Violation' in df.plays[i]:
            output = output.append(get_violation_data(df.plays[i], df.player_1[i], game_id))
        elif 'enters the game' in df.plays[i]:
            output = output.append(get_substitution_data(df.plays[i], df.player_1[i], df.player_2[i], game_id))
        elif 'timeout' in df.plays[i]:
            output = output.append(get_timeout_data(df.plays[i], game_id))
    output = output
    return output


def tidy_game_plays(x):
    x.quarter = x.quarter.fillna(method='ffill')
    x = x.dropna(axis=0, subset=['event']).reset_index(drop=True)
    x.score = get_score(x)
    return x


def get_game_plays(x):
    for i in range(len(x)):
        game_plays_raw = get_raw_plays(x[i])
        game_plays = clean_plays(game_plays_raw)
        output = tidy_game_plays(game_plays)

        # clear rows where game already exists
        try:
            connection_raw.execute(f'delete from nba.plays where game_id = "{x[i]}"')
        except ProgrammingError:
            pass

        status = write_data(df=output,
                            name='plays',
                            to_csv=False,
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(x),
                 iteration_name=x[i],
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])


if __name__ == '__main__':
    plays = load_data(df='plays',
                      sql_engine=engine,
                      meta=metadata)

    plays_raw = load_data(df='plays_raw',
                          sql_engine=engine_raw,
                          meta=metadata_raw)

    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    games_lineups = load_data(df='games_lineups',
                              sql_engine=engine,
                              meta=metadata)

    columns = ['game_id', 'quarter', 'time', 'score',  'team_id', 'player_id',
               'event', 'event_value', 'event_detail', 'possession']

    game_ids = games.game_id

    if SKIP_SCRAPED_DAYS:
        game_ids = games.game_id[~games.game_id.isin(plays.game_id)].reset_index(drop=True)

    get_game_plays(game_ids)

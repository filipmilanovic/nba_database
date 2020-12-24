# CLEAN RAW PLAYS DATA
from modelling.projects.nba import *  # import all project specific utils


def cleanup_unneeded_rows(df):
    # remove table header
    df = df[~(df.plays.str.contains('Time') & df.plays.str.contains('Score'))]

    # remove header for each quarter
    df = df[~df.plays.str.contains(' Q')]

    output = df.reset_index()
    return output


# get the plays for specified game
def get_raw_plays(game_id):
    df = plays_raw.loc[plays_raw.game_ref == game_id]
    output = cleanup_unneeded_rows(df)
    return output


# clean the raw play text to just show the play
def get_play(x):
    play_no_line_break = right(x, len(x) - (x.find('\n') + 1)).replace('Â ', '')
    play_no_add = re.sub(r'(\+[0-9])', '', play_no_line_break)
    play = re.sub(r'\d+(-)+\d+', '', play_no_add)
    output = right(play, len(play) - (play.find('\n') + 1))
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


# def get_score(x):
#     x = x.reset_index()
#     x[0] = '0-0'
#     for i in range(len(x)):
#

# def get_team(x):
#     play = get_play(x)


def get_player(x):
    play = get_play(x)


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
def get_jump_ball_data(x, game_id):
    play = x
    array = [game_id,  # game_id
             None,  # quarter
             get_time(play),  # time
             None,  # score
             None,  # team
             None,  # player
             'Jump Ball',  # event
             None,  # event_value
             None,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


# get necessary data for a shot attempt
def get_shot_attempt_data(x, shot_type, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             left(play, max(play.find(' makes'), play.find(' misses'))),  # player
             str(shot_type) + ' Shot',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get necessary data for a made shot
def get_shot_make_data(x, shot_type, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'(.*) makes', play).group(1),  # player
             str(shot_type) + ' Make',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get necessary data for a missed shot
def get_shot_miss_data(x, shot_type, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'(.*) misses', play).group(1),  # player
             str(shot_type) + ' Miss',  # event
             get_shot_value(play),  # event_value
             get_shot_detail(play),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get which player assisted if there was a made shot
def get_assist_data(x, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'assist by (.*)\)', play).group(1),  # player
             'Assist',  # event
             1,  # event_value
             re.search(r'(.*) makes', play).group(1),  # event_detail
             None  # possession
             ]
    output = array
    return output


# get which player blocked a shot
def get_block_data(x, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'block by (.*)\)', x).group(1),  # player
             'Block',  # event
             1,  # event_value
             re.search(r'(.*) misses', play).group(1),  # event_detail
             None  # possession
             ]
    output = array
    return output


# combine all shot related information to produce detailed rows of data
def get_shot_data(x, game_id):
    arrays = []
    if 'free throw' in x:
        shot_type = 'FT'
    else:
        shot_type = 'FG'
    shot = get_shot_attempt_data(x, shot_type, game_id)
    if ' misses' in x:
        miss = get_shot_miss_data(x, shot_type, game_id)
        arrays = [shot, miss]
        if 'block by' in x:
            block = get_block_data(x, game_id)
            arrays = [shot, miss, block]
    elif ' makes' in x:
        make = get_shot_make_data(x, shot_type, game_id)
        arrays = [shot, make]
        if 'assist by' in x:
            assist = get_assist_data(x, game_id)
            arrays = [shot, make, assist]
    output = pd.DataFrame(arrays, columns=columns)
    return output


# get who rebounded the ball, with whose shot they rebounded
def get_rebound_data(x, y, game_id):
    shooter = None
    play = get_play(x)
    if 'Miss' in y.event.item():
        shooter = y.player.item()
    elif 'Block' in y.event.item():
        shooter = y.event_detail.item()
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r' rebound by (.*)', play).group(1),  # player
             re.search(r'(.*) rebound', play).group(0),  # event
             1,  # event_value
             shooter,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_turnover_data(x, game_id):
    play = get_play(x)
    detail = if_none(re.search(r'\((.*);', play), re.search(r'\((.*)\)', play))
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'Turnover by (.*) \(', play).group(1),  # player
             'Turnover',  # event
             1,  # event_value
             detail.group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_steal_data(x, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'steal by (.*)\)', play).group(1),  # player
             'Steal',  # event
             1,  # event_value
             re.search(r'Turnover by (.*) \(', play).group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_foul_data(x, game_id):
    play = get_play(x)
    player = if_none(re.search(r' by (.*) \(', play), re.search(r' by (.*)', play))
    try:
        detail = re.search(r'drawn by (.*)\)', play).group(1)
    except AttributeError:
        detail = None
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             player.group(1),  # player
             re.search(r'(.*) foul', play).group(0),  # event
             1,  # event_value
             detail,  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output

# def get_time_left(series):
#     output = [mid(x, 1, x.find('.') - 1) for x in series]
#     return output


def get_violation_data(x, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'Violation by (.*) \(', play).group(1),  # player
             'Violation',  # event
             1,  # event_value
             re.search(r'\((.*)\)', play).group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


def get_substitution_data(x, game_id):
    play = get_play(x)
    array = [game_id,  # game_id
             None,  # quarter
             get_time(x),  # time
             None,  # score
             None,  # team
             re.search(r'(.*) enters the game for', play).group(1),  # player
             'Substitution',  # event
             1,  # event_value
             re.search(r'enters the game for (.*)', play).group(1),  # event_detail
             None  # possession
             ]
    output = pd.DataFrame([array], columns=columns)
    return output


# def get_timeout_data(x, game_id):
#     play = get_play(x)
#     array = [game_id,  # game_id
#              None,  # quarter
#              get_time(x),  # time
#              None,  # score
#              re.search(r'(.*) '),  # team
#              None,  # player
#              'Substitution',  # event
#              1,  # event_value
#              re.search(r'(.*) enters the game for', play).group(1),  # event_detail
#              None  # possession
#              ]
#     output = pd.DataFrame([array], columns=columns)
#     return output


def clean_plays(df):
    output = pd.DataFrame(columns=columns)
    for i in range(len(df.plays)):
        game_id = df.game_ref[i]
        if 'Start of ' in df.plays[i]:
            output = output.append(get_quarter_start(df.plays[i], game_id))
        elif 'Jump ball' in df.plays[i]:
            output = output.append(get_jump_ball_data(df.plays[i], game_id))
        elif ' makes ' in df.plays[i] or ' misses ' in df.plays[i]:
            output = output.append(get_shot_data(df.plays[i], game_id))
        elif ' rebound ' in df.plays[i]:
            output = output.append(get_rebound_data(df.plays[i], output.tail(1), game_id))
        elif 'Turnover ' in df.plays[i]:
            output = output.append(get_turnover_data(df.plays[i], game_id))
            if 'steal by' in df.plays[i]:
                output = output.append(get_steal_data(df.plays[i], game_id))
        elif ' foul ' in df.plays[i]:
            output = output.append(get_foul_data(df.plays[i], game_id))
        elif 'Violation' in df.plays[i]:
            output = output.append(get_violation_data(df.plays[i], game_id))
        elif 'enters the game' in df.plays[i]:
            output = output.append(get_substitution_data(df.plays[i], game_id))
        # elif 'timeout' in df.plays[i]:
        #     output = output.append(get_timeout_data(df.plays[i], game_id))
    return output


def tidy_game_plays(x):
    x.quarter = x.quarter.fillna(method='ffill')
    print(x)
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
    plays_raw = load_data(df='plays_raw',
                          sql_engine=engine_raw,
                          meta=metadata_raw)

    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    columns = ['game_id', 'quarter', 'time', 'score',  'team', 'player',
               'event', 'event_value', 'event_detail', 'possession']

    # get_game_plays(games.game_id)
    get_game_plays(['201710170CLE'])  # , '201710170GSW'])

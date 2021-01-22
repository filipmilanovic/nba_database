# CLEAN RAW PLAYS DATA
from modelling.projects.nba import *  # import all project specific utils


# LOADING AND TIDYING OF RAW PLAYS TEXT
# get the plays for specified game
def get_raw_plays(plays_raw, games, game_id):
    home_team = games.loc[games['game_id'] == game_id, 'home_team'].item()
    away_team = games.loc[games['game_id'] == game_id, 'away_team'].item()

    # define global team_names to be used
    global team_names
    team_names = {'home_team': home_team, 'away_team': away_team}

    output = plays_raw.loc[plays_raw.game_id == game_id]

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
def get_period_start(cols, row):
    play = row['plays']
    game_id = row['game_id']
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


# Produce the 'Period End' line in order to get the correct period end
def get_period_end(cols, row):
    game_id = row['game_id']
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


# get data for a jump ball
def get_jump_ball_data(cols, games_lineups, row):
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
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


# get necessary data for a shot attempt
def get_shot_attempt_data(row, shot_type):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']

    array = [None,  # play_id
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
    output = array

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

    array = [None,  # play_id
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
    output = array

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

    array = [None,  # play_id
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
    output = array

    log_performance()
    return output


# get which player assisted if there was a made shot
def get_assist_data(row):
    game_id = row['game_id']
    shooter_id = row['player_1']
    player_id = row['player_2']
    array = [None,  # play_id
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
    output = array

    log_performance()
    return output


# get which player blocked a shot
def get_block_data(row):
    game_id = row['game_id']
    shooter_id = row['player_1']
    player_id = row['player_2']
    array = [None,  # play_id
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
    output = array

    log_performance()
    return output


# combine all shot related information to produce detailed rows of data
def get_shot_data(cols, row):
    play = row['plays']
    arrays = []
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
        arrays = [shot, miss]

        # get row for block if shot blocked
        if 'block by' in play:
            block = get_block_data(row)
            arrays = [shot, miss, block]

    # get row for shot make
    elif ' makes' in play:
        make = get_shot_make_data(row, shot_type)
        arrays = [shot, make]

        # get row for assist if applicable
        if 'assist by' in play:
            assist = get_assist_data(row)
            arrays = [shot, make, assist]

    # create dataframe of given rows
    output = pd.DataFrame(arrays, columns=cols)

    log_performance()
    return output


# get who rebounded the ball, with whose shot they rebounded
def get_rebound_data(cols, row, y):
    game_id = row['game_id']
    shooter = None
    play = row['plays']
    player_id = row['player_1']
    # there is a bug with rare missing shot info, or sub occurs after FT miss so the shooter isn't picked up
    if y.event.item() is None:
        shooter = None
    elif 'Miss' in y.event.item():
        shooter = y.player_id.item()
    elif 'Block' in y.event.item():
        shooter = y.event_detail.item()
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_turnover_data(cols, row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    detail = if_none(re.search(r'\((.*);', play), re.search(r'\((.*)\)', play))
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_steal_data(cols, row):
    game_id = row['game_id']
    turnover_player_id = row['player_1']
    player_id = row['player_2']
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_foul_data(cols, row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    fouled_player_id = row['player_2']

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

    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_violation_data(cols, row):
    game_id = row['game_id']
    play = row['plays']
    player_id = row['player_1']
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_substitution_data(cols, row):
    game_id = row['game_id']
    player_id = row['player_1']
    sub_player_id = row['player_2']
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


def get_timeout_data(cols, row):
    game_id = row['game_id']
    play = row['plays']
    detail = re.search(r'(20 second|full|Official|no) timeout', play).group(1)
    array = [None,  # play_id
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
    output = pd.DataFrame([array], columns=cols)

    log_performance()
    return output


# iterate through plays to produce base event details
def clean_plays(cols, games_lineups, df):
    output = pd.DataFrame(columns=cols)
    for i in range(len(df)):
        play = df.loc[i, 'plays']
        row = df.loc[i]
        if 'Start of ' in play:
            output = output.append(get_period_start(cols, row))
        elif 'End of ' in play:
            output = output.append(get_period_end(cols, row))
        elif all(x in play for x in ['Jump ball', 'possession']):
            output = output.append(get_jump_ball_data(cols, games_lineups, row))
        elif any(x in play for x in [' makes ', ' misses ']):
            output = output.append(get_shot_data(cols, row))
        elif ' rebound ' in play:
            output = output.append(get_rebound_data(cols, row, output.tail(1)))
        elif 'Turnover ' in play:
            output = output.append(get_turnover_data(cols, row))
            if 'steal by' in play:
                output = output.append(get_steal_data(cols, row))
        elif ' foul ' in play:
            output = output.append(get_foul_data(cols, row))
        elif 'Violation' in play:
            output = output.append(get_violation_data(cols, row))
        elif 'enters the game' in play:
            output = output.append(get_substitution_data(cols, row))
        elif 'timeout' in play:
            output = output.append(get_timeout_data(cols, row))

    log_performance()
    return output


# any additional tidying goes here
def tidy_game_plays(df):
    # get list of teams
    teams = [i for i in set(df.team_id) if i is not None]

    # get index of period start rows
    period_start = df.index[df.event == 'Period Start']

    # get data from next row
    for i in period_start:
        df.loc[i, 'team_id'] = df.loc[i+1, 'team_id']

    # get index of period end rows
    period_end = df.index[df.event == 'Period End']

    # get data from previous row
    for i in period_end:
        if df.possession[i-1] == 1 or df.event[i-1] == 'Assist':
            team_id = teams[teams != df.team_id[i-1]]
        else:
            team_id = df.team_id[i-1]
        df.loc[i, 'team_id'] = team_id

    log_performance()
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

        # fill down period from start of period row
        game_plays['period'] = game_plays.period.fillna(method='ffill')

        # tidying up unnecessary information
        game_plays = tidy_game_plays(game_plays)

        # generate column of scores
        game_plays.score = get_score(game_plays)

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


def get_plays_query(series):
    ordered = series.sort_values().reset_index(drop=True)
    first_date = int(left(ordered[0], 8))
    last_date = int(left(ordered.values[-1], 8)) + 1

    metadata.reflect(bind=engine)
    table = metadata.tables['plays']

    output = table.select().where((func.left(table.c.play_id, 8) >= first_date)
                                  & (func.left(table.c.play_id, 8) <= last_date))

    log_performance()
    return output


def get_season_game_ids(season):
    games = name_space.games

    # set games to be cleaned
    output = games.loc[games['season'] == season, 'game_id'].reset_index(drop=True)

    # if skipping already cleaned games, then check and exclude games already in plays table
    if SKIP_SCRAPED_GAMES:
        # get selectable object sql query to get already scraped plays
        selectable = get_plays_query(output)

        # share seasons raw plays across processes
        plays = pd.read_sql(sql=selectable, con=engine)
        output = output[~output.isin(plays['game_id'])].reset_index(drop=True)
    else:
        clear_game_ids = "|".join(output)
        # clear rows in DB where game plays already exist
        try:
            connection.execute(f'delete from nba.plays where play_id regexp "{clear_game_ids}"')
        except ProgrammingError:
            pass

    log_performance()
    return output


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

        # get selectable object sql query to get raw plays for the season
        selectable = get_plays_raw_query(name_space.game_ids)

        # share seasons raw plays across processes
        name_space.plays_raw = pd.read_sql(sql=selectable, con=engine_raw)

        # create game_id queue
        q = manager.Queue()
        [q.put(i) for i in name_space.game_ids.index]

        write_season_plays(q)

        print(f'Completed season {season}')


if __name__ == '__main__':
    create_table_plays()

    manager = Manager()
    name_space = manager.Namespace()

    # generate base columns
    name_space.columns = ['play_id', 'game_id', 'period', 'time', 'score', 'team_id', 'player_id',
                          'event', 'event_value', 'event_detail', 'possession']

    # load games table to access game_ids
    name_space.games = load_data(df='games',
                                 sql_engine=engine,
                                 meta=metadata)

    # load lineups to assist with assigning players to teams
    name_space.games_lineups = load_data(df='games_lineups',
                                         sql_engine=engine,
                                         meta=metadata)

    # get seasons from games table to iterate
    seasons = list(set(name_space.games['season']))

    write_all_plays(seasons)

    print(Colour.green + 'Plays Data Cleaned' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

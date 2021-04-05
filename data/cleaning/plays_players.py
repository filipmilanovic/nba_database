# GET PLAYER_IDS ON THE COURT FOR EACH PLAY
from data import *


def get_box_key(team_id, period):
    """ define box score key """
    output = 'box-' + team_id + '-' + period.lower() + '-basic'

    return output


def get_box_score(game_id, team_id, period):
    """ get box score for period """
    # create box key then get table from url
    box_key = get_box_key(team_id, period)
    url = f'https://www.basketball-reference.com/boxscores/{game_id}.html'
    page = r.get(url)
    content = BeautifulSoup(page.content, 'lxml')
    output = content.find('table', {'id': box_key}).findChild('tbody')

    return output


def get_period_players(html):
    """ get all players who did not get substituted in period """
    output = [i.find('th').get('data-append-csv') for i in html.findAll('tr')
              if (i.find('td', {'data-stat': 'mp'})) and (i.find('td', {'data-stat': 'mp'}).text == '5:00')]

    return output


def get_seconds(i):
    """ convert time to seconds """
    try:
        time_played = dt.strptime(i, '%M:%S').time()
        output = time_played.minute * 60 + time_played.second
    except ValueError:
        # where time played >= 60:00
        fixed_string = str(int(left(i, 2))-60) + ':00'
        time_played = dt.strptime(fixed_string, '%M:%S').time()
        output = (time_played.minute+60) * 60 + time_played.second

    return output


def get_period_minutes(html, period):
    """ get all players who did not get substituted in period """
    refs = [i.find('th').find('a').get('href') for i in html.findAll('tr') if i.find('th').text != 'Reserves']
    players = [re.search(r'([a-z]+\d+).html', i).group(1) for i in refs]
    minutes_raw = [i.find('td', {'data-stat': 'mp'}) for i in html.findAll('tr') if i.find('th').text != 'Reserves']
    minutes = [{period: get_seconds(i.text)} if i else {period: 0} for i in minutes_raw]
    output = dict(zip(players, minutes))

    return output


def get_player_minutes(game_id, team_id, periods):
    """ get number of minutes each player played """
    player_minutes_list = []

    # get box score for each period
    for box_period in periods:
        box_score = get_box_score(game_id, team_id, box_period)
        player_minutes_list.append(get_period_minutes(box_score, box_period))

    output = {}

    # loop through player names and get each period minutes for that player
    for k in player_minutes_list[0].keys():
        output[k] = tuple(output[k] for output in player_minutes_list)

    return output


def get_periods(html):
    """ get list of periods in game """
    output = [i.text for i in html.find('div', {'class': 'filter switcher'}).findChildren('div')]

    return output


def get_page(game_id):
    """ get response from url """
    url = f'https://www.basketball-reference.com/boxscores/{game_id}.html'
    output = r.get(url)

    return output


def get_missing_players(players, game_id, team_id, period):
    """ find players in period and compare to original to find missing player """
    # get page content
    page = get_page(game_id)
    content = BeautifulSoup(page.content, 'lxml')

    # get periods
    periods = get_periods(content)
    game_periods = [i for i, x in enumerate(periods) if x not in ['Game', 'H1', 'H2', period_name[period]]]

    player_minutes = get_player_minutes(game_id, team_id, periods)

    period_players = []

    # get total game played in other periods, then compare difference to find missing players
    for i in player_minutes.keys():
        box_played = sum([player_minutes[i][j][periods[j]] for j in game_periods])
        total_played = player_minutes[i][0]['Game']

        if box_played + 60 <= total_played:
            period_players.append(i)

    # find all unique players for period
    all_players = list(set([inner for outer in players for inner in outer]))

    # find players that played in current period that weren't originally in list
    output = list(set(period_players) - set(all_players))

    return output


def play_players_check(players, game_id, team_id, period):
    """ check that there are exactly 5 players on the court, and fix if there are not """
    # check number of players for each play in period
    number_list = [e for e in set([len(i) for i in players]) if e != 5]

    if number_list:
        # fixes here
        # if too few players, likely because a player did nothing in a period, so get from box score
        if min(number_list) < 5:
            missing_players = get_missing_players(players, game_id, team_id, period)
            players = [i + missing_players for i in players]
            number_list = [e for e in set([len(i) for i in players])]

        # double check
        if min(number_list) < 5:
            sys.stdout.write('\n')
            print(Colour.red + f'Too few players for {team_id} in {period} of {game_id}' + Colour.end)
            exit()

        if max(number_list) > 5:
            sys.stdout.write('\n')
            print(Colour.red + f'Too many players for {team_id} in {period} of {game_id}' + Colour.end)
            exit()

    return players


def fill_players_down(players, events, subbed_in, subbed_out):
    """ if players missing, fill down based on players in previous play """
    players.reverse()
    events = events.iloc[::-1].reset_index(drop=True)
    subbed_out = subbed_out.iloc[::-1].reset_index(drop=True)
    subbed_in = subbed_in.iloc[::-1].reset_index(drop=True)

    incorrect_player = None
    remove_player = None
    true_on = None
    true_off = None
    false_on = None
    false_off = None

    # if period starts with 6 players, then there were likely false subs involved
    if len(players[0]) > 5:
        # find all players who did not do anything
        events_players = [i for i in subbed_in[events != 'Substitution'] if i]
        all_event_players = list(set(events_players))

        # find all unique players for period
        all_players = list(set([inner for outer in players for inner in outer]))

        try:
            incorrect_player = list(set(all_players) - set(all_event_players))[0]
            players[0].remove(incorrect_player)
        except (IndexError, ValueError):
            pass

    # find players in current play that weren't in previous play
    for i in range(1, len(players)):
        # remove player tagged as the false '6th man'
        if incorrect_player in players[i]:
            players[i].remove(incorrect_player)

        if events.loc[i] == 'Substitution':
            # if there's a substitution find who was substituted
            player_off = [subbed_out.loc[i]]
            player_on = [subbed_in.loc[i]]

            # in case of incorrect sub over multiple plays, remove true subbed in player
            if true_on in players[i]:
                players[i].remove(true_on)

            # if player designated as false sub is brought on properly, clear designation
            if player_on[0] == incorrect_player != false_off:
                players[i] = players[i] + [incorrect_player]
                incorrect_player = None

            # if subbed out player still in, designate to remove
            if player_off[0] in players[i]:
                remove_player = player_off[0]

            # THIS SECTION COVERS SUBS WHERE AN ALREADY OFF-COURT PLAYER WAS SUBBED OFF
            # if incorrect player was subbed off in play by play, this fixes it in the make-up sub
            if player_on[0] == false_off:
                # replace falsely taken off player with actually substituted player
                players[i] = [player.replace(false_off, true_on) for player in players[i]]

                # check if fixed, and append player if needed
                if true_on not in players[i]:
                    players[i].append(true_on)

                #  if the incorrect sub is explained by this bug, clear the removed player
                if false_off == remove_player:
                    remove_player = ''

                # clear incorrect subs bug fix variables
                false_off = None
                true_on = None

            # if subbed out player was already off, skip the sub, then note the players involved for check in next play
            if player_off[0] not in players[i-1]:
                if player_on[0] in players[i]:
                    players[i].remove(player_on[0])

                # this player was meant to remain on the court
                false_off = player_off[0]

                # this player is meant to come on and the make-up sub will fix this
                true_on = player_on[0]

            # THIS SECTION COVERS SUBS WHERE AN ALREADY ON-COURT PLAYER WAS SUBBED ON
            # if incorrect player was subbed on in play by play, this fixes it in the make-up sub
            if player_off[0] == false_on:
                # replace actually substituted player with falsely taken off player
                players[i] = [player.replace(true_off, false_on) for player in players[i]]

                # ensure this player is not re-added
                player_off = [true_off]

                #  if the incorrect sub is explained by this bug, clear the removed player
                if false_on == remove_player:
                    remove_player = ''

                # clear incorrect subs bug fix variables
                false_on = None
                true_off = None

            # if subbed in player was already on, skip the sub, then note the players involved for check in next play
            if player_on[0] in players[i-1]:
                # this player is taken off in the next play
                true_off = player_off[0]

                # this player was already on and the make-up sub comes after
                false_on = player_on[0]

                player_off = []

            # if player designated to remove subs back in, clear designation
            if subbed_in.iloc[i] == remove_player:
                remove_player = ''

            # find missing players from previous row, excluding subbed out player
            new_players = list(set(players[i-1]) - set(players[i]) - set(player_off))
        else:
            new_players = list(set(players[i-1]) - set(players[i]))

        # add on distinct new player
        players[i] = list(OrderedSet(players[i] + new_players))

        # remove any designated players, and clear designation if no longer on court
        if remove_player in players[i]:
            players[i].remove(remove_player)
        else:
            remove_player = ''

    return players


def manual_bug_fixes(players, df):
    if [df['game_id'], str(df['time']), df['player_id']] == ['200502230DEN', '12:00:00', 'boykiea01']:
        players.remove('boykiea01')

    return players


def check_manual_fix_game(game_id, period, team_id):
    if [game_id, period, team_id] in [['200502230DEN', '3rd', 'DEN']]:
        output = True
    else:
        output = False

    return output


def find_on_court_players(plays, game_id, team_id, period):
    """ go through play information to figure out which players are on the court """
    # ignore plays after period end, if it exists, as these can be incorrect and cause errors
    try:
        plays = plays[plays.index <= plays.index[plays['event'] == 'Period End'][0]]
    except IndexError:
        pass

    # reverse plays
    period_plays = plays.iloc[::-1]

    # get player_id, event and event_detail columns
    player_ids = period_plays['player_id']
    events = period_plays['event']
    event_details = period_plays['event_detail']

    # initialise players list
    players = [[i for i in [player_ids.iloc[0]] if i]]

    # get first player
    latest_players = [i for i in [player_ids.iloc[0]] if i]

    # designate if period needs manual bug fix
    fix_needed = check_manual_fix_game(game_id, period, team_id)

    for i in range(1, len(player_ids)):
        # get current play player_id (except fouls, to avoid potential bench players)
        if any(string in events.iloc[i].lower() for string in [' foul', 'technical']):
            player_id = None
        else:
            player_id = player_ids.iloc[i]

        # if previous play was a substitution, replace player who was brought on with player who was taken off
        if events.iloc[i-1] == 'Substitution':
            player_on = player_ids.iloc[i-1]
            player_off = event_details.iloc[i-1]

            latest_players = [player.replace(player_on, player_off) for player in latest_players]

        # get last play players and add new player_id if not already existing
        play_players = latest_players + [player_id] if player_id not in latest_players + [None] else latest_players

        # keep distinct
        play_players = list(OrderedSet(play_players))

        # append current player_ids to list of player_ids
        players.append(play_players)

        if fix_needed:
            play_players = manual_bug_fixes(play_players, period_plays.iloc[i])

        # update latest players
        latest_players = play_players

    players = fill_players_down(players, events, player_ids, event_details)

    # check data correctness
    players = play_players_check(players, game_id, team_id, period)

    # create key for players
    players = ["|".join(play) for play in players]

    output = pd.Series(players, index=plays.index)

    return output


def write_game_plays_players(ns, queue):
    """ loop through queue and set up relevant data, then write to DB """
    # get all the shared objects for the process
    game_ids = ns.game_ids
    columns = ns.columns
    plays = ns.plays
    games = ns.games

    while not queue.empty():
        game_start = time.process_time()

        # get game id from queue
        iteration = queue.get()
        game_id = game_ids[iteration]

        # get plays and teams for game
        game_plays = plays.loc[plays['game_id'] == game_id].reset_index(drop=True)
        team_ids = games.loc[games['game_id'] == game_id, ['home_team', 'away_team']]
        home_team = team_ids['home_team'].item()
        away_team = team_ids['away_team'].item()

        # initialise series'
        players = pd.Series(dtype='object')
        opp_players = pd.Series(dtype='object')

        # loop through periods
        for period in list(set(game_plays['period'])):
            # get each teams plays, then players for each team
            home_period_plays = game_plays.loc[(game_plays['period'] == period) & (game_plays['team_id'] == home_team)]
            home_players = find_on_court_players(home_period_plays, game_id, home_team, period)
            away_period_plays = game_plays.loc[(game_plays['period'] == period) & (game_plays['team_id'] == away_team)]
            away_players = find_on_court_players(away_period_plays, game_id, away_team, period)

            # get DataFrame index
            period_index = home_period_plays.index.tolist() + away_period_plays.index.tolist()

            # fill each series back and forward for complete list of players for ALL plays in period
            home_players = home_players.reindex(sorted(period_index)).fillna(method='ffill').fillna(method='bfill')
            away_players = away_players.reindex(sorted(period_index)).fillna(method='ffill').fillna(method='bfill')

            # convert the series' into team and opposition players
            period_players = pd.concat([home_players[home_period_plays.index],
                                        away_players[away_period_plays.index]])
            period_opp_players = pd.concat([home_players[away_period_plays.index],
                                            away_players[home_period_plays.index]])

            players = players.append(period_players)
            opp_players = opp_players.append(period_opp_players)

        # create DataFrame to write
        plays_players = pd.concat([game_plays['play_id'], game_plays['game_id'], players, opp_players], axis=1)
        plays_players.columns = columns

        cleaning_time = time.process_time() - game_start

        # write to DB and get status
        status = write_data(df=plays_players,
                            name='plays_players',
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        time_taken = 'Cleaned in ' + "{:.2f}".format(cleaning_time) + ' seconds, ' \
                                                                      'Total ' + time_lapsed()

        # show progress of loop
        progress(iteration=iteration,
                 iterations=len(game_ids),
                 iteration_name=game_ids[iteration],
                 lapsed=time_taken,
                 sql_status=status['sql'])


def write_season_plays_players(queue):
    """ define processes for the season """
    # set up processes
    processes = [Process(target=write_game_plays_players, name=f'Process-{i}', args=(name_space, queue,))
                 for i in range(8)]
    [proc.start() for proc in processes]
    [proc.join() for proc in processes]

    sys.stdout.write('\n')


def get_season_game_ids(season):
    """ get game_ids for the selected season """
    games = name_space.games

    # set games to be cleaned
    game_ids = games.loc[games['season'] == season, 'game_id'].reset_index(drop=True)

    # if skipping already cleaned games, then check and exclude games already in plays table
    if SKIP_SCRAPED_GAMES:
        # get selectable object sql query to get already scraped plays
        selectable = get_column_query(metadata, engine, 'plays_players', 'game_id')
        skip_games = pd.read_sql(sql=selectable, con=connection)['game_id']

        # skip already scraped game_ids
        game_ids = game_ids[~game_ids.isin(skip_games)].reset_index(drop=True)
    else:
        # clear rows where play data already exists
        selectable = get_delete_query(metadata, engine, 'plays_players', 'game_id', game_ids)
        connection.execute(selectable)

    return game_ids


def write_all_plays_players(series):
    """ get game_ids, then prepare the queue to pass """
    for season in series:
        # share game_ids for the season across processes
        name_space.game_ids = get_season_game_ids(season)

        # get selectable object sql query to get plays for the season
        selectable = get_table_query(metadata, engine, 'plays', 'game_id', name_space.game_ids)
        name_space.plays = pd.read_sql(sql=selectable, con=engine)

        # create game_id queue
        q = manager.Queue()
        [q.put(i) for i in name_space.game_ids.index]

        if not q.empty():
            write_season_plays_players(q)

        print(f'Completed season {season}')


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    create_table_plays_players(engine, metadata)

    # create manager for sharing data across processes
    manager = Manager()
    name_space = manager.Namespace()

    name_space.columns = ['play_id', 'game_id', 'players', 'opp_players']

    name_space.games = load_data(df='games',
                                 sql_engine=engine,
                                 meta=metadata)

    # get seasons from games table to iterate
    seasons = pd.Series(range(start_season_games, end_season_games+1))

    write_all_plays_players(seasons)

    print(Colour.green + 'Got on-court players ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

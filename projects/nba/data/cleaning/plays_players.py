# GET PLAYER_IDS ON THE COURT FOR EACH PLAY
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.utils import *
from modelling.projects.nba.data.scraping import *  # importing scraping for certain exceptions


def get_missing_players():
    print('missing')
    exit()


def play_players_check(players):
    # keep unique, and same ordered set
    output = list(OrderedSet(players))

    if len(players) > 5:
        # making assumption that any players beyond the 5th are mistakes, and that the mistake is not elsewhere
        output = output[0:5]
    elif len(players) < 5:
        get_missing_players()

    return output


def fill_players_down(players):
    players.reverse()
    # if players missing, fill down based on position in list
    for i in range(1, len(players)):
        number = len(players[i])

        players[i] = players[i] + players[i-1][number:5]

    return players


def find_on_court_players(plays):
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

    for i in range(1, len(player_ids)):
        # get current play player_id (except technical fouls, to avoid bench players)
        if events.iloc[i] == 'Technical foul':
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

        # check data correctness
        play_players = play_players_check(play_players)

        # append current player_ids to list of player_ids
        players.append(play_players)

        # update latest players
        latest_players = play_players

    players = fill_players_down(players)

    # create key for players
    players = ["|".join(play) for play in players]

    output = pd.Series(players, index=plays.index)

    return output


def write_game_plays_players(ns, queue):
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
            home_players = find_on_court_players(home_period_plays)
            away_period_plays = game_plays.loc[(game_plays['period'] == period) & (game_plays['team_id'] == away_team)]
            away_players = find_on_court_players(away_period_plays)

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

        write_performance()


def write_season_plays_players(queue):
    # set up processes
    processes = [Process(target=write_game_plays_players, name=f'Process-{i}', args=(name_space, queue,))
                 for i in range(1)]
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
        selectable = get_column_query(metadata, engine, 'plays_players', 'game_id')
        skip_games = pd.read_sql(sql=selectable, con=connection)['game_id']

        # skip already scraped game_ids
        game_ids = game_ids[~game_ids.isin(skip_games)].reset_index(drop=True)
    else:
        # clear rows where play data already exists
        selectable = get_delete_query(metadata, engine, 'plays_players', 'game_id', game_ids)
        connection.execute(selectable)

    log_performance()
    return game_ids


def write_all_plays_players(series):
    for season in [2020]:
        # share game_ids for the season across processes
        name_space.game_ids = get_season_game_ids(season)
        # name_space.game_ids = pd.Series('201911130BOS')

        # get selectable object sql query to get plays for the season
        selectable = get_table_query(metadata, engine, 'plays', 'game_id', name_space.game_ids)
        name_space.plays = pd.read_sql(sql=selectable, con=engine)

        # create game_id queue
        q = manager.Queue()
        [q.put(i) for i in name_space.game_ids.index]

        if not q.empty():
            write_season_plays_players(q)


if __name__ == '__main__':
    create_table_plays_players()

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

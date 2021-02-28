# SCRAPING PLAY BY PLAY DATA
from modelling.projects.nba import *  # import broadly used python packages
from modelling.projects.nba.utils import *  # import user defined utilities
from modelling.projects.nba.data import *  # import data specific packages


# generate list of 5 starters
def get_starters_roles():
    output = ['Starter'] * 5

    log_performance()
    return output


# generate list of bench players where not a starter and received minutes
def get_bench_roles(rows):
    players = rows[5:]
    bench = [i.findChild('th').get('data-append-csv') for i in players if i.findAll('td', {'data-stat': 'mp'})]
    output = ['Bench'] * len(bench)

    log_performance()
    return output


# generate list of dnp players where reason for not playing provided
def get_dnp_roles(rows):
    players = rows[5:]
    dnp = [i.findChild('th').get('data-append-csv') for i in players if i.findAll('td', {'data-stat': 'reason'})]
    output = ['DNP'] * len(dnp)

    log_performance()
    return output


# find box scores for each team, then combine player roles and write
def get_team_roles(html, team_id, game_id):
    # get box score
    box = html.find(id=f'box-{team_id}-game-basic').findChild('tbody')

    # return player rows where no class available (i.e. section header)
    players = [i for i in box.findChildren('tr') if i.get('class') is None]

    # get player ids from each row header
    player_ids = [i.findChild('th').get('data-append-csv') for i in players]

    # get lists of player roles and combine
    starters = get_starters_roles()
    bench = get_bench_roles(players)
    dnp = get_dnp_roles(players)
    roles = starters + bench + dnp

    # create dataframe for teams lineups
    output = pd.DataFrame([[game_id]*len(roles),
                           [team_id]*len(roles),
                           player_ids,
                           roles]).T

    output.columns = columns

    log_performance()
    return output


# get contents of page
def get_page_content(game_id, session):
    # get url
    url = f'https://www.basketball-reference.com/boxscores/{game_id}.html'

    page = session.get(url)
    output = BeautifulSoup(page.content, 'lxml')

    log_performance()
    return output


# get team names by home/away
def get_teams(game_id):
    output = games.loc[games['game_id'] == game_id, ['home_team', 'away_team']]

    log_performance()
    return output


# open session for each thread
def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = r.session()
    else:
        pass
    return thread_local.session


# get the team lineups then write
def write_lineup(iteration):
    # open session for thread
    session = get_session()

    # get game_id
    game_id = game_ids[iteration]

    # get page content
    soup = get_page_content(game_id, session)

    # get teams
    teams = get_teams(game_id)

    home_team = teams['home_team'].item()
    away_team = teams['away_team'].item()

    # get lineups for each team
    home_roles = get_team_roles(soup, home_team, game_id)
    away_roles = get_team_roles(soup, away_team, game_id)

    output = home_roles.append(away_roles)

    status = write_data(df=output,
                        name='games_lineups',
                        sql_engine=engine,
                        db_schema='nba',
                        if_exists='append',
                        index=False)

    progress(iteration=iteration,
             iterations=len(game_ids),
             iteration_name=game_id,
             lapsed=time_lapsed(),
             sql_status=status['sql'])

    log_performance()
    return output


def write_all_lineups():
    iterations = range(len(game_ids))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(write_lineup, iterations)
        executor.shutdown()


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    create_table_games_lineups(engine, metadata)

    # column names for plays_raw table
    columns = ['game_id', 'team_id', 'player_id', 'role']

    # load games table to help set up loop and to return team names
    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    # create game index for accessing website
    game_ids = games['game_id']

    # skip games that have already been scraped
    if SKIP_SCRAPED_GAMES:
        selectable = get_column_query(metadata, engine, 'games_lineups', 'game_id')
        skip_game_ids = pd.read_sql(sql=selectable, con=connection)['game_id']

        game_ids = game_ids[~game_ids.isin(skip_game_ids)].reset_index(drop=True)
    else:
        # clear rows where play data already exists
        selectable = get_delete_query(metadata, engine, 'games_lineups', 'game_id', game_ids)
        connection.execute(selectable)

    # defining threads
    thread_local = threading.local()

    # scrape all lineups and write them to the DB
    write_all_lineups()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Lineup Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

    write_performance()

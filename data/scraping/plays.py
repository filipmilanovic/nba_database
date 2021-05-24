# SCRAPING PLAY BY PLAY DATA
from data import *


# get the nth player_id from a play
def get_player_id(x, n):
    # get all rows
    row_elements = x.findChildren('td')

    # get all associated href elements (which include player_id in link)
    href_elements = [y.findChildren('a') for y in row_elements if y.findChildren('a')]

    # extract player_id if there is a href link
    try:
        url = [player[n].get('href') for player in href_elements]
        output = re.search(r'players/\w/(.*).html', url[0]).group(1)
    except (IndexError, AttributeError):
        output = None

    return output


# open session for each thread
def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = r.session()
    else:
        pass
    return thread_local.session


# get contents of page
def get_page_content(game_id, session):
    # get url
    url = f'https://www.basketball-reference.com/boxscores/pbp/{game_id}.html'

    page = session.get(url)
    output = BeautifulSoup(page.content, 'lxml')

    return output


# get play by play table from soup
def get_table_content(soup):
    output = soup.find('table', {'id': 'pbp'})

    return output


def get_raw_plays(soup):
    # raw plays
    plays = [x.getText() for x in soup.find_all('tr')]

    # scrape first player_id
    player_1 = [get_player_id(x, 0) for x in soup.find_all('tr')]

    # scrape second player_id
    player_2 = [get_player_id(x, 1) for x in soup.find_all('tr')]

    # scrape third player_id
    player_3 = [get_player_id(x, 2) for x in soup.find_all('tr')]

    output = list(zip(plays, player_1, player_2, player_3))

    return output


def write_raw_plays(iteration):
    # open session for thread
    session = get_session()

    # get game_id
    game_id = game_ids[iteration]

    # get page html for game
    soup = get_page_content(game_id, session)

    # get play by play table html from page
    table = get_table_content(soup)

    # scrape the raw plays and tidy the dataframe
    game_plays = get_raw_plays(table)
    game_plays = pd.DataFrame(game_plays, columns=['plays', 'player_1', 'player_2', 'player_3'])
    game_plays['game_id'] = game_id

    status = write_data(df=game_plays,
                        name='plays_raw',
                        sql_engine=engine_raw,
                        db_schema='nba_raw',
                        if_exists='append',
                        index=False)

    progress(iteration=iteration,
             iterations=len(game_ids),
             iteration_name=game_ids[iteration],
             lapsed=time_lapsed(),
             sql_status=status['sql'])


def write_all_raw_plays():
    iterations = range(len(game_ids))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(write_raw_plays, iterations)
        executor.shutdown()


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    engine_raw, metadata_raw, connection_raw = get_connection(database_raw)
    create_table_plays_raw(engine_raw, metadata_raw)

    # column names for plays_raw table
    columns = ['plays', 'player_1', 'player_2', 'player_3', 'game_id']

    # create game index for accessing website
    selectable = get_column_query(metadata, engine, 'games', 'game_id')
    game_ids = pd.read_sql(sql=selectable, con=connection)['game_id']

    # skip games that have already been scraped
    if SKIP_SCRAPED_GAMES:
        selectable = get_column_query(metadata_raw, engine_raw, 'plays_raw', 'game_id')
        skip_games = pd.read_sql(sql=selectable, con=connection_raw)['game_id']

        game_ids = game_ids[~game_ids.isin(skip_games)].reset_index(drop=True)
    else:
        # clear rows where play data already exists
        selectable = get_delete_query(metadata_raw, engine_raw, 'plays_raw', 'game_id', game_ids)
        connection_raw.execute(selectable)

    # defining threads
    thread_local = threading.local()

    # scrape all lineups and write them to the DB
    write_all_raw_plays()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

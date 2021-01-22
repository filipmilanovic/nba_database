# SCRAPING PLAYER DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_player_name(html):
    output = html.find('h1', {'itemprop': 'name'}).text.replace('\n', '')

    log_performance()
    return output


def get_player_dob(html):
    output = html.find('span', {'itemprop': 'birthDate'}).get('data-birth')

    log_performance()
    return output


def get_player_height(html):
    height = html.find('span', {'itemprop': 'height'}).text
    inches = int(left(height, 1))*12 + int(re.search(r'-(\d+)', height).group(1))
    output = int(inches*2.54)

    log_performance()
    return output


def get_player_weight(html):
    weight = html.find('span', {'itemprop': 'weight'}).text
    pounds = int(re.search(r'(\d+)lb', weight).group(1))
    output = int(pounds/2.205)

    log_performance()
    return output


def get_player_hand(html):
    # the line with position contains players shooting hand
    output = html.find('strong', text=re.compile(r'Shoots:')).next_sibling.strip()

    log_performance()
    return output


def get_player_position(html):
    raw = html.find('strong', text=re.compile(r'Position:')).next_sibling
    output = positions[raw.split()[0]]

    log_performance()
    return output


# need to add undrafted exception
def get_drafted_year(html):
    try:
        output = html.find('a', text=re.compile(r' NBA Draft')).text.split()[0]
    except AttributeError:
        output = None

    log_performance()
    return output


def get_draft_pick(html):
    try:
        raw = html.find('a', text=re.compile(r' NBA Draft')).previous_sibling
        output = re.search(r'pick, (\d+).*', raw).group(1)
    except AttributeError:
        output = None

    log_performance()
    return output


# need to add no debut exception
def get_rookie_year(html):
    try:
        raw = html.find('strong', text=re.compile(r'NBA Debut:')).next_sibling.get('href')
        game_id = re.search(r'/boxscores/(.*)\.html', raw).group(1)
        output = games.loc[games['game_id'] == game_id, 'season'].item()
    except ValueError:
        raw = html.find('strong', text=re.compile(r'NBA Debut:')).next_sibling.text
        debut = dt.strptime(raw, '%B %d, %Y')
        if debut.month > 6:
            output = debut.year + 1
        else:
            output = debut.year
    except AttributeError:
        output = None

    log_performance()
    return output


def get_player_url_list(series):
    initial = [left(i, 1) for i in series]
    output = [f'players/{initial[i]}/{series[i]}.html' for i in range(len(series))]

    print(Colour.green + 'Generated list of URLs' + Colour.end)

    log_performance()
    return output


# open session for each thread
def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = r.session()
    else:
        pass
    return thread_local.session


def get_page_content(url, session):
    page = session.get(url)
    output = BeautifulSoup(page.content, 'lxml')

    log_performance()
    return output


def get_player_info(soup):
    output = soup.find('div', {'itemtype': 'https://schema.org/Person'})

    log_performance()
    return output


def write_player_data(iteration):
    # open session for thread
    session = get_session()

    url = 'https://www.basketball-reference.com/' + url_list[iteration]

    page = get_page_content(url, session)

    player_info = get_player_info(page)

    player_id = player_list[iteration]
    player_name = get_player_name(player_info)
    dob = get_player_dob(player_info)
    height = get_player_height(player_info)
    weight = get_player_weight(player_info)
    hand = get_player_hand(player_info)
    position = get_player_position(player_info)
    draft_year = get_drafted_year(player_info)
    draft_pick = get_draft_pick(player_info)
    rookie_year = get_rookie_year(player_info)

    # build row for player, although currently possible exception where player has one name (e.g. Nene)
    player = [player_id,
              player_name,
              dob,
              height,
              weight,
              hand,
              position,
              draft_year,
              draft_pick,
              rookie_year]

    df = pd.DataFrame([player], columns=columns)

    status = write_data(df=df,
                        name='players',
                        sql_engine=engine,
                        db_schema='nba',
                        if_exists='append',
                        index=False)

    progress(iteration=iteration,
             iterations=len(url_list),
             iteration_name=player_name,
             lapsed=time_lapsed(),
             sql_status=status['sql'])


def write_all_players():
    iterations = range(len(url_list))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(write_player_data, iterations)
        executor.shutdown()


if __name__ == '__main__':
    create_table_players()

    columns = ['player_id', 'player_name', 'dob', 'height', 'weight', 'hand', 'position',
               'draft_year', 'draft_pick', 'rookie_year']

    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    games_lineups = load_data(df='games_lineups',
                              sql_engine=engine,
                              meta=metadata)

    # get list of players
    selectable = get_existing_query(metadata, engine, 'games_lineups', 'player_id')
    player_list = pd.read_sql(sql=selectable, con=connection)['player_id']

    if SKIP_SCRAPED_PLAYERS:
        selectable = get_existing_query(metadata, engine, 'players', 'player_id')
        skip_players = pd.read_sql(sql=selectable, con=connection)['player_id']

        player_list = pd.Series(player_list)[~pd.Series(player_list).isin(skip_players)].reset_index(drop=True)
    else:  # clear rows where play data already exists
        selectable = get_delete_query(metadata, engine, 'players', 'player_id', player_list)
        connection.execute(selectable)

    # get list of urls
    url_list = get_player_url_list(player_list)

    # defining threads
    thread_local = threading.local()

    # scrape all lineups and write them to the DB
    write_all_players()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Player Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

    write_performance()

# SCRAPING PLAYER DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_player_id(url):
    output = re.search('players/\w/(.*).html', url).group(1)

    log_performance()
    return output


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
    inches = int(left(height, 1))*12 + int(re.search('-(\d+)', height).group(1))
    output = int(inches*2.54)

    log_performance()
    return output


def get_player_weight(html):
    weight = html.find('span', {'itemprop': 'weight'}).text
    pounds = int(re.search('(\d+)lb', weight).group(1))
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


def get_player_list(df):
    output = list([])

    # loop through team/season combinations and build a list of URLs for each player
    for i in range(len(df)):
        team = df.team[i]
        season = df.season[i]
        url = f'https://www.basketball-reference.com/teams/{team}/{season}.html'
        team_list = get_player_url_list(url)
        output += team_list
        progress(iteration=i,
                 iterations=len(df),
                 iteration_name=f'{team} {season}',
                 lapsed=time_lapsed(),
                 sql_status='',
                 csv_status='')

    # make it a distinct list to save time
    output = pd.Series(sorted(list(set(output))))

    # skip players already in DB
    if SKIP_SCRAPED_PLAYERS:
        names = [re.search('players/[a-z]/(.*)\.html', x).group(1) for x in output]
        output = output[~pd.Series(names).isin(players.player_id)].reset_index(drop=True)

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Generated list of players' + Colour.end)

    log_performance()
    return output


def get_player_url_list(url):
    page = r.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    roster = soup.find(id='roster')
    output = [i.findChild('a').get('href') for i in roster.findAll('td', {"data-stat": "player"})]

    return output


def write_player_data(array):
    for i in range(len(array)):
        # driver.get(array[i])
        player_url = 'https://www.basketball-reference.com/' + array[i]
        player_page = r.get(player_url)
        soup = BeautifulSoup(player_page.content, 'html.parser')
        player_info = soup.find('div', {'itemtype': 'https://schema.org/Person'})

        player_id = get_player_id(array[i])
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

        try:
            connection_raw.execute(f'delete from nba.players where player_id = "{df.player_id.item()}"')
        except ProgrammingError:
            create_table_players()

        status = write_data(df=df,
                            name='players',
                            to_csv=False,
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(array),
                 iteration_name=df['player_name'].item(),
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Player Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)


if __name__ == '__main__':
    columns = ['player_id', 'player_name', 'dob', 'height', 'weight', 'hand', 'position',
               'draft_year', 'draft_pick', 'rookie_year']

    players = initialise_df(table_name='players',
                            columns=columns,
                            sql_engine=engine,
                            meta=metadata)

    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    # generate list of unique teams and seasons
    team_season = pd.DataFrame({'team': games.home_team, 'season': games.season}).drop_duplicates().reset_index()

    season_range = range(start_season_players, end_season_players)

    team_season = team_season[team_season['season'].isin(season_range)].reset_index(drop=True)

    # get list of players
    player_list = get_player_list(team_season)

    # write player data
    write_player_data(player_list)

    write_performance()

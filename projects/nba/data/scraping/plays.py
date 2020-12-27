# SCRAPING PLAY BY PLAY DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_game_id(df):
    short_date = pd.to_datetime(df.date).dt.strftime('%Y%m%d')
    short_name = [x for x in df.home_team]
    return short_date + '0' + short_name


def get_player_id(x, pos):
    row_elements = x.findChildren('td')
    href_elements = [y.findChildren('a') for y in row_elements if y.findChildren('a')]
    try:
        url = [player[pos].get('href') for player in href_elements]
        output = re.search('players/\w/(.*).html', url[0]).group(1)
    except (IndexError, AttributeError):
        output = None
    return output


def scrape_plays(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # raw plays
    plays = [x.getText().encode('utf-8') for x in soup.find_all('tr')
             if x.get('data-row') is not None]
    # scrape first player_id
    player_1 = [get_player_id(x, 0) for x in soup.find_all('tr')
                if x.get('data-row') is not None]
    # scrape second player_id
    player_2 = [get_player_id(x, 1) for x in soup.find_all('tr')
                if x.get('data-row') is not None]
    # scrape third player_id
    player_3 = [get_player_id(x, 2) for x in soup.find_all('tr')
                if x.get('data-row') is not None]
    output = list(zip(plays, player_1, player_2, player_3))
    return output


def get_plays_data(iterations):
    # selenium driver
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    for i in range(len(iterations)):
        # load website using index
        driver.get("https://www.basketball-reference.com/boxscores/pbp/" + iterations[i] + ".html")

        game_plays = scrape_plays(driver)

        game_plays = pd.DataFrame(game_plays, columns=['plays', 'player_1', 'player_2', 'player_3'])
        game_plays['game_id'] = iterations[i]

        # clear rows where play data already exists
        try:
            connection_raw.execute(f'delete from nba_raw.plays_raw where game_id = "{iterations[i]}"')
        except ProgrammingError:
            pass

        status = write_data(df=game_plays,
                            name='plays_raw',
                            to_csv=False,
                            sql_engine=engine_raw,
                            db_schema='nba_raw',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(iterations),
                 iteration_name=iterations[i],
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])

    # return to regular output writing
    sys.stdout.write('\n')

    driver.close()


if __name__ == '__main__':
    # column names for plays_raw table
    columns = ['plays', 'player_1', 'player_2', 'player_3', 'game_id']

    # get plays_raw dataframe from DB, or build from scratch
    plays_raw = initialise_df(table_name='plays_raw',
                              columns=columns,
                              sql_engine=engine_raw,
                              meta=metadata_raw)

    # load games table to help set up loop
    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    # pick up date range from parameters
    date_range = pd.date_range(start_date_plays, end_date_plays)

    # load games in selected date range
    games = games.loc[games.date.isin(date_range.strftime('%Y-%m-%d'))].reset_index(drop=True)

    # create game index for accessing website
    game_id = get_game_id(games)

    # skip games that have already been scraped
    if SKIP_SCRAPED_DAYS:
        game_id = game_id[~game_id.isin(plays_raw.game_id)].reset_index(drop=True)

    # get data and write to DB/CSV
    get_plays_data(game_id)

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

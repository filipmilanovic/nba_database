# SCRAPING PLAY BY PLAY DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_game_ref(df):
    short_date = pd.to_datetime(df.date).dt.strftime('%Y%m%d')
    short_name = [x for x in df.home_team]
    return short_date + '0' + short_name


def scrape_plays(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    df = [x.getText().encode('utf-8') for x in soup.find_all('tr')
          if x.get('data-row') is not None]
    return df


def get_plays_data(iterations):
    # selenium driver
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    for i in range(len(iterations)):
        # load website using index
        driver.get("https://www.basketball-reference.com/boxscores/pbp/" + iterations[i] + ".html")

        game_plays = scrape_plays(driver)

        game_plays = pd.DataFrame(game_plays, columns=['plays'])
        game_plays['game_ref'] = iterations[i]

        # clear rows where game already exists
        connection_raw.execute(f'delete from nba_raw.plays_raw where game_ref = "{iterations[i]}"')

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

    driver.close()


if __name__ == '__main__':
    # column names for plays_raw table
    columns = ['plays', 'game_ref']

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
    games = games.loc[games.date.isin(date_range.strftime('%Y-%m-%d'))]

    # create game index for accessing website
    game_ref = get_game_ref(games)

    # skip games that have already been scraped
    if SKIP_SCRAPED_DAYS:
        game_ref = game_ref[~game_ref.isin(plays_raw.game_ref)]

    # get data and write to DB/CSV
    get_plays_data(game_ref)

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

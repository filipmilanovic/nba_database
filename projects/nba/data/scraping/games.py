# SCRAPING GAME DATA
from modelling.projects.nba import *  # import broadly used python packages
from modelling.projects.nba.utils import *  # import user defined utilities
from modelling.projects.nba.data import *  # import data specific packages


# convert to standardised date format
def convert_date(x):
    output = dt.strptime(x, "%a, %b %d, %Y").strftime("%Y-%m-%d")

    log_performance()
    return output


# find header from each row and return game_id
def get_game_id(rows):
    output = [x.findChild('th').get('csk') for x in rows]

    log_performance()
    return output


# get date from row header and convert to standardised date
def get_game_date(rows):
    output = [convert_date(x.findChild('th').findChild('a').text) for x in rows]

    log_performance()
    return output


# return 'csk' item from the element of each row designated to home team name, then extract team_id
def get_home_team(rows):
    output = [re.search(r'([A-Z]+)\.', x[i].get('csk')).group(1) for x in rows for i in range(len(rows[0]))
              if x[i].get('data-stat') == 'home_team_name']

    log_performance()
    return output


# return text from the element of each row designated to home points
def get_home_score(rows):
    output = [x[i].text for x in rows for i in range(len(rows[0]))
              if x[i].get('data-stat') == 'home_pts']

    log_performance()
    return output


# return 'csk' item from the element of each row designated to away team name, then extract team_id
def get_away_team(rows):
    output = [re.search(r'([A-Z]+)\.', x[i].get('csk')).group(1) for x in rows for i in range(len(rows[0]))
              if x[i].get('data-stat') == 'visitor_team_name']

    log_performance()
    return output


# return text from the element of each row designated to visitor points
def get_away_score(rows):
    output = [x[i].text for x in rows for i in range(len(rows[0]))
              if x[i].get('data-stat') == 'visitor_pts']

    log_performance()
    return output


def scrape_season_games(driver, months, season):
    # initialise season dataframe
    output = pd.DataFrame(columns=columns)

    # set a default date for playoffs start, which will be updated later when we know the date
    playoff_date = dt.strptime(f'{season}-12-31', '%Y-%m-%d')

    for x in months:
        # initialise monthly dataframe
        monthly = pd.DataFrame(columns=columns)

        # set month for url (lower case, and 2020 includes two separate Octobers)
        month = x.lower().replace(' ', '-')

        # jump to month/season combination of games
        driver.get(f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html")
        time.sleep(0.5)

        # get schedule table
        schedule = driver.find_element_by_id('schedule')

        # get html text of schedule table, and return all rows
        soup = BeautifulSoup(schedule.get_attribute('innerHTML'), 'html.parser')
        table = soup.findChild('tbody').findChildren('tr')

        # get whole rows
        rows = [x for x in table if x.get('data-row') is not None and x.get('class') is None]

        # get row cells
        row_cells = [x.findChildren('td') for x in rows]

        # if playoffs happen in the month, update the playoff_date
        try:
            playoff = [i for i in range(len(table)) if table[i].text == 'Playoffs'][0]
            playoff_date = convert_date(table[playoff-1].findChild('th').findChild('a').text)
        except IndexError:
            pass

        # manually set playoff date for 2020 since it is not given by basketball reference
        if season == 2020:
            playoff_date = '2020-08-15'

        # get all data into monthly data_frame
        monthly['game_id'] = get_game_id(rows)
        monthly['game_date'] = get_game_date(rows)
        monthly['home_team'] = get_home_team(row_cells)
        monthly['home_score'] = get_home_score(row_cells)
        monthly['away_team'] = get_away_team(row_cells)
        monthly['away_score'] = get_away_score(row_cells)
        monthly['season'] = [season] * len(monthly)
        monthly['is_playoffs'] = (pd.to_datetime(monthly['game_date']) > playoff_date)*1

        output = output.append(monthly)

        log_performance()
    return output


def write_season_data(iteration):
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    # go to base game schedule for the season
    driver.get(f"https://www.basketball-reference.com/leagues/NBA_{season_range[iteration]}_games.html")

    # wait for page to load
    time.sleep(0.5)

    # get all the months for the season
    month_elements = driver.find_elements_by_xpath("//*[@class='filter']/div")
    months = [x.text for x in month_elements]

    # scrape the season data for all found months
    yearly = scrape_season_games(driver, months, season_range[iteration])

    status = write_data(df=yearly,
                        name='games',
                        sql_engine=engine,
                        db_schema='nba',
                        if_exists='append',
                        index=False)

    progress(iteration=iteration,
             iterations=len(season_range),
             iteration_name='Season ' + str(season_range[iteration]),
             lapsed=time_lapsed(),
             sql_status=status['sql'])

    driver.quit()


def write_all_games_data():
    iteration = list(range(len(season_range)))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(write_season_data, iteration)
        executor.shutdown()


if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)
    create_table_games(engine, metadata)

    # column names for games table
    columns = ['game_id', 'game_date', 'home_team', 'home_score', 'away_team', 'away_score', 'season', 'is_playoffs']

    # pick up date range from parameters
    season_range = pd.Series(range(start_season_games, end_season_games+1))

    if SKIP_SCRAPED_GAMES:
        # return seasons of existing games
        selectable = get_column_query(metadata, engine, 'games', 'season')
        skip_seasons = pd.read_sql(sql=selectable, con=connection)['season']

        # remove seasons from iterations where already exists
        season_range = season_range[~season_range.isin(skip_seasons)].reset_index(drop=True)
    else:
        # get query to remove data that is being re-scraped
        selectable = get_delete_query(metadata, engine, 'games', 'season', season_range)
        connection.execute(selectable)

    # defining threads
    thread_local = threading.local()

    # scrape all lineups and write them to the DB
    write_all_games_data()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

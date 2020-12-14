# SCRAPING GAME DATA

from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def game_index(game_date, name):
    short_date = pd.to_datetime(game_date).strftime('%Y%m%d')
    short_name = Team.team_ids[Team.short_names.index(name)]
    return short_date + '0' + short_name


def scrape_games(game_date, driver, df):
    # grab all game information and load into daily table
    hteams = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[1]/a")
    hscore = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[2]")
    ateams = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[1]/a")
    ascore = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[2]")
    # there is a loose game_summary on every page that returns an empty result
    for j in range(len(hteams)):
        df.loc[j, 'game_id'] = game_index(game_date.strftime('%Y-%m-%d'), hteams[j].text)
        df.loc[j, 'date'] = str(game_date.strftime('%Y-%m-%d'))
        df.loc[j, 'home_team'] = Team.team_ids[Team.short_names.index(hteams[j].text)]
        df.loc[j, 'home_score'] = hscore[j].text
        df.loc[j, 'away_team'] = Team.team_ids[Team.short_names.index(ateams[j].text)]
        df.loc[j, 'away_score'] = ascore[j].text


def get_games_data(dates):
    # selenium driver
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    for i in range(len(dates)):
        # clear out daily data frame and select next date
        daily = pd.DataFrame(columns=columns)

        # go to game scores for the day
        driver.get("https://www.basketball-reference.com/boxscores/?month=" + str(dates[i].strftime('%m'))
                   + '&day=' + str(dates[i].strftime('%d')) + '&year=' + str(dates[i].strftime('%Y')))

        # wait for page to load
        time.sleep(1)

        # scrape the daily data
        scrape_games(dates[i], driver, daily)

        # clear rows where game already exists
        try:
            connection_raw.execute(f'delete from nba.games where date = "{dates[i].date()}"')
        except sql.exc.ProgrammingError:
            pass

        status = write_data(df=daily,
                            name='games',
                            to_csv=False,
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(dates),
                 iteration_name=dates[i].strftime('%Y-%m-%d'),
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])

    # return to regular output writing
    sys.stdout.write('\n')

    # close web driver
    driver.close()

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)


if __name__ == '__main__':
    # column names for games table
    columns = ['game_id', 'date', 'home_team', 'home_score', 'away_team', 'away_score']

    # get games dataframe from DB, or build from scratch
    games = initialise_df(table_name='games',
                          columns=columns,
                          sql_engine=engine,
                          meta=metadata)

    # pick up date range from parameters
    date_range = pd.date_range(start_date_games, end_date_games)

    # skip or re-attempt already scraped days
    if SKIP_SCRAPED_DAYS:
        date_range = date_range[~date_range.isin(games.date)]

    # get data and write to DB/CSV
    get_games_data(date_range)

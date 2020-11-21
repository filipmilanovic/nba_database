# SCRAPING GAME DATA

from projects.nba import *  # import all project specific utils
from projects.nba.data.scraping import *


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
    for j in range(1, len(hteams)):
        df.loc[j, 'date'] = str(game_date.strftime('%Y-%m-%d'))
        df.loc[j, 'home_team'] = hteams[j].text
        df.loc[j, 'home_score'] = hscore[j].text
        df.loc[j, 'away_team'] = ateams[j].text
        df.loc[j, 'away_score'] = ascore[j].text


def get_games_data(df, dates):
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

        # append daily data to games, and remove any duplicates
        df = pd.concat([df, daily]).drop_duplicates().reset_index(drop=True)

        write_data(df=df,
                   name='games',
                   to_csv=True,
                   sql_engine=engine,
                   db_schema='nba',
                   if_exists='replace',
                   iteration=dates[i].strftime('%Y-%m-%d'))

    driver.close()

    print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)


if __name__ == '__main__':
    # column names for games table
    columns = ['date', 'home_team', 'home_score', 'away_team', 'away_score']

    # get games dataframe from DB, or build from scratch
    games = initialise_df(table_name='games',
                          columns=columns,
                          sql_engine=engine,
                          meta=metadata)

    # pick up date range from parameters
    date_range = pd.date_range(start_date_games, end_date_games)

    # skip already scraped days
    if SKIP_SCRAPED_DAYS:
        date_range = date_range[~date_range.isin(games.date)]

    # get data and write to DB/CSV
    get_games_data(games, date_range)

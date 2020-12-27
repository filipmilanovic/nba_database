# SCRAPING GAME DATA

from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def game_index(game_date, name):
    short_date = pd.to_datetime(game_date).strftime('%Y%m%d')
    return short_date + '0' + name


def get_daily_games(driver):
    output = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[1]/a")
    return output


def get_home_team(driver, i):
    home_team = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[1]/a")
    output = Team.team_ids[Team.short_names.index(home_team[i].text)]
    return output


def get_home_score(driver, i):
    home_score = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[2]")
    output = home_score[i].text
    return output


def get_away_team(driver, i):
    away_team = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[1]/a")
    output = Team.team_ids[Team.short_names.index(away_team[i].text)]
    return output


def get_away_score(driver, i):
    away_score = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[2]")
    output = away_score[i].text
    return output


def get_season(game_date):
    if game_date.month <= 6:
        output = game_date.year
    else:
        output = game_date.year + 1
    return output


def scrape_games(game_date, driver, df):
    daily_games = get_daily_games(driver)
    for i in range(len(daily_games)):
        df.loc[i, 'game_id'] = game_index(game_date.strftime('%Y-%m-%d'), get_home_team(driver, i))
        df.loc[i, 'date'] = str(game_date.strftime('%Y-%m-%d'))
        df.loc[i, 'home_team'] = get_home_team(driver, i)
        df.loc[i, 'home_score'] = get_home_score(driver, i)
        df.loc[i, 'away_team'] = get_away_team(driver, i)
        df.loc[i, 'away_score'] = get_away_score(driver, i)
        df.loc[i, 'season'] = get_season(game_date)


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
        except ProgrammingError:
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
    columns = ['game_id', 'date', 'home_team', 'home_score', 'away_team', 'away_score', 'season']

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

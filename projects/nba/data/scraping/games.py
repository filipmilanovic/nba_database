""" Scraping game data """
from projects.nba import *  # import all project specific utils
from selenium import webdriver  # used for interacting with webpages

# set up basic dataframe by loading from SQL or CSV if exists, or generating empty one
try:
    games = load_games()
    columns = games.columns.values
except (sql.exc.NoSuchTableError, sql.exc.OperationalError, NameError) as error:
    print(Colour.green + "Building table games from scratch" + Colour.end)
    columns = ['date', 'home_team', 'home_score', 'away_team', 'away_score']
    games = pd.DataFrame(columns=columns)

# pick up date range from parameters
date_range = pd.date_range(start_date_games, end_date_games)

if SKIP_SCRAPED_DAYS:
    date_range = date_range[~date_range.isin(games.date)]

# selenium driver
driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe")

for i in range(len(date_range)):
    # clear out daily data frame and select next date
    daily = pd.DataFrame(columns=columns)

    # go to game scores for the day
    driver.get("https://www.basketball-reference.com/boxscores/?month=" + str(date_range[i].strftime('%m'))
               + '&day=' + str(date_range[i].strftime('%d')) + '&year=' + str(date_range[i].strftime('%Y')))

    # wait for page to load
    time.sleep(1)

    # scrape the daily data
    scrape_games(date_range[i], driver, daily)

    # append daily data to games, and remove any duplicates
    games = pd.concat([games, daily]).drop_duplicates().reset_index(drop=True)

    # attempt to write to csv
    try:
        games.to_csv(str(p) + '/data/output/games.csv', sep=',')
        status_csv = Colour.green + 'Successfully written to csv!' + Colour.end
    except FileNotFoundError:
        status_csv = Colour.red + 'Failed to write to CSV! (Path does not exist)' + Colour.end
    except PermissionError:
        status_csv = Colour.red + 'Failed to write to CSV! (File already opened)' + Colour.end

    # attempt to write to sql
    try:
        games.to_sql('games', con=engine, schema='nba', if_exists='replace')
        status_sql = Colour.green + 'Successfully written to MySQL Database!' + Colour.end
    except sql.exc.OperationalError:
        status_sql = Colour.red + 'Failed to write to DB!' + Colour.end

    print(str(date_range[i].strftime('%Y-%m-%d')) + ' ' + status_csv + ' ' + status_sql + ' '
          + str('{0:.2f}'.format(time.time() - start_time)) + ' seconds so far')

driver.close()

print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

""" Scraping game data """
from projects.nba import *  # import all project specific utils
from projects.nba.utils import *  # importing of parameters and functions
from selenium import webdriver  # used for interacting with webpages

# pick up date range from parameters
date_range = pd.date_range(start_date_scrape, end_date_scrape)

# set up basic dataframe
columns = ['date', 'home_team', 'home_score', 'away_team', 'away_score']
game_data_raw = pd.DataFrame(columns=columns)

# selenium driver
driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe")

for i in range(len(date_range)):
    print('Date scraped: ' + str(date_range[i].strftime('%Y-%m-%d')) + ' '
          + str('{0:.2f}'.format(time.time() - start_time)) + ' seconds so far')

    # clear out daily data frame and select next date
    daily = pd.DataFrame(columns=columns)

    # go to game scores for the day
    driver.get("https://www.basketball-reference.com/boxscores/?month=" + str(date_range[i].strftime('%m'))
               + '&day=' + str(date_range[i].strftime('%d')) + '&year=' + str(date_range[i].strftime('%Y')))

    # wait for page to load
    time.sleep(1)

    # scrape the daily data
    scrape(date_range[i], driver, daily)

    # append daily data to table
    game_data_raw = game_data_raw.append(daily, ignore_index=True)

driver.close()

try:
    game_data_raw.to_csv(str(p)+'/data/output/game_data_raw.csv', sep=',')
    print(Colour.green + 'Successfully written to '
          + str(p) + '/data/output/game_data_raw.csv' + Colour.end)
except FileNotFoundError:
    print(Colour.red + 'Failed to write to CSV (Path does not exist)' + Colour.end)
except PermissionError:
    print(Colour.red + 'Failed to write to CSV (File already opened)' + Colour.end)

try:
    game_data_raw.to_sql('game_data_raw', con=engine, schema='nba', if_exists='replace')
    print(Colour.green + 'Successfully written to MySQL Database' + Colour.end)
except exc.OperationalError:
    print(Colour.red + 'Failed to write to DB' + Colour.end)
    pass

print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

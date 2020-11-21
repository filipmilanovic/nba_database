""" Scraping game data """
from projects.nba import *  # import all project specific utils
from selenium import webdriver  # used for interacting with webpages

games = load_games()
print(games)
# set up basic dataframe by loading from SQL if exists, or generating empty one
# try:
#     plays_raw = pd.read_sql(sql=sql.select([games_sql]), con=engine, index_col='index')
#     columns = plays_raw.columns.values
# except (sql.exc.NoSuchTableError, sql.exc.OperationalError, NameError) as error:
#     columns = ['date', 'home_team', 'home_score', 'away_team', 'away_score']
#     plays_raw = pd.DataFrame(columns=columns)

# pick up date range from parameters
date_range = pd.date_range(start_date_plays, end_date_plays)

if SKIP_SCRAPED_DAYS:
    date_range = date_range[~date_range.isin(plays_raw.date)]

# selenium driver
driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe")

driver.get("https://www.basketball-reference.com/boxscores/?month=" + str(date_range[0].strftime('%m'))
           + '&day=' + str(date_range[0].strftime('%d')) + '&year=' + str(date_range[0].strftime('%Y')))

# nbr_games = driver.find_element_by_xpath('//*[@id="content"]/div[2]/h2')
# print(left(nbr_games.text, 2)*1)

print(games)

driver.get("https://www.basketball-reference.com/boxscores/pbp/201810160GSW.html")

driver.find_elements_by_link_text('Play-By-Play')[0].url

# for i in range(len(date_range)):
#     # clear out daily data frame and select next date
#     daily = pd.DataFrame(columns=columns)
#
#     # go to game scores for the day
#     driver.get("https://www.basketball-reference.com/boxscores/?month=" + str(date_range[i].strftime('%m'))
#                + '&day=' + str(date_range[i].strftime('%d')) + '&year=' + str(date_range[i].strftime('%Y')))
#
#     # wait for page to load
#     time.sleep(1)
#
#     # scrape the daily data
#     scrape_games(date_range[i], driver, daily)
#
#     # append daily data to plays_raw, and remove any duplicates
#     plays_raw = pd.concat([plays_raw, daily]).drop_duplicates().reset_index(drop=True)
#
#     # attempt to write to csv
#     try:
#         plays_raw.to_csv(str(p) + '/data/output/plays_raw.csv', sep=',')
#         status_csv = Colour.green + 'Successfully written to csv!' + Colour.end
#     except FileNotFoundError:
#         status_csv = Colour.red + 'Failed to write to CSV! (Path does not exist)' + Colour.end
#     except PermissionError:
#         status_csv = Colour.red + 'Failed to write to CSV! (File already opened)' + Colour.end
#
#     # attempt to write to sql
#     try:
#         plays_raw.to_sql('plays_raw', con=engine, schema='nba', if_exists='replace')
#         status_sql = Colour.green + 'Successfully written to MySQL Database!' + Colour.end
#     except sql.exc.OperationalError:
#         status_sql = Colour.red + 'Failed to write to DB!' + Colour.end
#
#     print(str(date_range[i].strftime('%Y-%m-%d')) + ' ' + status_csv + ' ' + status_sql + ' '
#           + str('{0:.2f}'.format(time.time() - start_time)) + ' seconds so far')

# driver.close()

print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

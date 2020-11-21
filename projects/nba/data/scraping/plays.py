# SCRAPING PLAY BY PLAY DATA
from projects.nba import *  # import all project specific utils
from projects.nba.data.scraping import *

# pick up date range from parameters
date_range = pd.date_range(start_date_plays, end_date_plays)

# load other tables to help set up loop
games = load_data(df='games',
                  sql_engine=engine,
                  meta=metadata)
teams = load_teams()

# load games in selected date range
games = games.loc[games.date.isin(date_range.strftime('%Y-%m-%d'))]

# set up basic dataframe by loading from SQL if exists, or generating empty one
try:
    plays_raw = load_data(df='plays_raw',
                          sql_engine=engine_raw,
                          meta=metadata_raw)
    columns = plays_raw.columns.values
except (sql.exc.NoSuchTableError, sql.exc.OperationalError, NameError) as error:
    print(Colour.green + "Building table plays_raw from scratch" + Colour.end)
    columns = ['plays', 'game_ref']
    plays_raw = pd.DataFrame(columns=columns)

# create game index for accessing website
short_date = pd.to_datetime(games.date).dt.strftime('%Y%m%d')
short_name = games.home_team.map(teams.set_index('team_name')['short_name'])
game_ref = short_date + '0' + short_name

# skip games that have already been scraped
game_ref = game_ref[~game_ref.isin(plays_raw.game_ref)]

# selenium driver
driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                          options=options)

for i in game_ref:
    # load website using index
    driver.get("https://www.basketball-reference.com/boxscores/pbp/" + i + ".html")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    game_plays = [x.getText().encode('utf-8') for x in soup.find_all('tr')
                  if x.get('data-row') is not None]

    game_plays = pd.DataFrame(game_plays, columns=['plays'])
    game_plays['game_ref'] = i

    # append game_plays to plays_raw, and remove any duplicates
    plays_raw = pd.concat([plays_raw, game_plays]).drop_duplicates().reset_index(drop=True)

    write_data(df=game_plays,
               to_csv=False,
               sql_engine=engine_raw,
               db_schema='nba_raw',
               if_exists='append',
               iteration=i)

    # # write to csv
    # try:
    #     plays_raw.to_csv(str(p) + '/data/scraping/output/plays_raw.csv', sep=',')
    #     status_csv = Colour.green + 'Successfully written to csv!' + Colour.end
    # except FileNotFoundError:
    #     status_csv = Colour.red + 'Failed to write to CSV! (Path does not exist)' + Colour.end
    # except PermissionError:
    #     status_csv = Colour.red + 'Failed to write to CSV! (File already opened)' + Colour.end
    #
    # # write to sql
    # try:
    #     game_plays.to_sql('plays_raw', con=engine, schema='nba_raw', if_exists='append')
    #     status_sql = Colour.green + 'Successfully written to MySQL Database!' + Colour.end
    # except sql.exc.OperationalError:
    #     status_sql = Colour.red + 'Failed to write to DB!' + Colour.end
    #
    # print(i + ' ' + status_csv + ' ' + status_sql + ' '
    #       + str('{0:.2f}'.format(time.time() - start_time)) + ' seconds so far')

driver.close()

print(Colour.green + 'Game Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

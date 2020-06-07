### SCRAPING ODDS DATA FROM ODDSPORTAL ###
## http://www.oddsportal.com/basketball/usa/nba/results/

from nba import *
# load game data to have comparison of games available
game_data = pd.read_csv(p+'/data/output/gamedata_raw.csv')
game_data['DATE'] = pd.to_datetime(game_data['DATE'])
game_data['DATE'] = game_data['DATE'].dt.strftime('%d %b %Y')

# temporary fix for cancelled Celtics Pacers game
game_data.loc[(game_data['DATE'] == '17 Apr 2013') & (game_data['HOME_TEAM'] == 'Celtics'), 'HOME_SCORE'] = 0
game_data.loc[(game_data['DATE'] == '17 Apr 2013') & (game_data['HOME_TEAM'] == 'Celtics'), 'AWAY_SCORE'] = 0

# set column names
game_data = game_data[pd.notnull(game_data['HOME_TEAM'])]
game_data = game_data[pd.notnull(game_data['HOME_SCORE'])]
game_data = game_data[pd.notnull(game_data['AWAY_TEAM'])]
game_data = game_data[pd.notnull(game_data['AWAY_SCORE'])]

# Set start time for calculating time lapsed
start_time = time.time()

# load selenium driver
driver = webdriver.Chrome(executable_path="C:/Users/filip/PycharmProjects/modelling/venv/Scripts/chromedriver.exe")

# onnect to website
driver.get("http://www.oddsportal.com/basketball/usa/nba/results/#/")

# try:
#    timezone = driver.find_element_by_xpath("//*[@id='col-content']/div[1]/ul/li/div/a")
#    time.sleep(2)
#    timezone.click()
# except Exception:
#    pass

# set timezone to US EST
try:
    timezone = driver.find_element_by_xpath("//*[@id='user-header-timezone-expander']")
    timezone.click()
    time.sleep(2)
    us_timezone = driver.find_element_by_xpath("//*[@id='timezone-content']/a[69]")
    us_timezone.click()
except Exception:
    pass

# set up basic dataframe if initialising for first time
oddsdata = pd.DataFrame(columns=['DATE', 'TEAMS', 'SCORE', 'HOME_ODDS', 'AWAY_ODDS'])

# load existing data if available
odds_data = pd.read_csv(p+'/data/output/oddsdata.csv')
del odds_data['Unnamed: 0']
odds_data = odds_data[odds_data['DATE'] != 'Remove']

odds_data = odds_data[(pd.to_datetime(odds_data.DATE) <= pd.to_datetime(date_start_odds)) |
                      (pd.to_datetime(odds_data.DATE) >= pd.to_datetime(date_end_odds))]

# set up date range
for i in range(start_season_odds, end_season_odds):  # @UnresolvedImport
    year = driver.find_element_by_partial_link_text(str(i-1) + '/' + str(i))
    year.click()
    for j in range(30):
        time.sleep(2)
        dates = driver.find_elements_by_css_selector(".center.nob-border")
        page_data = pd.DataFrame(columns=['DAY', 'GAMES'])
        for k in range(len(dates)):
            page_data.loc[k, 'DAY'] = dates[k].text
            page_data.loc[k, 'DAY'] = page_data.loc[k, 'DAY'].replace('Today, ', '')
            page_data.loc[k, 'DAY'] = page_data.loc[k, 'DAY'].replace('Yesterday, ', '')
            if page_data.loc[k, 'DAY'].find('All Stars') > 0:
                page_data.loc[k, 'DAY'] = 'Remove'
                page_data.loc[page_data['DAY'] == 'Remove', 'GAMES'] = 1
            else:
                try:  # This exception is for 29 Feb cases
                    page_data.loc[k, 'DAY'] = datetime.strptime(page_data.loc[k, 'DAY'][0:6], '%d %b')
                    if page_data.loc[k, 'DAY'].month <= 7:
                        page_data.loc[k, 'DAY'] = date(i, page_data.loc[k, 'DAY'].month, page_data.loc[k, 'DAY'].day)
                    else:
                        page_data.loc[k, 'DAY'] = date(i-1, page_data.loc[k, 'DAY'].month, page_data.loc[k, 'DAY'].day)
                except Exception:
                    page_data.loc[k, 'DAY'] = date(i, 2, 29)
                page_data.loc[k, 'DAY'] = str(page_data.loc[k, 'DAY'].strftime('%d %b %Y'))
                page_data.loc[k, 'GAMES'] = len(game_data.loc[game_data['DATE'] == str(page_data.loc[k, 'DAY']), 'DATE'])-\
                                                len(odds_data.loc[odds_data['DATE'] == str(page_data.loc[k ,'DAY']), 'DATE'])
        for l in range(len(dates)):
            daily = pd.DataFrame(columns=['DATE', 'TEAMS', 'HOME_TEAM', 'AWAY_TEAM', 'SCORE', 'HOME_ODDS', 'AWAY_ODDS'])
            games_low = sum(page_data.loc[0:l, 'GAMES']) - page_data.loc[l, 'GAMES']
            print(games_low)
            games = page_data.loc[l, 'GAMES']
            for m in range(games_low, games_low + games):
                iter = 4+2*l+m
                try:
                    teams_path = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[2]".format(iter)
                    teams = driver.find_element_by_xpath(teams_path)
                    score_path = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[3]".format(iter)
                    score = driver.find_element_by_xpath(score_path)
                    home_path = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[4]".format(iter)
                    home_odds = driver.find_element_by_xpath(home_path)
                    away_path = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[5]".format(iter)
                    away_odds = driver.find_element_by_xpath(away_path)
                    daily.loc[m] = [page_data.loc[l, 'DAY'], teams.text, '', '', score.text, home_odds.text, away_odds.text]
                    daily.loc[m, 'HOME_TEAM'] = re.split(' - ', str(daily.loc[m, 'TEAMS']))[0]
                    daily.loc[m, 'AWAY_TEAM'] = re.split(' - ', str(daily.loc[m, 'TEAMS']))[1]
                except Exception:
                    pass
            print(page_data.loc[l, 'DAY'] + ' ' + str(time.time() - start_time) + ' ' + str(games))
            odds_data = odds_data.append(daily)
            del odds_data['TEAMS']
            odds_data.to_csv(p+'/data/output/oddsdata.csv')
        next = driver.find_element_by_xpath("//*[@id='pagination']/a[13]/span")
        next.click()
driver.close()
print('Odds Loaded ' + str(time.time() - start_time))
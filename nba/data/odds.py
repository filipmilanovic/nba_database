# http://www.oddsportal.com/basketball/usa/nba/results/
from nba import *
gamedata = pd.read_csv(p+'/data/output/gamedata_raw.csv')
gamedata['Date'] = pd.to_datetime(gamedata['Date'])
gamedata['Date'] = gamedata['Date'].dt.strftime('%d %b %Y')

# Temporary fix for cancelled Celtics Pacers game
gamedata.loc[(gamedata['Date'] == '17 Apr 2013') & (gamedata['Home Team'] == 'Celtics'), 'Home Score'] = 0
gamedata.loc[(gamedata['Date'] == '17 Apr 2013') & (gamedata['Home Team'] == 'Celtics'), 'Away Score'] = 0

gamedata = gamedata[pd.notnull(gamedata['Home Team'])]
gamedata = gamedata[pd.notnull(gamedata['Home Score'])]
gamedata = gamedata[pd.notnull(gamedata['Away Team'])]
gamedata = gamedata[pd.notnull(gamedata['Away Score'])]


# Set start time for calculating time lapsed
start_time=time.time()

## selenium driver
driver = webdriver.Chrome(executable_path="C:/Users/filip/Anaconda3/Scripts/chromedriver.exe")

# Connect to website
driver.get("http://www.oddsportal.com/basketball/usa/nba/results/#/")

try:
    timezone = driver.find_element_by_xpath("//*[@id='col-content']/div[1]/ul/li/div/a")
    time.sleep(2)
    timezone.click()
except Exception:
    pass

# set up basic dataframe if initialising for first time
oddsdata = pd.DataFrame(columns = ['Date', 'Teams', 'Score', 'HomeOdds', 'AwayOdds'])

# load existing data if available
oddsdata = pd.read_csv(p+'/data/output/oddsdata.csv')
del oddsdata['Unnamed: 0']
oddsdata = oddsdata[oddsdata['Date'] != 'Remove']
oddsdata = oddsdata[(pd.to_datetime(oddsdata.Date) <= clean_date_start) | (pd.to_datetime(oddsdata.Date) >= clean_date_end)]

# set up date range
for i in range(start_season, end_season): # @UnresolvedImport
#    season = gamedata.loc[gamedata['Season'] == i]
#    season['Date'] = season['Date'] + ' ' + str(i)
    year = driver.find_element_by_partial_link_text(str(i-1) + '/' + str(i))
    year.click()
    for j in range(30):
        time.sleep(2)
        dates = driver.find_elements_by_css_selector(".center.nob-border")
        pagedata = pd.DataFrame(columns = ['day', 'games'])
        for k in range(len(dates)):
            pagedata.loc[k, 'day'] = dates[k].text
            pagedata.loc[k, 'day'] = pagedata.loc[k, 'day'].replace('Today, ', '')
            pagedata.loc[k, 'day'] = pagedata.loc[k, 'day'].replace('Yesterday, ', '')
            if pagedata.loc[k, 'day'].find('All Stars') > 0:
                pagedata.loc[k, 'day'] = 'Remove'
                pagedata.loc[pagedata['day'] == 'Remove', 'games'] = 1
            else:
                try: ## This exception is for 29 Feb cases
                    pagedata.loc[k, 'day'] = datetime.strptime(pagedata.loc[k, 'day'][0:6],('%d %b'))
                    if pagedata.loc[k, 'day'].month <= 7:
                        pagedata.loc[k, 'day'] = date(i, pagedata.loc[k, 'day'].month, pagedata.loc[k, 'day'].day)
                    else:
                        pagedata.loc[k, 'day'] = date(i-1, pagedata.loc[k, 'day'].month, pagedata.loc[k, 'day'].day)
                except Exception:
                    pagedata.loc[k, 'day'] = date(i, 2, 29)
                pagedata.loc[k, 'day'] = str(pagedata.loc[k, 'day'].strftime('%d %b %Y'))
                pagedata.loc[k, 'games'] = len(gamedata.loc[gamedata['Date']==str(pagedata.loc[k,'day']), 'Date']) - \
                                           len(oddsdata.loc[oddsdata['Date']==str(pagedata.loc[k,'day']), 'Date'])
        for l in range(len(dates)):
            daily = pd.DataFrame(columns = ['Date', 'Teams', 'HomeTeam', 'AwayTeam', 'Score', 'HomeOdds', 'AwayOdds'])
            games_low = sum(pagedata.loc[0:l,'games']) - pagedata.loc[l,'games']
            games = pagedata.loc[l, 'games']
            for m in range(games_low, games_low + games):
                iter = 4+2*l+m
                try:
                    teamspath = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[2]".format(iter)
                    teams = driver.find_element_by_xpath(teamspath)
                    scorepath = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[3]".format(iter)
                    score = driver.find_element_by_xpath(scorepath)
                    homepath = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[4]".format(iter)
                    homeodds = driver.find_element_by_xpath(homepath)
                    awaypath = "//*[@id='tournamentTable']/table/tbody/tr[{0}]/td[5]".format(iter)
                    awayodds = driver.find_element_by_xpath(awaypath)
                    daily.loc[m] = [pagedata.loc[l, 'day'], teams.text, '', '', score.text, homeodds.text, awayodds.text]
                    daily.loc[m,'HomeTeam'] = re.split(' - ', str(daily.loc[m,'Teams']))[0]
                    daily.loc[m,'AwayTeam'] = re.split(' - ', str(daily.loc[m,'Teams']))[1]
                except Exception:
                    pass
            print(pagedata.loc[l, 'day'] + ' ' + str(time.time() - start_time) + ' ' + str(games))
            oddsdata = oddsdata.append(daily)
            del oddsdata['Teams']
            oddsdata.to_csv(p+'/data/output/oddsdata.csv')
        next = driver.find_element_by_xpath("//*[@id='pagination']/a[13]/span")
        next.click()
driver.close()
print('Odds Loaded ' + str(time.time() - start_time))
### Choose csv or sql
loadtype = 'csv'
columns = 'GameID', 'Date', 'HomeTeam', 'HomeScore', 'AwayTeam', 'AwayScore'#, 'HomeRecord', 'AwayRecord'

print ('Loading raw data ' + str(time.time() - start_time))
### Loading Data
if loadtype == 'sql':
    with connection.cursor() as cursor:
        sql = "select * from espn.gamedata_raw"
        cursor.execute(sql)
        result = cursor.fetchall()
    connection.close()
    gamedata = pd.DataFrame(list(result), columns = columns)
elif loadtype == 'csv':
    gamedata = pd.read_csv(p+'/data/output/gamedata_raw.csv')
    gamedata.columns = columns

### Data Cleaning
print('Removing pre and post-season games and adding season identifier ' + str(time.time() - start_time))
gamedata.Date = pd.to_datetime(gamedata.Date)

gamedata = gamedata[(gamedata.Date > datetime(2019,10,15))|(gamedata.Date < datetime(2019,4,12))]
gamedata = gamedata[(gamedata.Date > datetime(2018,10,17))|(gamedata.Date < datetime(2018,4,13))]
gamedata = gamedata[(gamedata.Date > datetime(2017,10,17))|(gamedata.Date < datetime(2017,4,14))]
gamedata = gamedata[(gamedata.Date > datetime(2016,10,25))|(gamedata.Date < datetime(2016,4,15))]
gamedata = gamedata[(gamedata.Date > datetime(2015,10,27))|(gamedata.Date < datetime(2015,4,17))]
gamedata = gamedata[(gamedata.Date > datetime(2014,10,28))|(gamedata.Date < datetime(2014,4,18))]
gamedata = gamedata[(gamedata.Date > datetime(2013,10,29))|(gamedata.Date < datetime(2013,4,19))]
gamedata = gamedata[(gamedata.Date > datetime(2012,10,30))|(gamedata.Date < datetime(2012,4,28))]
gamedata = gamedata[(gamedata.Date > datetime(2011,12,25))|(gamedata.Date < datetime(2011,4,15))]
gamedata = gamedata[(gamedata.Date > datetime(2010,10,26))|(gamedata.Date < datetime(2010,4,16))]
gamedata = gamedata[(gamedata.Date > datetime(2009,10,27))|(gamedata.Date < datetime(2009,4,17))]
gamedata = gamedata[(gamedata.Date > datetime(2008,10,28))]


gamedata['Season'] = [2019 if Date > datetime(2018,10,15) else
                      2018 if Date > datetime(2017,10,17) else
                      2017 if Date > datetime(2016,10,25) else
                      2016 if Date > datetime(2015,10,27) else
                      2015 if Date > datetime(2014,10,28) else
                      2014 if Date > datetime(2013,10,29) else
                      2013 if Date > datetime(2012,10,30) else
                      2012 if Date > datetime(2011,10,25) else
                      2011 if Date > datetime(2010,10,26) else
                      2010 if Date > datetime(2009,10,27) else
                      2009 for Date in gamedata['Date']]

gamedata.loc[(gamedata['HomeTeam'] == 'Hornets') & (gamedata['Date'] < datetime(2014,10,9)), 'HomeTeam'] = 'Pelicans'
gamedata.loc[(gamedata['AwayTeam'] == 'Hornets') & (gamedata['Date'] < datetime(2014,10,9)), 'AwayTeam'] = 'Pelicans'
gamedata.loc[(gamedata['HomeTeam'] == 'Bobcats') & (gamedata['Date'] < datetime(2014,10,9)), 'HomeTeam'] = 'Hornets'
gamedata.loc[(gamedata['AwayTeam'] == 'Bobcats') & (gamedata['Date'] < datetime(2014,10,9)), 'AwayTeam'] = 'Hornets'

gamedata = gamedata.loc[gamedata.HomeTeam != 'Team Stephen']
gamedata = gamedata.loc[gamedata.HomeTeam != 'WEST']
gamedata = gamedata.loc[gamedata.HomeTeam != 'EAST']

gamedata.Date = pd.to_datetime(gamedata.Date).dt.date

print('Cleaning out null observations ' + str(time.time() - start_time))

### Fix this bit of code to just exclude date range from not null function
gamedata.loc[gamedata['Date'] >= unplayed_date, 'HomeScore'] = 0
gamedata.loc[gamedata['Date'] >= unplayed_date, 'AwayScore'] = 0

gamedata = gamedata[pd.notnull(gamedata['HomeTeam'])]
gamedata = gamedata[pd.notnull(gamedata['HomeScore'])]
gamedata = gamedata[pd.notnull(gamedata['AwayTeam'])]
gamedata = gamedata[pd.notnull(gamedata['AwayScore'])]

gamedata.index = range(len(gamedata))
gamedata.GameID = range(len(gamedata))

gamedata.to_csv(p+'/data/output/gamedata.csv')
gamelog = pd.read_csv(p+'/data/output/gamelog.csv')

homelog = gamelog.loc[gamelog['Home/Away']=='Home']
awaylog = gamelog.loc[gamelog['Home/Away']=='Away']

gamedata['HomeWinTotal'] = gamedata['GameID'].map(homelog.set_index('GameID')['Wins'])
gamedata['HomeLossTotal'] = gamedata['GameID'].map(homelog.set_index('GameID')['Losses'])
gamedata['HomeWinHome'] = gamedata['GameID'].map(homelog.set_index('GameID')['HomeWin'])
gamedata['HomeLossHome'] = gamedata['GameID'].map(homelog.set_index('GameID')['HomeLoss'])
gamedata['HomeForm'] = gamedata['GameID'].map(homelog.set_index('GameID')['Form'])
gamedata['HomePPG'] = gamedata['GameID'].map(homelog.set_index('GameID')['PPG'])
gamedata['HomeOPPG'] = gamedata['GameID'].map(homelog.set_index('GameID')['OPPG'])
gamedata['HomeDiffPPG'] = gamedata['GameID'].map(homelog.set_index('GameID')['DiffPPG'])
gamedata['HomeVsOpp'] = gamedata['GameID'].map(homelog.set_index('GameID')['ResVsOpp'])
gamedata['AwayWinTotal'] = gamedata['GameID'].map(awaylog.set_index('GameID')['Wins'])
gamedata['AwayLossTotal'] = gamedata['GameID'].map(awaylog.set_index('GameID')['Losses'])
gamedata['AwayWinAway'] = gamedata['GameID'].map(awaylog.set_index('GameID')['AwayWin'])
gamedata['AwayLossAway'] = gamedata['GameID'].map(awaylog.set_index('GameID')['AwayLoss'])
gamedata['AwayForm'] = gamedata['GameID'].map(awaylog.set_index('GameID')['Form'])
gamedata['AwayPPG'] = gamedata['GameID'].map(awaylog.set_index('GameID')['PPG'])
gamedata['AwayOPPG'] = gamedata['GameID'].map(awaylog.set_index('GameID')['OPPG'])
gamedata['AwayDiffPPG'] = gamedata['GameID'].map(awaylog.set_index('GameID')['DiffPPG'])
gamedata['AwayVsOpp'] = gamedata['GameID'].map(awaylog.set_index('GameID')['ResVsOpp'])

columns = 'GameID', 'Date', 'HomeTeam', 'HomeScore', 'AwayTeam', 'AwayScore', 'Result', 'Season', 'HomeWinTotal', \
'HomeLossTotal', 'HomeWinHome', 'HomeLossHome', 'HomeForm', 'HomeWinLast', 'HomePPG', 'HomeOPPG', 'HomeDiffPPG', \
'HomeVsOpp', 'AwayWinTotal', 'AwayLossTotal', 'AwayWinAway', 'AwayLossAway', 'AwayForm', 'AwayWinLast', 'AwayPPG', \
'AwayOPPG', 'AwayDiffPPG', 'AwayVsOpp'

gamedata = gamedata.reindex(columns = columns)

# gamedata = gamedata.convert_objects(convert_numeric=True)

gamedata.to_csv(p+'/data/output/gamedata.csv')

print('Calculating yearly standings and adding previous season record ' + str(time.time() - start_time))
from data.standings import wins # @UnresolvedImport

for i in wins.index:
    for j in range(2009,2019):
        gamedata.HomeWinLast[(gamedata.HomeTeam == i) & (gamedata.Season == j)] = wins.loc[i,j-1]
        gamedata.AwayWinLast[(gamedata.AwayTeam == i) & (gamedata.Season == j)] = wins.loc[i,j-1]

print('Creating result variable and adjusting record for pre-game numbers ' + str(time.time() - start_time))
gamedata.loc[gamedata['HomeScore']>gamedata['AwayScore'], 'Result'] = 'HomeWin'
gamedata.loc[gamedata['HomeScore']<gamedata['AwayScore'], 'Result'] = 'HomeLoss'

gamedata.loc[gamedata['Result'] == 'HomeWin','HomeWinHome'] = gamedata.loc[gamedata['Result'] == 'HomeWin','HomeWinHome'] - 1
gamedata.loc[gamedata['Result'] == 'HomeWin','HomeWinTotal'] = gamedata.loc[gamedata['Result'] == 'HomeWin','HomeWinTotal'] - 1
gamedata.loc[gamedata['Result'] == 'HomeWin','AwayLossAway'] = gamedata.loc[gamedata['Result'] == 'HomeWin','AwayLossAway'] - 1
gamedata.loc[gamedata['Result'] == 'HomeWin','AwayLossTotal'] = gamedata.loc[gamedata['Result'] == 'HomeWin','AwayLossTotal'] - 1

gamedata.loc[gamedata['Result'] == 'HomeLoss','HomeLossHome'] = gamedata.loc[gamedata['Result'] == 'HomeLoss','HomeLossHome'] - 1
gamedata.loc[gamedata['Result'] == 'HomeLoss','HomeLossTotal'] = gamedata.loc[gamedata['Result'] == 'HomeLoss','HomeLossTotal'] - 1
gamedata.loc[gamedata['Result'] == 'HomeLoss','AwayWinAway'] = gamedata.loc[gamedata['Result'] == 'HomeLoss','AwayWinAway'] - 1
gamedata.loc[gamedata['Result'] == 'HomeLoss','AwayWinTotal'] = gamedata.loc[gamedata['Result'] == 'HomeLoss','AwayWinTotal'] - 1

print('Adding travel and rest data to gamedata ' + str(time.time() - start_time))

gamedata.index = range(len(gamedata))
gamedata['HomeTravelLast'] = gamedata['GameID'].map(homelog.set_index('GameID')['DistLast'])
gamedata['AwayTravelLast'] = gamedata['GameID'].map(awaylog.set_index('GameID')['DistLast'])
gamedata['HomeTravelWeek'] = gamedata['GameID'].map(homelog.set_index('GameID')['DistWeek'])
gamedata['AwayTravelWeek'] = gamedata['GameID'].map(awaylog.set_index('GameID')['DistWeek'])
gamedata['HomeRest'] = gamedata['GameID'].map(homelog.set_index('GameID')['Rest'])
gamedata['AwayRest'] = gamedata['GameID'].map(awaylog.set_index('GameID')['Rest'])
gamedata['HomeGameWeek'] = gamedata['GameID'].map(homelog.set_index('GameID')['GameWeek'])
gamedata['AwayGameWeek'] = gamedata['GameID'].map(awaylog.set_index('GameID')['GameWeek'])

print('Converting record to percentage ' + str(time.time() - start_time))
gamedata['HomeWinTotal'] = gamedata['HomeWinTotal']/(gamedata['HomeWinTotal']+gamedata['HomeLossTotal'])
gamedata['HomeLossTotal'] = 1-gamedata['HomeWinTotal']
gamedata['HomeWinHome'] = gamedata['HomeWinHome']/(gamedata['HomeWinHome']+gamedata['HomeLossHome'])
gamedata['HomeLossHome'] = 1 - gamedata['HomeWinHome']
gamedata['AwayWinAway'] = gamedata['AwayWinAway']/(gamedata['AwayWinAway']+gamedata['AwayLossAway'])
gamedata['AwayLossAway'] = 1 - gamedata['AwayWinAway']
gamedata['AwayWinTotal'] = gamedata['AwayWinTotal']/(gamedata['AwayWinTotal']+gamedata['AwayLossTotal'])
gamedata['AwayLossTotal'] = 1 - gamedata['AwayWinTotal']
gamedata.loc[gamedata['Season'] != 2012, 'HomeWinLast'] = gamedata.loc[gamedata['Season'] != 2012, 'HomeWinLast']/82
gamedata.loc[gamedata['Season'] != 2012, 'AwayWinLast'] = gamedata.loc[gamedata['Season'] != 2012, 'AwayWinLast']/82
gamedata.loc[gamedata['Season'] == 2012, 'HomeWinLast'] = gamedata.loc[gamedata['Season'] == 2012, 'HomeWinLast']/66
gamedata.loc[gamedata['Season'] == 2012, 'AwayWinLast'] = gamedata.loc[gamedata['Season'] == 2012, 'AwayWinLast']/66
gamedata['HomeVsOpp'] = gamedata['HomeVsOpp']/5
gamedata['AwayVsOpp'] = gamedata['AwayVsOpp']/5

gamedata.loc[pd.isnull(gamedata['HomeWinTotal']), 'HomeWinTotal'] = 0
gamedata.loc[pd.isnull(gamedata['HomeLossTotal']), 'HomeLossTotal'] = 0
gamedata.loc[pd.isnull(gamedata['HomeWinHome']), 'HomeWinHome'] = 0
gamedata.loc[pd.isnull(gamedata['HomeLossHome']), 'HomeLossHome'] = 0
gamedata.loc[pd.isnull(gamedata['AwayWinAway']), 'AwayWinAway'] = 0
gamedata.loc[pd.isnull(gamedata['AwayLossAway']), 'AwayLossAway'] = 0
gamedata.loc[pd.isnull(gamedata['AwayWinTotal']), 'AwayWinTotal'] = 0
gamedata.loc[pd.isnull(gamedata['AwayLossTotal']), 'AwayLossTotal'] = 0
gamedata.loc[pd.isnull(gamedata['HomeWinLast']), 'HomeWinLast'] = 0
gamedata.loc[pd.isnull(gamedata['AwayWinLast']), 'AwayWinLast'] = 0
gamedata.loc[pd.isnull(gamedata['HomeVsOpp']), 'HomeVsOpp'] = 0
gamedata.loc[pd.isnull(gamedata['AwayVsOpp']), 'AwayVsOpp'] = 0

gamedata.loc[pd.isnull(gamedata['HomeRest']), 'HomeRest'] = 0
gamedata.loc[pd.isnull(gamedata['AwayRest']), 'AwayRest'] = 0

gamedata.loc[gamedata['Result']=='HomeWin', 'Result'] = 0
gamedata.loc[gamedata['Result']=='HomeLoss', 'Result'] = 1
gamedata['Result'] = pd.Categorical(gamedata['Result'])

##### Combine odds data
oddsdata = pd.read_csv(p+'/data/output/oddsdata.csv')
location = pd.read_csv(p+'/data/output/location.csv')

oddsdata = oddsdata[pd.notnull(oddsdata['AwayTeam'])]
oddsdata['AwayTeam'] = oddsdata['AwayTeam'].map(lambda x: x.rstrip("\r\n "))
oddsdata['HomeTeam'] = oddsdata['HomeTeam'].map(location.set_index('FullTeam')['Team'])
oddsdata['AwayTeam'] = oddsdata['AwayTeam'].map(location.set_index('FullTeam')['Team'])

oddsdata = oddsdata.loc[oddsdata.Date != 'Remove']
oddsdata['Date'] = [datetime.strptime(d, '%d %b %Y') for d in oddsdata['Date']]
gamedata.Date = pd.to_datetime(gamedata.Date).dt.date
oddsdata.Date = pd.to_datetime(oddsdata.Date).dt.date

oddsdata.index = range(len(oddsdata))

def gamemap(i):
    try:
        return int(gamedata.loc[(gamedata['HomeTeam'] == oddsdata.loc[i,'HomeTeam']) \
                            & (gamedata['Date'] == oddsdata.loc[i,'Date']), 'GameID'])
    except Exception:
        pass

### TEMPORARY FIX - Lakers Clippers on 17/1/2011 shows up as 18/1/2011 in oddsdata
oddsdata.loc[(oddsdata['AwayTeam'] == 'Lakers') & (oddsdata['Date'] == date(2011, 1, 18)), \
             'Date'] = date(2011, 1, 17)

for i in range(len(oddsdata)):
    try:
        oddsdata.loc[i, 'GameID'] = gamemap(i)
    except Exception:
        oddsdata.loc[i, 'GameID'] = 'nan'

oddsdata = oddsdata[pd.notnull(oddsdata['GameID'])]
gamedata['HomeOdds'] = gamedata['GameID'].map(oddsdata.set_index('GameID')['HomeOdds'])
gamedata['AwayOdds'] = gamedata['GameID'].map(oddsdata.set_index('GameID')['AwayOdds'])

###### Tidy up bit above

print('Writing data to csv and sql ' + str(time.time() - start_time))
gamedata.to_csv(p+'/data/output/gamedata.csv')

#engine = create_engine("mysql+mysqlconnector://root:password@localhost/espn")
#gamedata.to_sql('gamedata', con=engine, schema='espn', if_exists='replace')

print('Data Cleaned and written ' + str(time.time() - start_time))
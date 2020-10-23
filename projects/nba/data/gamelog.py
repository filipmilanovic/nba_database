# from data import coordinates # @UnresolvedImport

gamedata = pd.read_csv(p+'/data/output/gamedata.csv')
del gamedata['Unnamed: 0']

location = pd.read_csv(p+'/data/output/location.csv')
del location['Unnamed: 0']

gamelog = pd.DataFrame()

print('Creating Game Logs')
for i in location['Team']:
    team = pd.DataFrame()
    
    team['Team'] = [i] * len(gamedata[(gamedata.HomeTeam == i) | (gamedata.AwayTeam == i)])
    
    team.index = gamedata.index[(gamedata.HomeTeam == i) | (gamedata.AwayTeam == i)]
    
    team['GameID'] = gamedata.loc[(gamedata.HomeTeam == i) | (gamedata.AwayTeam == i), 'GameID']
    
    team['Date'] = gamedata.loc[(gamedata.HomeTeam == i) | (gamedata.AwayTeam == i), 'Date']

    team['Season'] = gamedata.loc[(gamedata.HomeTeam == i) | (gamedata.AwayTeam == i), 'Season']
    
    team['Opponent'] = \
        gamedata.loc[gamedata.HomeTeam == i, 'AwayTeam'].append(gamedata.loc[gamedata.AwayTeam == i,'HomeTeam'])

    team.loc[gamedata.index[gamedata.HomeTeam == i], 'Home/Away'] = 'Home'
    
    team.loc[gamedata.index[gamedata.AwayTeam == i], 'Home/Away'] = 'Away'
    
    team['Scored'] = \
    gamedata.loc[gamedata.HomeTeam == i,'HomeScore'].append(gamedata.loc[gamedata.AwayTeam == i,'AwayScore'])
    
    team['Against'] = \
    gamedata.loc[gamedata.HomeTeam == i,'AwayScore'].append(gamedata.loc[gamedata.AwayTeam == i,'HomeScore'])
    
    team['Result'] = np.where(team['Scored'] > team['Against'], 'Win', 'Loss')
    
    team['Location'] = team.loc[team['Home/Away']=='Home','Team'].map(location.set_index('Team')['City']).append(
    team.loc[team['Home/Away']=='Away','Opponent'].map(location.set_index('Team')['City']))
    
    team['Coordinates'] = team.loc[team['Home/Away']=='Home','Team'].map(location.set_index('Team')['Coordinates']).append(
    team.loc[team['Home/Away']=='Away','Opponent'].map(location.set_index('Team')['Coordinates']))

    for j in range(2009,2020):
        temp = team[team['Season'] == j]
        temp = temp.sort_values(by = 'Date', ascending=True)
        temp.index = range(len(temp))
        temp.loc[0, 'Wins'] = np.where(temp.loc[0,'Result'] == 'Win', 1, 0)
        temp.loc[0, 'Losses'] = np.where(temp.loc[0,'Result'] == 'Loss', 1, 0)
        temp.loc[0, 'HomeWin'] = np.where((temp.loc[0,'Result'] == 'Win') & (temp.loc[0,'Home/Away'] == 'Home'), 1, 0)
        temp.loc[0, 'HomeLoss'] = np.where((temp.loc[0,'Result'] == 'Loss') & (temp.loc[0,'Home/Away'] == 'Home'), 1, 0)
        temp.loc[0, 'AwayWin'] = np.where((temp.loc[0,'Result'] == 'Win') & (temp.loc[0,'Home/Away'] == 'Away'), 1, 0)
        temp.loc[0, 'AwayLoss'] = np.where((temp.loc[0,'Result'] == 'Loss') & (temp.loc[0,'Home/Away'] == 'Away'), 1, 0)
        temp.loc[0, 'Form'] = 0
        temp.loc[min(temp.index), 'DistLast'] = \
            geodesic(temp.Coordinates[0].replace('(','').replace(')',''), \
                     location.Coordinates[location.Team == i].item().replace('(','').replace(')','')).kilometers
        temp.loc[0, 'DistWeek'] = temp.loc[0, 'DistLast']
        recent = team.loc[(team['Team'] == i) & (team['Opponent'] == temp.loc[0, 'Opponent']) &
                              (team['Date'] < temp.loc[0, 'Date'])].tail(5)
        temp.loc[0, 'ResVsOpp'] = sum(recent['Result'] == "Win")
        for k in range(1, len(temp)):
            # temp.loc[k,'Date'] = datetime.strptime(temp.loc[k,'Date'], '%Y-%m-%d')
            temp.loc[k,'DistLast'] = geodesic(temp.loc[k,'Coordinates'].replace('(','').replace(')','') \
                                              ,temp.loc[k-1,'Coordinates'].replace('(','').replace(')','')).kilometers
            temp.loc[k,'DistWeek'] = sum(temp.loc[(pd.to_datetime(temp['Date']) >= \
                                                  pd.to_datetime(temp.loc[k, 'Date']) - timedelta(days=7)) & \
                                                  (pd.to_datetime(temp['Date']) <= \
                                                  pd.to_datetime(temp.loc[k, 'Date'])), 'DistLast'])
            temp.loc[k,'Rest'] = \
            (datetime.strptime(temp.loc[k,'Date'], '%Y-%m-%d') - \
             datetime.strptime(temp.loc[k-1,'Date'], '%Y-%m-%d')).days - 1
            temp.loc[k,'GameWeek'] = len(temp.loc[(pd.to_datetime(temp['Date']) >= \
                                                  pd.to_datetime(temp.loc[k, 'Date']) - timedelta(days=7)) & \
                                                  (pd.to_datetime(temp['Date']) < \
                                                  pd.to_datetime(temp.loc[k, 'Date']))])
            temp.loc[k,'Wins'] = temp.loc[k-1, 'Wins'] + np.where(temp.loc[k,'Result'] == 'Win', 1, 0)
            temp.loc[k,'Losses'] = temp.loc[k-1, 'Losses'] + np.where(temp.loc[k,'Result'] == 'Loss', 1, 0)
            temp.loc[k,'HomeWin'] = temp.loc[k-1, 'HomeWin'] + \
            np.where((temp.loc[k,'Result'] == 'Win') & (temp.loc[k,'Home/Away'] == 'Home'), 1, 0)
            temp.loc[k,'HomeLoss'] = temp.loc[k-1, 'HomeLoss'] + \
            np.where((temp.loc[k,'Result'] == 'Loss') & (temp.loc[k,'Home/Away'] == 'Home'), 1, 0)
            temp.loc[k,'AwayWin'] = temp.loc[k-1, 'AwayWin'] + \
            np.where((temp.loc[k,'Result'] == 'Win') & (temp.loc[k,'Home/Away'] == 'Away'), 1, 0)
            temp.loc[k,'AwayLoss'] = temp.loc[k-1, 'AwayLoss'] + \
            np.where((temp.loc[k,'Result'] == 'Loss') & (temp.loc[k,'Home/Away'] == 'Away'), 1, 0)
            if k < 11:
                temp.loc[k,'Form'] = temp.loc[k-1, 'Wins']/k
            else:
                temp.loc[k,'Form'] = (temp.loc[k-1, 'Wins'] - temp.loc[k-11, 'Wins'])/10
            temp.loc[k, 'PPG'] = np.mean(temp.loc[temp.index<k,'Scored'])
            temp.loc[k, 'OPPG'] = np.mean(temp.loc[temp.index<k,'Against'])
            temp.loc[k, 'DiffPPG'] = temp.loc[k, 'PPG'] - temp.loc[k, 'OPPG']
            recent = team.loc[(team['Team']==i) & (team['Opponent']==temp.loc[k, 'Opponent']) & 
                              (team['Date'] < temp.loc[k, 'Date'])].tail(5)
            temp.loc[k, 'ResVsOpp'] = sum(recent['Result']=="Win")
        temp.loc[0, 'PPG'] = 0
        temp.loc[0, 'OPPG'] = 0
        temp.loc[0, 'DiffPPG'] = 0
        temp.loc[0, 'Rest'] = 0
        temp.loc[0, 'GameWeek'] = 0
        gamelog = gamelog.append(temp, ignore_index=True)
    print('Logged ' + str(i) + ' ' + str(time.time() - start_time))

gamelog.to_csv(p+'/data/output/gamelog.csv')

#engine = create_engine("mysql+mysqlconnector://root:password@localhost/espn")
#gamelog.to_sql('gamelog', con=engine, schema='espn', if_exists='replace')
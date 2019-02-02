from nba import *

gamedata = pd.read_csv(p+'/data/output/gamedata.csv')

index = '76ers', 'Bucks', 'Bulls', 'Cavaliers', 'Celtics', 'Clippers', 'Grizzlies', 'Hawks', 'Heat',\
'Hornets', 'Jazz', 'Kings', 'Knicks', 'Lakers', 'Magic', 'Mavericks', 'Nets', 'Nuggets', 'Pacers',\
'Pelicans', 'Pistons', 'Raptors', 'Rockets', 'Spurs', 'Suns', 'Thunder', 'Timberwolves', 'Trail Blazers',\
'Warriors', 'Wizards'

wins = pd.DataFrame(index = index)

wins['2008'] = 40, 26, 33, 45, 66, 23, 22, 37, 15, 32, 54, 38, 23, 57, 52, 51, 34, 50, 36, 56, 59, 41, 55,\
56, 55, 20, 22, 41, 48, 43


for i in wins.index:
    for j in range(2009,2019):
        wins.loc[i,j] = \
        max(gamedata.HomeWinTotal[(gamedata.HomeTeam==i) & (gamedata.Season==j)].max(), \
        gamedata.AwayWinTotal[(gamedata.AwayTeam==i) & (gamedata.Season==j)].max())

wins.columns = range(2008, 2019)

wins.to_csv(p+'/data/output/standings.csv')
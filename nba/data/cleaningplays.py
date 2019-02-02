""" This code cleans play-by-play data """
from nba import pd, p, time, START_TIME

### Start from scratch here ###
plays = pd.read_csv(p+'/data/output/plays_raw.csv', sep=',')
del plays['Unnamed: 0']
plays['Date'] = pd.to_datetime(plays['Date']).dt.date

games = plays.drop_duplicates(subset=['Date', 'Home Team'])
games.index = range(len(games))

for i in range(len(games)):
    if games.loc[i, 'Away Team'] == '  1':
        print(i)
        dct = {'Date': games.loc[i, 'Date'], 'Home Team': games.loc[i, 'Home Team']}
        temp = plays[(plays['Date'] == dct['Date']) & (plays['Home Team'] == dct['Home Team'])]
        temp.index = range(len(temp))
        plays.loc[(plays['Date'] == dct['Date']) & \
                  (plays['Home Team'] == dct['Home Team']), 'Away Team'] \
                  = temp.loc[1, 'Plays'][0:3]
        plays.loc[(plays['Date'] == dct['Date']) & \
                  (plays['Home Team'] == dct['Home Team']), 'Home Team'] \
                  = temp.loc[2, 'Plays'][0:3]

plays.to_csv(p+'/data/output/plays_raw_clean.csv',
             sep=',')
#print(games)

### Start with updated teams data here ###
plays = pd.read_csv(p+'/data/output/plays_raw_clean.csv',
                    sep=',')

quarter = pd.Series('1st')

for i in range(1, len(plays)):
    if plays.loc[i, 'Plays'].find('Start of') == -1:
        quarter[i] = quarter[i-1]
    elif plays.loc[i, 'Plays'].find('1st q') > 0:
        quarter[i] = '1st'
    elif plays.loc[i, 'Plays'].find('2nd q') > 0:
        quarter[i] = '2nd'
    elif plays.loc[i, 'Plays'].find('3rd q') > 0:
        quarter[i] = '3rd'
    elif plays.loc[i, 'Plays'].find('4th q') > 0:
        quarter[i] = '4th'
    elif plays.loc[i, 'Plays'].find('1st o') > 0:
        quarter[i] = '1st OT'
    elif plays.loc[i, 'Plays'].find('2nd o') > 0:
        quarter[i] = '2nd OT'
    elif plays.loc[i, 'Plays'].find('3rd o') > 0:
        quarter[i] = '3rd OT'
    elif plays.loc[i, 'Plays'].find('4th o') > 0:
        quarter[i] = '4th OT'
    if i % 10000 == 0:
        print(str(i) + ' ' + str(time.time() - START_TIME))

plays.to_csv(p+'/data/output/plays.csv',
             sep=',')

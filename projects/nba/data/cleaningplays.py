""" This code cleans play-by-play data """
from projects.nba import pd, p, time, START_TIME
from projects.nba.utils.functions import mid

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

quarter = pd.Series('1st q')

for i in range(1, len(plays)):
    if plays.loc[i, 'Plays'].find('Start of') > 0:
        quarter[i] = mid(plays.loc[i, 'Plays'],
               plays.loc[i, 'Plays'].find('Start of') + 9, 5)
    else:
        quarter[i] = quarter[i-1]
    if i % 10000 == 0:
        print(str(i) + ' ' + str(time.time() - START_TIME))

plays['Quarter'] = quarter

plays.to_csv(p+'/data/output/plays.csv', \
             sep=',')

### Start with Quarter indicator here
plays = pd.read_csv(p+'/data/output/plays.csv',
                    sep=',')

del plays['Unnamed: 0']
plays['Date'] = pd.to_datetime(plays['Date']).dt.date

# Remove unneeded strings
plays = plays.loc[~plays['Plays'].str.contains('1 2 3 4')]
plays = plays.loc[~plays['Plays'].str.contains('Time ')]
plays = plays.loc[plays['Plays'].str.slice(0,3,1) != plays['Away Team']]
plays = plays.loc[plays['Plays'].str.slice(0,3,1) != plays['Home Team']]
plays = plays.loc[plays['Plays'] != '1st Q']
plays = plays.loc[plays['Plays'] != '2nd Q']
plays = plays.loc[plays['Plays'] != '3rd Q']
plays = plays.loc[plays['Plays'] != '4th Q']
plays = plays.loc[plays['Plays'] != '1st OT']
plays = plays.loc[plays['Plays'] != '2nd OT']
plays = plays.loc[plays['Plays'] != '3rd OT']

plays.loc[plays['Plays'].str.contains('Start of'), 'Event'] = 'Start'
plays.loc[plays['Plays'].str.contains('End of'), 'Event'] = 'End'
plays.loc[plays['Plays'].str.contains('Jump ball'), 'Event'] = 'Jump ball'
plays.loc[plays['Plays'].str.contains('makes 2'), 'Event'] = '2 points'
plays.loc[plays['Plays'].str.contains('makes 3'), 'Event'] = '3 points'
plays.loc[plays['Plays'].str.contains('makes f'), 'Event'] = '1 point'
plays.loc[plays['Plays'].str.contains('makes t'), 'Event'] = '1 point'
plays.loc[plays['Plays'].str.contains('makes c'), 'Event'] = '1 point'
plays.loc[plays['Plays'].str.contains('misses 2'), 'Event'] = '2 miss'
plays.loc[plays['Plays'].str.contains('misses 3'), 'Event'] = '3 miss'
plays.loc[plays['Plays'].str.contains('misses f'), 'Event'] = 'FT miss'
plays.loc[plays['Plays'].str.contains('misses t'), 'Event'] = 'FT miss'
plays.loc[plays['Plays'].str.contains('misses c'), 'Event'] = 'FT miss'
plays.loc[plays['Plays'].str.contains('rebound'), 'Event'] = 'Rebound'
plays.loc[plays['Plays'].str.contains('Turnover'), 'Event'] = 'Turnover'
plays.loc[plays['Plays'].str.contains('foul'), 'Event'] = 'Foul'
plays.loc[plays['Plays'].str.contains('tech foul'), 'Event'] = 'Def 3 sec'
plays.loc[plays['Plays'].str.contains('Technical foul'), 'Event'] = 'Technical'
plays.loc[plays['Plays'].str.contains('enters'), 'Event'] = 'Sub'
plays.loc[plays['Plays'].str.contains('timeout'), 'Event'] = 'Timeout'
plays.loc[plays['Plays'].str.contains('Violation'), 'Event'] = 'Violation'
plays = plays.loc[~plays['Event'].isnull()]

plays['Time'] = plays['Plays'].str.slice(0,7,1)

plays.to_csv(p+'/data/output/test.csv', \
             sep=',')

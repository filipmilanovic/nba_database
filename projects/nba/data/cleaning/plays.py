from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.cleaning import *

# def get_quarter(x):


plays_raw = load_data(df='plays_raw',
                      sql_engine=engine_raw,
                      meta=metadata_raw)

columns = ['game_id', 'quarter', 'time', 'player', 'event', 'event_value', 'event_detail']
# print(plays_raw)

test = plays_raw.loc[plays_raw.game_ref == '201710170CLE']

plays = pd.DataFrame(columns=columns)

test = test[~(test.plays.str.contains('Time') & test.plays.str.contains('Score'))]

plays.game_id = test.game_ref
print(test.plays[1])
print(test.plays[1].find('Start of'))

print([mid(x, x.find('Start of') + 9, 3) for x in test.plays])



# print(plays)

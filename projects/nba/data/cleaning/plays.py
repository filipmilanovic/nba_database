from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.cleaning import *

plays_raw = load_data(df='plays_raw',
                      sql_engine=engine_raw,
                      meta=metadata_raw)

columns = ['game', 'quarter', 'time', 'player', 'event', 'event_value', 'event_detail']
# print(plays_raw)

test = plays_raw.loc[plays_raw.game_ref == '201710170CLE']

plays = test[~(test.plays.str.contains('Time') & test.plays.str.contains('Score'))]



print(plays)



# test = test.plays.str.findall('Score')
# print(test)

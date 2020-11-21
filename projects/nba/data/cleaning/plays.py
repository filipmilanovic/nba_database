from projects.nba import *  # import all project specific utils
from projects.nba.data.cleaning import *

plays_raw = load_plays_raw()

columns = ['game', 'quarter', 'time', 'player', 'event', 'event_value', 'event_detail']

test = plays_raw.loc[plays_raw.game_ref == '201710170CLE']

print(test[~(test.plays.str.contains('Time') & test.plays.str.contains('Score'))])

# test = test.plays.str.findall('Score')
# print(test)

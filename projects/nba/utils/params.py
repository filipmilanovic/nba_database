# SETTING PARAMETERS FOR RUNNING OF PROJECT
from datetime import date

# Dates for table games
start_date_games = date(2016, 7, 1)
end_date_games = date(2019, 6, 30)

# Dates for table plays
start_date_plays = date(2016, 7, 1)
end_date_plays = date(2019, 6, 30)

# Control to skip games that have already been scraped
SKIP_SCRAPED_DAYS = True

# Dates for table odds
start_season_odds = 2017
end_season_odds = 2019

# Loading method (csv or sql)
LOAD_METHOD = 'sql'

# For cleaning game data future games
unplayed_date = date(2019, 6, 30)

# SETTING PARAMETERS FOR RUNNING OF PROJECT
from modelling.projects import dt

# Dates for table games
start_season_games = 2020
end_season_games = 2020

# Dates for table plays
start_date_plays = dt(2000, 7, 1)
end_date_plays = dt(2020, 10, 12)

# Control to skip games that are already in DB
SKIP_SCRAPED_GAMES = True
SKIP_SCRAPED_PLAYERS = True

# Dates for table odds
start_season_odds = 2009  # odds only from 2008/2009
end_season_odds = 2020

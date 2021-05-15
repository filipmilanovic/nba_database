# SETTING PARAMETERS FOR RUNNING OF PROJECT
from datetime import datetime as dt

# Dates for table games
start_season_games = 2001
end_season_games = 2020

# Dates for table plays
start_date_plays = dt(2000, 7, 1)
end_date_plays = dt(2020, 10, 12)

# Control whether to skip or replace cases that are already in DB
REBUILD_DB = False

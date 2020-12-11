# SETTING PARAMETERS FOR RUNNING OF PROJECT
from datetime import date

# For game data scraping dates
start_date_games = date(2016, 7, 1)
end_date_games = date(2019, 6, 30)
start_date_plays = date(2016, 7, 1)
end_date_plays = date(2019, 6, 30)
SKIP_SCRAPED_DAYS = True

# Loading method (csv or sql)
LOAD_METHOD = 'sql'

# For odds portal odds scraping dates
start_season_odds = 2019
end_season_odds = 2020
date_start_odds = date(2018, 6, 30)
date_end_odds = date(2019, 6, 30)

# For cleaning game data future games
unplayed_date = date(2019, 6, 30)

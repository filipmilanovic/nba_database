# NBA Database
### Requirements
- python3.8
- pip3
- venv
- install libraries inside the virtual environment

`pip3 install -r requirements.txt`

The project should now be set up and ready to run and interact with GitHub

### Set-up Instructions
- Start Docker on your machine
- In the terminal, run `docker compose up --build`, and wait for the MySQL database to be built
- The database should now be available at [localhost:3308](http://localhost:3308), with PHPMyAdmin available at
[localhost:8080](http://localhost:8080)

#### Database Connection
By default, this project has been set up to work with MySQL databases.  All the SQL connections are defined at 
[connections.py](utils/connections.py).

The connection parameters can be adjusted at [environment.py](utils/environment.py).

The `write_data`, `load_data` and `initialise_df` functions have been defined at
[functions.py](utils/functions.py) and will need to be adjusted  if another DB is to be used.

#### Data Scraping and Cleaning
To ensure everything runs smoothly, the modules should be run in the following order:

[cleaning.teams.py](data/scraping/teams.py) - this gets the team data from stats.nba.com and writes to
`nba.teams` in the DB. (10 minutes)

[scraping.games.py](data/scraping/games.py) - this scrapes daily score data from [stats.nba.com](stats.nba.com)
within the date range defined in [params.py](utils/params.py) and writes the data to `nba.games` in the DB.
(20 seconds)

[scraping.game_lineups](data/scraping/games_lineups.py) - this goes through the box score for each game in
`nba.games` and scrapes the lineups for each time, denoting Starters, Bench, and DNP, then writes the data to
`nba.games_lineups` in the DB. (~2 hours)

[scraping.players.py](data/scraping/players.py) - this pulls the entire roster for each game-season
combination in the `nba.games`, then scrapes information about each player in the list, then writes the data to
`nba.players` in the DB. (~5 minutes)

[scraping.plays_raw.py](data/scraping/plays_raw.py) - this scrapes the raw play-by-play rows from
Basketball Reference for all games that appear within both the nba.games table, and the date range defined in
[params.py](utils/params.py), then writes the data to `nba_raw.plays_raw` in the DB. (~2 hours)

[cleaning.plays.py](data/cleaning/plays.py) - this applies logic to all raw play by play rows in
`nba_raw.plays_raw` to clean and isolate each individual statistic that happens in a game (e.g. one FGA row
becomes multiple rows; FGA, FG Miss/Make, Assist, Block, Rebound), then writes the data to `nba.plays` in the DB.
(~1 hour)

[cleaning.plays_players.py](data/cleaning/plays_players.py) - this figures out which players were on the
court at any point in time.  Basketball Reference doesn't show substitutions at quarter/half breaks, so this looks
through plays in each quarter, and figures out which players contributed/substituted.  In some cases, a player plays an
entire quarter without any contributions, so the box scores are scraped to figure out where the minutes discrepancies
occur. (~45 minutes)

[scraping.odds.py]() has been **deprecated** until a more reliable source is found

### Analysis & Modelling
#### Potential analyses
* Overall 'value added' statistic by player (e.g. +/- by player accounting for other players on the court)
* Predicting game probabilities (e.g. based on record, home/away, fatigue, missing players)
* Interesting stats/trends (e.g. likelihood of shooting/making next shot after shot/make; importance index
  by game)

### Planned Development
*Note: all data and modelling files that are not listed above are currently not in use.*
* Write cleaning.game_logs.py script to create a nicer dataset for predictive
  analysis
  
* Re-do betting odds scraping
  
* Add ejections to [cleaning.plays.py](data/cleaning/plays.py)
  
* Access [NBA stats](http://stats.nba.com) for shot information (location, type, defenders)
  
* ~~Update [cleaning.plays.py](data/cleaning/plays.py) to include possession indicator and which players
  are on the court~~
  
* ~~Add automated performance testing~~
  
* ~~Update all data modules to be faster (e.g. multi-processing, writing output in batches, more efficient code)~~
  
* Set up central control to build dataset from one script
  
* Move scraping to use [nba.com](http://nba.com) - this is likely to be slower, but should be more accurate, so I manual fixes
can be reduced and is probably also a bit more 'official'

* Set up automated daily ingestion of data

* ~~Keep chromedriver up to date automatically, or move to purely using the requests library~~

* Convert `get_session` and pre-execution table clearing/iteration skipping into a
  [function](utils/functions.py)
  
* Set up API to access database from Python

* Set up UI for exploration of data

### Bug Log


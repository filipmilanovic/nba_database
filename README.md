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

#### Data Scraping and Cleaning
The following scripts access [stats.nba.com](stats.nba.com) endpoints within the date range defined in
[params.py](utils/params.py).  These scripts should be run in the following order to most completely develop the
corresponding tables in the DB (approximate time per season in brackets):

[scraping.teams.py](data/scraping/teams.py) - gets the team data from `commonteamyears` and `teaminfocommon` and writes
to `nba.teams` (30 seconds)

[scraping.standings.py](data/scraping/standings.py) - gets the season-by-season record and standings data from
`leaguestandingsv3` and writes to `nba.standings`.  There is an issue with two teams ranked as the 5th seed in the West
in 2001, so a [query](data/queries/standings/fix_seeds.sql) is run to correct it (1 second)

[scraping.games.py](data/scraping/games.py) - gets game data from `scheduleLeaguev2` and writes the data to
`nba.games`.  Playoff series identifiers are grabbed from `commonplayoffseries`, although this is incomplete from 2001
and earlier, so a [query](data/queries/games/add_series_info.sql) is run to populate the missing data (2 seconds)

[scraping.playoffs.py](data/scraping/playoffs.py) - accesses playoff series information from `playoffbracket` and
writes the data to `nba.playoffs`.  The data is only tidy from 2020, so a
[query](data/queries/playoffs/add_teams_info.sql) is run to populate missing data (1 seconds)

[scraping.players.py](data/scraping/players.py) - gets all player information from `playerindex` and populates
`nba.players` (instant)

[scraping.draft.py](data/scraping/draft.py) - gets all draft information from `drafthistory` and populates
`nba.draft` (instant)

[cleaning.transactions.py](data/scraping/transactions.py) - gets player transaction json with data from 2015 onwards
from a static [NBA_Player_Movement](https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json) file and
writes to `nba.transactions` (instant)

[scraping.games_lineups](data/scraping/games_lineups.py) - this goes through the box score for each game in
`nba.games` and scrapes the lineups for each time, denoting Starters, Bench, and DNP, then writes the data to
`nba.games_lineups` in the DB. (~2 hours)

[scraping.plays_raw.py](data/scraping/plays.py) - this scrapes the raw play-by-play rows from
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
  
* Fix performance testing in [performance.py](utils/performance.py)
  
* Re-do betting odds scraping
  
* Add ejections to [cleaning.plays.py](data/cleaning/plays.py)
  
* Access [NBA stats](http://stats.nba.com) for shot information (location, type, defenders)

* Set up central control to build dataset from one script
  
* Move scraping to use [nba.com](http://nba.com) - this is likely to be slower, but should be more accurate, so I manual fixes
can be reduced and is probably also a bit more 'official'

* Set up automated daily ingestion of data

* Convert `get_session` and pre-execution table clearing/iteration skipping into a
  [function](utils/functions.py)
  
* Set up API to access database from Python

* Set up UI for exploration of data

### Bug Log


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

[scraping.lineups](data/scraping/lineups.py) - gets all player logs from `playergamelogs`, then inserts them into
`nba.lineups` (~10 seconds)

[scraping.plays_raw.py](data/scraping/plays.py) - this scrapes the raw play-by-play rows from
`playbyplayv2` for all game_id that appear within both the nba.games table, and the date range defined in
[params.py](utils/params.py), then writes the data to `nba.plays`. (20 minutes)

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
  
* Set up look-up table for EVENTMSGACTIONTYPE (for shots, where EVENTMSGTYPE == 1)

* Update query generators in [connections.py](utils/connections.py)
  
* Fix performance testing in [performance.py](utils/performance.py)
  
* Find solution for Starter/Bench/DNP designation in [scraping.lineups](data/scraping/lineups.py)

* Re-do betting odds scraping
  
* Access [NBA stats](http://stats.nba.com) for shot information (location, type, defenders)

* Set up central control to build dataset from one script
  
* Set up automated daily ingestion of data
  
* Set up API to access database from Python

* Set up UI for exploration of data

### Issue Log
[cleaning.plays.py](data/cleaning/plays.py)
* there are a large number of 'Instant Replay' events at the end of quarters
* a handful of empty events in most seasons, mostly due to missing information (e.g. team/player/event) - there don't
appear to be any consistent rules that can be applied to fix these
* there are some inconsistencies between points scored from plays and points from `nba.games`, although these issues
appear to come from the nba endpoints

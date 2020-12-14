# Modelling
## NBA Package
### Instructions
#### Terminal
If running virtual environment (venv), initiate with

`venv\Scripts\activate`

then check that Python Interpreter is located at  ~\ProjectName\venv\Scripts\python.exe

Next change the working directory to modelling folder

`cd modelling`

then install all requirements

`pip install -r requirements.txt`

The project should now be set up and ready to run and interact with GitHub

#### Setting up the DB
By default, this project has been set up to work with MySQL databases.  All the SQL connections are defined at 
[connections.py](projects/nba/utils/connections.py).

The connection parameters can be adjusted at [environment.py](projects/nba/utils/environment.py).

The `write_data`, `load_data` and `initialise_df` functions have been defined at [functions.py](projects/nba/utils/functions.py)
and will need to be adjusted  if another DB is to be used.

#### Setting up the Data
To ensure everything runs smoothly, the modules should be run in the following order:

[teams.py](projects/nba/data/cleaning/teams.py) - this automatically writes all team data defined in
[classes.py](projects/nba/utils/classes.py) to `nba.teams` in the DB.

[scraping.games.py](projects/nba/data/scraping/games.py) - this scrapes daily score data from Basketball Reference 
within the date range defined in [params.py](projects/nba/utils/params.py) and writes the data to `nba.games` in the DB.

[scraping.plays.py](projects/nba/data/scraping/plays.py) - this scrapes the raw play-by-play rows from Basketball
Reference for all games that appear within both the nba.games table, and the date range defined in
[params.py](projects/nba/utils/params.py), then writes the data to `nba_raw.plays_raw` in the DB

[scraping.odds.py](projects/nba/data/scraping/odds.py) - this scrapes game odds from
[oddsportal](https://www.oddsportal.com/) on a season by season basis (set in
[params.py](projects/nba/utils/params.py)) for seasons existing in `nba.games`, then writes the data to `nba.odds` in
the DB.

#### Currently planned upgrades
*Note: all data and modelling files that are not listed above are currently not in use.*
* Cleaning the plays data
* Analysing Player and Team performance
* Predicting game probabilities

#### Current Bugs to Fix
* Make Team-based code adaptable for changes in team names
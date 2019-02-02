# Modeling
## NBA Package
### Process
#### Modules to run
To use this package, run the modules in the following order:

**1. espn.py** - This module is used to scrape daily score data from the ESPN scoreboard website.
				 Note that data prior to the 2014/15 season does not currently load cleanly due to failure to
				 cleanly scrape Charlotte Bobcats data (probably due to the name change).
				 This uncleaned dataset is output as a gamedata_raw.
				 
**2. odds.py** - This module is used to scrape odds data (USD) for each game from the 'Odds Portal' website.

**3. cleaning.py** - This module is used to clean the data provided into a usable format (e.g. cleaning up
					 Home/Away Record variables, and combining odds data to the dataset). This pulls
					 output created by the 'Cleaning Modules'. This cleaned dataset is output as gamedata.

**4. modeling packages** - These modules used to take the final output gamedata and train models on
						   selected dates (currently recommended to train on 2014-2017 season data,
						   and test on 2018 season).
					 
**5. api.py** - This module creates the API to be hosted on server for ingesting match data (json) and
				return prediction of result.

**6. ui.py** - This module creates a UI capable of indepently communicating with the API. This module should
			   be built with the capability to run independently of the other modules

#### Cleaning modules
**1. gamelog.py** - This module is used to create a game-by-game log for each time. This has largely been
					created to assist with calculation of variables in the core dataset

**2. coordinates.py** - This module is used to load teams/cities in a table and scrape the geographical
						coordinates for each team.

**3. standings.py** - This module is used to calculate the wins for each team for the prior season.
					  Note that the 2014 season performance has been manually loaded.

#### Other modules
**1. functions.py** - This module is used to create user-defined functions.

#### Other notes
Each module outputs to both a mysql connection (can be defined in the __init__ file), and a csv loaded into the
'output' folder contained within the package.

This package is mainly being used to develop some skills in coding Python and created self contained packages, as
well as ultimately creating an API/UI that can be shared. The final model itself is currently of lower priority.

#### Upgrades and Bugs/Issues to fix
##### Functionality upgrades
Develop data analytics 'dashboard' using box scores, player data and play-by-play data

Provide probabilities and odds/returns for each predicted game

~~Develop UI for interaction with API~~ this should be developed further for appearance and functionality

Allow for ingesting of csv format game data and prediction of games by day

When using apipredict function, update travel/rest numbers, and ensure that it is configured for model
type

##### Modeling upgrades
Possible predictors - ~~recent form, recent results between teams, last week travel, games last week,
offensive/defensive ratings, point differential~~, player data

~~Remove scraping of record from ESPN site - calculate this using the gamelog code~~

~~Allow for pulling entire season data and (safe) daily updates to data/model~~

~~Get historic odds data~~

Attempt different types of models; ~~SVM, RandomForest, XGBoost, ~~Neural Network, CART, C5.0

Incorporate probabilities into betting recommendations

##### Bug fixes and performance upgrades
~~Fix record (currently includes current game in calculating win %) and look into form calc~~

Create functions for more efficient code and clean up code (especially scraping and cleaning)

Clean up warnings: convert_objects, last year wins

~~Organise folders into dataset, modeling, output, and ui. Move data specific output to data folder,
model specific output to modeling folder, etc.~~

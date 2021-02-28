# FIND VALUE OF EACH PLAYER
from modelling.projects.nba import *  # import broadly used python packages
from modelling.projects.nba.utils import *  # import user defined utilities
from modelling.projects.nba.data import *  # import data specific packages
from modelling.projects.nba.data.analysis import *

# load games table to access game_ids
season_plays = load_data(df='season_plays',
                         sql_engine=engine,
                         meta=metadata)

print(season_plays)

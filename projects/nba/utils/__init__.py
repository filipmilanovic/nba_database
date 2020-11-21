""" Import functions for use in package """
import time  # used to calculate time lapsed when running
# from xgboost.sklearn import XGBClassifier # used for xg boost model
from projects.nba.utils.params import *
from projects.nba.utils.functions import *
from projects.nba.utils.colours import *

# Load connections
import pymysql  # used to interact with sql (namely, load csv)
from sqlalchemy import create_engine  # used to interact with sql (namely, upload csv)

# Set start time for calculating time lapsed
start_time = time.time()

# pymysql connection
connection = pymysql.connect(host='localhost',
                             port=3306,
                             user='root',
                             password='password',
                             database='nba')

# sqlalchemy engine
engine = create_engine("mysql://root:password@localhost/nba")

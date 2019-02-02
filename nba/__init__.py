""" Import functions for use in package """
from datetime import datetime, date, timedelta # used for date data cleaning
import time # used to calculate time lapsed when running
import re # used for regular expression data cleaning
import pandas as pd # used for dataframe creation and manipulation
import numpy as np # used for array manipulation
from geopy.distance import vincenty # used to calculate distances between cities
from sklearn import svm, ensemble, metrics, preprocessing # used for model building
from xgboost.sklearn import XGBClassifier # used for xg boost model
import pickle # used for saving model object
from flask import Flask, request, json # used for api creation
import requests as r # used to send requests to api
from pathlib import Path # used to set root path
from nba.params import * # @UnresolvedImport
from threading import Thread

### Load connections
from selenium import webdriver # used to interact with webpage
import pymysql # used to interact with sql (namely, load csv)
from sqlalchemy import create_engine # used to interact with sql (namely, upload csv)

# Set start time for calculating time lapsed
START_TIME = time.time()

## Create root path
p = str(Path(__file__).parents[0]).replace('\\', '/')

## pymysql connection
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='espn')

## sqlalchemy engine
# engine = create_engine("mysql+mysqlconnector://root:password@localhost/espn")

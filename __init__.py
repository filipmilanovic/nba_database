# IMPORTING OVERALL SYSTEM VARIABLES
import sys
import threading
import concurrent.futures
from multiprocessing import Process, Manager, Queue
import pandas as pd
import numpy as np
import time  # used to calculate time lapsed when running
from datetime import datetime as dt
import re
from ordered_set import OrderedSet

# stop SettingWithCopyWarning error
pd.options.mode.chained_assignment = None

# show up to 15 columns when viewing DataFrames
pd.set_option('display.max_columns', 15)

# Set start time for calculating time lapsed
start_time = time.time()

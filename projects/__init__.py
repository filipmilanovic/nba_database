# IMPORTING OVERALL SYSTEM VARIABLES
import os  # used for system variables
from pathlib import Path  # used for setting up directory
from datetime import datetime as dt
import time  # used to calculate time lapsed when running
import timeit
import pandas as pd

# Create root path
ROOT_DIR = Path(__file__).parent.parent

# Set start time for calculating time lapsed
start_time = time.time()

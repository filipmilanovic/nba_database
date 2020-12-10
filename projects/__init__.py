# IMPORTING OVERALL SYSTEM VARIABLES
import os  # used for system variables
from pathlib import Path  # used for setting up directory
import time  # used to calculate time lapsed when running

# Create root path
ROOT_DIR = Path(__file__).parent.parent

# Set start time for calculating time lapsed
start_time = time.time()

from utils import *
import numpy as np
from bs4 import BeautifulSoup
import re
import threading
import concurrent.futures
from multiprocessing import Process, Manager
from ordered_set import OrderedSet

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' \
             '89.0.4389.90 Safari/537.36'

# stop SettingWithCopyWarning error
pd.options.mode.chained_assignment = None

# show up to 15 columns when viewing DataFrames
pd.set_option('display.max_columns', 15)

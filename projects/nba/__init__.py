from projects import *  # high level packages
from pathlib import Path  # used for root directory
import pandas as pd
from sqlalchemy import create_engine, exc  # used to interact with MySQL

# Set working base path for project
p = Path(__file__).parent

# Set up MySQL Connection
engine = create_engine('mysql://' + os.environ['user'] + ':' + os.environ['password']
                       + '@' + os.environ['host'] + '/' + os.environ['database'])

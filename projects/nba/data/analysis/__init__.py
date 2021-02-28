from modelling.projects import pd
from modelling.projects.nba.utils import connections, environment, functions

engine, metadata, connection = connections.get_connection(environment.database_analysis)

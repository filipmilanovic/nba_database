""" Defining team data """
from projects.nba import *

teams_df = pd.DataFrame.from_records([t.to_dict() for t in teams])

# attempt to write to sql
try:
    teams_df.to_sql('teams', con=engine, schema='nba', if_exists='replace')
    status_sql = Colour.green + 'Successfully written to MySQL Database!' + Colour.end
except sql.exc.OperationalError:
    status_sql = Colour.red + 'Failed to write to DB!' + Colour.end

print(Colour.green + 'Team Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

# CONVERTING TEAMS TO DATAFRAME
from modelling.projects.nba import *

if __name__ == '__main__':
    # Get teams from class objects
    teams = pd.DataFrame.from_records([team.to_dict() for team in Team.instances])

    create_table_teams()

    # write to SQL and CSV
    write_data(df=teams,
               name='teams',
               to_csv=True,
               sql_engine=engine,
               db_schema='nba',
               if_exists='append',
               index=False)

    print(Colour.green + 'Team Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

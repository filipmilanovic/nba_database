# CONVERTING TEAMS TO DATAFRAME
from utils import *

if __name__ == '__main__':
    engine, metadata, connection = get_connection(database)

    create_table_teams(metadata)

    # Get teams from class objects
    teams = pd.DataFrame.from_records([team.to_dict() for team in Team.instances])

    # write to SQL and CSV
    write_data(df=teams,
               name='teams',
               sql_engine=engine,
               db_schema='nba',
               if_exists='append',
               index=False)

    print(Colour.green + 'Team Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

""" Defining team data """
from projects.nba import *

games = load_games()

temp = sorted(set(games.home_team))

#  define teams dictionary
teams = {'team_name': temp,
         'short_name': ['ATL',
                        'BOS',
                        'BRK',
                        'CHO',
                        'CHI',
                        'CLE',
                        'DAL',
                        'DEN',
                        'DET',
                        'GSW',
                        'HOU',
                        'IND',
                        'LAC',
                        'LAL',
                        'MEM',
                        'MIA',
                        'MIL',
                        'MIN',
                        'NOP',
                        'NYK',
                        'OKC',
                        'ORL',
                        'PHI',
                        'PHO',
                        'POR',
                        'SAC',
                        'SAS',
                        'TOR',
                        'UTA',
                        'WAS'],
         'coordinates': ['(33.757222, -84.396389)',
                         '(42.366303, -71.062228)',
                         '(40.68265, -73.974689)',
                         '(35.225, -80.839167)',
                         '(41.880556, -87.674167)',
                         '(41.496389, -81.688056)',
                         '(32.790556, -96.810278)',
                         '(39.748611, -105.0075)',
                         '(42.696944, -83.245556)',
                         '(37.768056, -122.3875)',
                         '(29.750833, -95.362222)',
                         '(39.763889, -86.155556)',
                         '(34.043056, -118.267222)',
                         '(34.043056, -118.267222)',
                         '(35.138333, -90.050556)',
                         '(25.781389, -80.188056)',
                         '(43.043611, -87.916944)',
                         '(44.979444, -93.276111)',
                         '(29.948889, -90.081944)',
                         '(40.750556, -73.993611)',
                         '(35.463333, -97.515)',
                         '(28.539167, -81.383611)',
                         '(39.901111, -75.171944)',
                         '(33.445833, -112.071389)',
                         '(45.531667, -122.666667)',
                         '(38.649167, -121.518056)',
                         '(29.426944, -98.4375 )',
                         '(43.643333, -79.379167)',
                         '(40.768333, -111.901111)',
                         '(38.898056, -77.020833)']
         }

teams = pd.DataFrame(teams, columns=['team_name', 'short_name', 'coordinates'])

# attempt to write to csv
try:
    teams.to_csv(str(p) + '/data/output/teams.csv', sep=',')
    status_csv = Colour.green + 'Successfully written to csv!' + Colour.end
except FileNotFoundError:
    status_csv = Colour.red + 'Failed to write to CSV! (Path does not exist)' + Colour.end
except PermissionError:
    status_csv = Colour.red + 'Failed to write to CSV! (File already opened)' + Colour.end

# attempt to write to sql
try:
    teams.to_sql('teams', con=engine, schema='nba', if_exists='replace')
    status_sql = Colour.green + 'Successfully written to MySQL Database!' + Colour.end
except sql.exc.OperationalError:
    status_sql = Colour.red + 'Failed to write to DB!' + Colour.end

print(Colour.green + 'Team Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
      + ' seconds taken' + Colour.end)

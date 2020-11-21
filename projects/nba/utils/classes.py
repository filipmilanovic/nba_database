""" Define key classes"""


# Define base Team class
class Team:
    def __init__(self,
                 name,
                 short_name,
                 coordinates):
        self.name = name
        self.short_name = short_name
        self.coordinates = coordinates

    def to_dict(self):
        return {
            'name': self.name,
            'short_name': self.short_name,
            'coordinates': self.coordinates
        }


# Generate empty list for Teams
teams = list([])

# Create list of teams
teams.append(Team('Atlanta Hawks', 'ATL', '(33.757222, -84.396389)'))
teams.append(Team('Boston Celtics', 'BOS', '(42.366303, -71.062228)'))
teams.append(Team('Brooklyn Nets', 'BRK', '(40.68265, -73.974689)'))
teams.append(Team('Charlotte Bobcats', 'CHO', '(35.225, -80.839167)'))
teams.append(Team('Chicago Bulls', 'CHI', '(41.880556, -87.674167)'))
teams.append(Team('Cleveland Cavaliers', 'CLE', '(41.496389, -81.688056)'))
teams.append(Team('Dallas Mavericks', 'DAL', '(32.790556, -96.810278)'))
teams.append(Team('Denver Nuggets', 'DEN', '(39.748611, -105.0075)'))
teams.append(Team('Detroit Pistons', 'DET', '(42.696944, -83.245556)'))
teams.append(Team('Golden State Warriors', 'GSW', '(37.768056, -122.3875)'))
teams.append(Team('Houston Rockets', 'HOU', '(29.750833, -95.362222)'))
teams.append(Team('Indiana Pacers', 'IND', '(39.763889, -86.155556)'))
teams.append(Team('Los Angeles Clippers', 'LAC', '(34.043056, -118.267222)'))
teams.append(Team('Los Angeles Lakers', 'LAL', '(34.043056, -118.267222)'))
teams.append(Team('Memphis Grizzlies', 'MEM', '(35.138333, -90.050556)'))
teams.append(Team('Miami Heat', 'MIA', '(25.781389, -80.188056)'))
teams.append(Team('Milwaukee Bucks', 'MIL', '(43.043611, -87.916944)'))
teams.append(Team('Minnesota Timberwolves', 'MIN', '(44.979444, -93.276111)'))
teams.append(Team('New Orleans Pelicans', 'NOP', '(29.948889, -90.081944)'))
teams.append(Team('New York Knicks', 'NYK', '(40.750556, -73.993611)'))
teams.append(Team('Oklahoma City Thunder', 'OKC', '(35.463333, -97.515)'))
teams.append(Team('Orlando Magic', 'ORL', '(28.539167, -81.383611)'))
teams.append(Team('Philadelphia 76ers', 'PHI', '(39.901111, -75.171944)'))
teams.append(Team('Phoenix Suns', 'PHO', '(33.445833, -112.071389)'))
teams.append(Team('Portland Trailblazers', 'POR', '(45.531667, -122.666667)'))
teams.append(Team('Sacramento Kings', 'SAC', '(38.649167, -121.518056)'))
teams.append(Team('San Antonio Spurs', 'SAS', '(29.426944, -98.4375 )'))
teams.append(Team('Toronto Raptors', 'TOR', '(43.643333, -79.379167)'))
teams.append(Team('Utah Jazz', 'UTA', '(40.768333, -111.901111)'))
teams.append(Team('Washington Wizards', 'WAS', '(38.898056, -77.020833)'))

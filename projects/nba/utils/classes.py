# DEFINE KEY CLASSES


# Define base Team class
class Team:
    instances = []
    team_ids = []
    names = []
    full_names = []
    coordinates = []

    def __init__(self,
                 team_id,
                 name,
                 full_name,
                 coordinates):
        self.__class__.instances.append(self)

        self.team_id = team_id
        self.__class__.team_ids.append(team_id)

        self.name = name
        self.__class__.names.append(name)

        self.full_name = full_name
        self.__class__.full_names.append(full_name)

        self.coordinates = coordinates
        self.__class__.coordinates.append(coordinates)

    def to_dict(self):
        return {
            'team_id': self.team_id,
            'name': self.name,
            'full_name': self.full_name,
            'coordinates': self.coordinates
        }


# Create objects of class Team
Team('ATL', 'Atlanta', 'Atlanta Hawks', '(33.757222, -84.396389)')
Team('BOS', 'Boston', 'Boston Celtics', '(42.366303, -71.062228)')
Team('BRK', 'Brooklyn', 'Brooklyn Nets', '(40.68265, -73.974689)')
Team('CHO', 'Charlotte', 'Charlotte Bobcats', '(35.225, -80.839167)')
Team('CHI', 'Chicago', 'Chicago Bulls', '(41.880556, -87.674167)')
Team('CLE', 'Cleveland', 'Cleveland Cavaliers', '(41.496389, -81.688056)')
Team('DAL', 'Dallas', 'Dallas Mavericks', '(32.790556, -96.810278)')
Team('DEN', 'Denver', 'Denver Nuggets', '(39.748611, -105.0075)')
Team('DET', 'Detroit', 'Detroit Pistons', '(42.696944, -83.245556)')
Team('GSW', 'Golden State', 'Golden State Warriors', '(37.768056, -122.3875)')
Team('HOU', 'Houston', 'Houston Rockets', '(29.750833, -95.362222)')
Team('IND', 'Indiana', 'Indiana Pacers', '(39.763889, -86.155556)')
Team('LAC', 'LA Clippers', 'Los Angeles Clippers', '(34.043056, -118.267222)')
Team('LAL', 'LA Lakers', 'Los Angeles Lakers', '(34.043056, -118.267222)')
Team('MEM', 'Memphis', 'Memphis Grizzlies', '(35.138333, -90.050556)')
Team('MIA', 'Miami', 'Miami Heat', '(25.781389, -80.188056)')
Team('MIL', 'Milwaukee', 'Milwaukee Bucks', '(43.043611, -87.916944)')
Team('MIN', 'Minnesota', 'Minnesota Timberwolves', '(44.979444, -93.276111)')
Team('NOP', 'New Orleans', 'New Orleans Pelicans', '(29.948889, -90.081944)')
Team('NYK', 'New York', 'New York Knicks', '(40.750556, -73.993611)')
Team('OKC', 'Oklahoma City', 'Oklahoma City Thunder', '(35.463333, -97.515)')
Team('ORL', 'Orlando', 'Orlando Magic', '(28.539167, -81.383611)')
Team('PHI', 'Philadelphia', 'Philadelphia 76ers', '(39.901111, -75.171944)')
Team('PHO', 'Phoenix', 'Phoenix Suns', '(33.445833, -112.071389)')
Team('POR', 'Portland', 'Portland Trailblazers', '(45.531667, -122.666667)')
Team('SAC', 'Sacramento', 'Sacramento Kings', '(38.649167, -121.518056)')
Team('SAS', 'San Antonio', 'San Antonio Spurs', '(29.426944, -98.4375 )')
Team('TOR', 'Toronto', 'Toronto Raptors', '(43.643333, -79.379167)')
Team('UTA', 'Utah', 'Utah Jazz', '(40.768333, -111.901111)')
Team('WAS', 'Washington', 'Washington Wizards', '(38.898056, -77.020833)')

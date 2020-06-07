from nba import *

#### THIS IS STILL BROKEN THE LONGITUDE/LATITUDE NUMBERS ARE NOT YET RIGHT

print('Getting coordinates ' + str(time.time() - start_time))
# set up mysql connection and load teams table
names = '76ers', 'Bucks', 'Bulls', 'Cavaliers', 'Celtics', 'Clippers', 'Grizzlies', 'Hawks', 'Heat',\
    'Hornets', 'Jazz', 'Kings', 'Knicks', 'Lakers', 'Magic', 'Mavericks', 'Nets', 'Nuggets', 'Pacers',\
    'Pelicans', 'Pistons', 'Raptors', 'Rockets', 'Spurs', 'Suns', 'Thunder', 'Timberwolves', 'Trail Blazers',\
    'Warriors', 'Wizards'

cities = 'Philadelphia', 'Milwaukee', 'Chicago', 'Cleveland', 'Boston', 'Los Angeles', 'Memphis', 'Atlanta',\
    'Miami', 'Charlotte', 'Salt Lake City', 'Sacramento', 'New York', 'Los Angeles', 'Orlando', 'Dallas',\
    'Brooklyn', 'Denver', 'Indianapolis', 'New Orleans', 'Detroit', 'Toronto', 'Houston', 'San Antonio',\
    'Phoenix', 'Oklahoma City', 'Minnesota', 'Portland', 'Oakland', 'Washington DC',

    
teams = 'Philadelphia 76ers', 'Milwaukee Bucks', 'Chicago Bulls', 'Cleveland Cavaliers', 'Boston Celtics',\
'Los Angeles Clippers', 'Memphis Grizzlies', 'Atlanta Hawks', 'Miami Heat', 'Charlotte Hornets', 'Utah Jazz',\
'Sacramento Kings', 'New York Knicks', 'Los Angeles Lakers', 'Orlando Magic', 'Dallas Mavericks', 'Brooklyn Nets',\
'Denver Nuggets', 'Indiana Pacers', 'New Orleans Pelicans', 'Detroit Pistons', 'Toronto Raptors', 'Houston Rockets',\
'San Antonio Spurs', 'Phoenix Suns', 'Oklahoma City Thunder', 'Minnesota Timberwolves', 'Portland Trail Blazers',\
'Golden State Warriors', 'Washington Wizards'

# convert table to pandas dataframe
columns = 'TEAM', 'FULLNAME', 'CITY', 'LONGITUDE', 'LATITUDE'
coordinates = pd.DataFrame(columns = columns)
coordinates['TEAM'] = names
coordinates['FULLNAME'] = teams
coordinates['CITY'] = cities

# selenium driver
driver = webdriver.Chrome(executable_path="C:/Users/filip/PycharmProjects/modelling/venv/Scripts/chromedriver.exe")

# Connect to website
driver.get("https://www.google.com.au/maps")


for i in range(len(cities)):
    # enter name into search bar
    entry = driver.find_element_by_xpath("//*[@id='searchboxinput']")
    entry.clear()
    entry.click()
    entry.send_keys(cities[i])

    # click on search button
    search = driver.find_element_by_xpath("//*[@id='searchbox-searchbutton']")
    search.click()

    # grab url and coordinates
    time.sleep(3)
    url = str(driver.current_url)
    lng = url[url.find('@')+1:url.find('@')+11]
    lat = url[url.find('@')+12:url.find('@')+23]

    # put to table
    coordinates.loc[i, 'LONGITUDE'] = lng.replace(',','')
    coordinates.loc[i, 'LATITUDE'] = lat.replace(',','')
    print(cities[i])

print(coordinates)
coordinates.to_csv(p+'/data/output/coordinates.csv')
coordinates.to_sql('coordinates', con=engine, schema='nba', if_exists='replace')

driver.close()

print('Loaded coordinates ' + str(time.time() - start_time))

# put to table
#coordinates = dict()
#coordinates[i] = {lng + ', ' + lat}
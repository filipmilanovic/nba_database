from nba import *

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
columns = 'Team', 'FullTeam', 'City', 'Coordinates'
location = pd.DataFrame(columns = columns)
location['Team'] = names
location['FullTeam'] = teams
location['City'] = cities

## selenium driver
driver = webdriver.Chrome(executable_path="C:/Program Files (x86)/Python/Python36/Scripts/chromedriver.exe")

# Connect to website
driver.get("https://www.latlong.net/")

for i in range(len(location)):
    entry = driver.find_element_by_xpath("/html/body/main/div[1]/div[1]/form[1]/input")
    entry.clear()
    entry.click()
    entry.send_keys(location.loc[i,'City'])
        
    find = driver.find_element_by_xpath("/html/body/main/div[1]/div[1]/form[1]/button")
    find.click()
    
    time.sleep(2)
    coord = driver.find_element_by_xpath("//*[@id='latlongmap']/div/div/div[1]/div[3]/div[2]/div[4]/div/div[2]/div[1]/div")
    location.loc[i,'Coordinates'] = coord.text

location.to_csv(p+'/data/output/location.csv')
location.to_sql('location', con=engine, schema='espn', if_exists='replace')
print('Loaded coordinates ' + str(time.time() - start_time))
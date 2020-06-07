### SCRAPING GAME DATA FROM ESPN ###

from nba import *

# selenium driver
driver = webdriver.Chrome(executable_path="C:/Users/filip/PycharmProjects/modelling/venv/Scripts/chromedriver.exe")

# website if fail
# driver.get("http://www.espn.com.au/nba/scoreboard/_/date/20171113")

# set up basic dataframe
columns = ['DATE', 'HOME_TEAM', 'HOME_SCORE', 'AWAY_TEAM', 'AWAY_SCORE']
data = pd.DataFrame(columns=columns)

# pick up date range from parameters
date_range = pd.date_range(start_date_scrape, end_date_scrape) # @UnresolvedImport

# connect to website
driver.get("http://www.espn.com.au/nba/scoreboard/_/date/"+str(start_date_scrape.strftime('%Y%m%d')))

# wait for page to load
time.sleep(3)

# accept cookie banner
try:
    cookie = driver.find_element_by_xpath("//*[text()='Accept Cookies']")
    cookie.click()
except Exception:
    pass

# wait for page to load
time.sleep(5)

# load data when fail
data = pd.read_csv(p+'/data/output/gamedata_raw.csv')
del data['Unnamed: 0']
data['DATE'] = pd.to_datetime(data['DATE']).dt.date
data = data[(data.DATE > end_date_scrape) | (data.DATE < start_date_scrape)]

# loop through the days
for i in range(len(date_range)):
    # clear out daily data frame and select next date
    daily = pd.DataFrame(columns=columns)
    day = driver.find_element_by_css_selector("[data-id=\'%s\']" % str(date_range[i].strftime('%Y%m%d')))
    day.click()

    # wait for page to load
    time.sleep(5)

    # grab each of the elements
    try:
        hteams = driver.find_elements_by_xpath("//*[@class='home']/td[1]/div[2]/h2")
        for j in range(len(hteams)):
            daily.loc[j, 'DATE'] = str(date_range[i].strftime('%Y-%m-%d'))
            daily.loc[j, 'HOME_TEAM'] = hteams[j].text
        
        hscore = driver.find_elements_by_xpath("//*[@class='home']/td[@class='total']/span[1]")
        for j in range(len(hscore)):
            daily.loc[j, 'HOME_SCORE'] = hscore[j].text
            
        ateams = driver.find_elements_by_xpath("//*[@class='away']/td[1]/div[2]/h2")
        for j in range(len(ateams)):
            daily.loc[j, 'AWAY_TEAM'] = ateams[j].text
            
        ascore = driver.find_elements_by_xpath("//*[@class='away']/td[@class='total']/span[1]")
        for j in range(len(ascore)):
            daily.loc[j, 'AWAY_SCORE'] = ascore[j].text
    except Exception:
        pass

    # output to csv
    data = data.append(daily)
    data['DATE'] = pd.to_datetime(data['DATE']).dt.date
    data = data.sort_values(by = 'DATE', ascending=True)
    data.to_csv(p+'/data/output/gamedata_raw.csv', sep = ',')
    
    # show latest date and time lapsed
    print(str(date_range[i].strftime('%Y-%m-%d')) + ' ' + str(time.time() - start_time))

driver.close()
print('Raw Data Loaded')

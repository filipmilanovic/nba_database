from nba import *
## selenium driver
driver = webdriver.Chrome(executable_path="C:/Users/filip/Anaconda3/Scripts/chromedriver.exe")

# website if fail
# driver.get("http://www.espn.com.au/nba/scoreboard/_/date/20171113")

# set up basic dataframe
columns = ['Date', 'Home Team', 'Home Score', 'Away Team', 'Away Score']#, 'Home Record', 'Away Record']
data = pd.DataFrame(columns=columns)

# set up date range
#start_date = date(2018, 1, 30)
#end_date = date(2018, 1, 30) # recommended date(2014, 7, 1)
daterange = pd.date_range(end_date, start_date) # @UnresolvedImport
daterange = pd.Index(reversed(daterange))

# Connect to website
driver.get("http://www.espn.com.au/nba/scoreboard/_/date/"+str(start_date.strftime('%Y%m%d')))

# load data when fail
data = pd.read_csv(p+'/data/output/gamedata_raw.csv')
del data['Unnamed: 0']
data['Date'] = pd.to_datetime(data['Date']).dt.date
data = data[(data.Date < end_date) | (data.Date > start_date)]

#loop through the days
for i in range(len(daterange)):
    # clear out daily data frame and select next date
    daily = pd.DataFrame(columns=columns)
    
    day = driver.find_element_by_css_selector("[data-id=\"%s\"]" % str(daterange[i].strftime('%Y%m%d')))
    day.click()
    
    # wait for page to load
    time.sleep(5)
    
    try:
        hteams = driver.find_elements_by_xpath("//*[@class='home']/td[1]/div[2]/h2")
        for j in range(len(hteams)):
            daily.loc[j, 'Date'] = str(daterange[i].strftime('%Y-%m-%d'))
            daily.loc[j, 'Home Team'] = hteams[j].text
        
        hscore = driver.find_elements_by_xpath("//*[@class='home']/td[@class='total']/span[1]")
        for j in range(len(hscore)):
            daily.loc[j, 'Home Score'] = hscore[j].text
            
        ateams = driver.find_elements_by_xpath("//*[@class='away']/td[1]/div[2]/h2")
        for j in range(len(ateams)):
            daily.loc[j, 'Away Team'] = ateams[j].text
            
        ascore = driver.find_elements_by_xpath("//*[@class='away']/td[@class='total']/span[1]")
        for j in range(len(ascore)):
            daily.loc[j, 'Away Score'] = ascore[j].text
           
        #hrec = driver.find_elements_by_xpath("//*[@class='home']/td[1]/div[2]/div/p[@class='record']")
        #for j in range(len(hrec)):
        #    daily.loc[j, 'Home Record'] = hrec[j].text
        #
        #arec = driver.find_elements_by_xpath("//*[@class='away']/td[1]/div[2]/div/p[@class='record']")
        #for j in range(len(arec)):
        #    daily.loc[j, 'Away Record'] = arec[j].text
    except Exception:
        pass

    # output to csv
    data = data.append(daily)
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data = data.sort_values(by = 'Date', ascending=True)
    data.to_csv(p+'/data/output/gamedata_raw.csv', sep = ',')
    
    # show latest date and time lapsed
    print(str(daterange[i].strftime('%Y-%m-%d')) + ' ' + str(time.time() - start_time))

driver.close()
print('Raw Data Loaded')
from nba import *

#from selenium.webdriver.common.keys import Keys
type = 'fix'

if type == 'update':
    start_date = date(2018,4,12)
    end_date = date(2018,4,12)
elif type == 'fix':
    start_date = date(2018,3,11)
    end_date = start_date
    
def tabscrape(i, date):
    globals()['driver%s' % i] = webdriver.Firefox(executable_path="C:/Users/filip/Anaconda3/Scripts/geckodriver.exe")
    eval("driver%s.get(games[i].get_attribute('href'))" % i)
    try:
        widescreen = eval("driver%s" % i).find_element_by_xpath("//*[contains(text(), 'Widescreen')]")
        widescreen.click()
    except Exception:
        pass
    globals()['temp%s' % i] = pd.Series(eval("driver%s.find_elements_by_css_selector('[data-row]')" % i))
    globals()['plays%s' % i] = pd.DataFrame(columns = ('Date', 'Home Team', 'Away Team', 'Plays'))
    globals()['plays%s' % i]['Plays'] = pd.Series(eval('temp%s' % i)[j].text for j in range(len(eval('temp%s' % i))))
    globals()['plays%s' % i]['Date'] = date
    globals()['plays%s' % i]['Home Team'] = eval('temp%s' % i)[1].text[0:3]
    globals()['plays%s' % i]['Away Team'] = eval('temp%s' % i)[0].text[0:3]
    eval("driver%s.close()" % i)

#plays = pd.DataFrame(columns = ('Date', 'Home Team', 'Away Team', 'Plays'))
plays = pd.read_csv(p+'/data/output/plays_raw.csv', sep = ',')
del plays['Unnamed: 0']
plays['Date'] = pd.to_datetime(plays['Date']).dt.date

if type == 'update':
    plays = plays[plays.Date < start_date]
elif type == 'fix':
    plays = plays[plays.Date != start_date]

## selenium driver
driver = webdriver.Firefox(executable_path="C:/Users/filip/Anaconda3/Scripts/geckodriver.exe")

for i in pd.date_range(start_date, end_date):
    print(i.strftime('%Y-%m-%d'))
    driver.get("https://www.basketball-reference.com/boxscores/?month="+ \
           str(i.month)+"&day="+str(i.day)+"&year="+str(i.year))
    games = driver.find_elements_by_class_name("game_summary")
    games = driver.find_elements_by_xpath("//*[@class='links']/a[2]")
    for j in range(int(len(games))):
        globals()['thread%s' % j] = Thread(target = tabscrape, args = (j, i))
    print("Opening " + str(len(games)) + " threads " + str(time.time() - start_time))
    for j in range(len(games)):
        eval("thread%s.start()" % j)
        time.sleep(1)
    for j in range(len(games)):
        eval("thread%s.join()" % j)
    print("Closed threads " + str(time.time() - start_time))
    for j in range(len(games)):
        plays = plays.append(eval("plays%s" % j), ignore_index = True)
    plays.to_csv(p+'/data/output/plays_raw.csv', sep = ',')
    
#plays.to_csv(p+'/data/output/plays_raw.csv', sep = ',')
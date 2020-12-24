# SCRAPING PLAYER DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_player_id(url):
    output = re.search('players/\w/(.*).html', url).group(1)
    return output


def get_player_name(driver):
    output = driver.find_element_by_xpath('//*[@id="meta"]/div[2]/h1/span').text
    return output


# this gets used when get_player_name only returns one name, as we need the initial. surname format available
def get_player_name_exception(driver):
    # use Twitter as most players use twitter, so this should cover the limited number of edge cases
    raw = driver.find_element_by_partial_link_text("Twitter")
    parent = raw.find_element_by_xpath('..').text
    output = re.search('(.*) ▪', parent).group(1)
    return output


def get_player_short_name(x):
    output = left(x, 1) + '. ' + re.search(r' \b(.*)$', x).group(1)
    return output


def get_player_dob(driver):
    raw = driver.find_element_by_xpath('//*[@id="necro-birth"]').text
    dob = dt.strptime(raw, '%B %d, %Y')
    output = dob.strftime('%Y-%m-%d')
    return output


def get_player_height(driver):
    height = driver.find_element_by_xpath('//*[@itemprop="height"]').text
    inches = int(left(height, 1))*12 + int(re.search('-(\d+)', height).group(1))
    output = int(inches*2.54)
    return output


def get_player_weight(driver):
    weight = driver.find_element_by_xpath('//*[@itemprop="weight"]').text
    pounds = int(re.search('(\d+)lb', weight).group(1))
    output = int(pounds/2.205)
    return output


def get_player_hand(driver):
    # the line with position contains players shooting hand
    raw = driver.find_element_by_xpath("//*[contains(text(), 'Position:')]")
    parent = raw.find_element_by_xpath('..').text
    output = re.search('Shoots: ([A-z]+)', parent).group(1)
    return output


def get_player_position(driver):
    raw = driver.find_element_by_xpath("//*[contains(text(), 'Position:')]")
    parent = raw.find_element_by_xpath('..').text
    output = positions[re.search('Position: ([A-z]+)', parent).group(1)]
    return output


def get_players(df):
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    player_list = list([])

    # loop through team/season combinations and build a list of URLs for each player
    for i in range(len(df)):
        team = df.team[i]
        season = df.season[i]
        url = f'https://www.basketball-reference.com/teams/{team}/{season}.html'
        team_list = get_player_url_list(url, driver)
        player_list = player_list + team_list
        progress(iteration=i,
                 iterations=len(df),
                 iteration_name=f'{team} {season}',
                 lapsed=time_lapsed(),
                 sql_status='',
                 csv_status='')

    # make it a distinct list to save time
    player_list = pd.Series(sorted(list(set(player_list))))

    # skip players already in DB
    if SKIP_SCRAPED_PLAYERS:
        names = [re.search('players/[a-z]/(.*)\.html', x).group(1) for x in player_list]
        player_list = player_list[~pd.Series(names).isin(players.player_id)].reset_index(drop=True)

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Generated list of players' + Colour.end)

    get_player_data(player_list, driver)

    # return to regular output writing
    sys.stdout.write('\n')

    # close web driver
    driver.close()


def get_player_url_list(url, driver):
    driver.get(url)
    # look at all rows under roster for team and return href link
    player_list = driver.find_elements_by_xpath('//*[@id="roster"]/tbody/tr/td[1]/a')
    output = [x.get_attribute("href") for x in player_list if x.get_attribute("href")]
    return output


def get_player_data(array, driver):
    for i in range(len(array)):
        driver.get(array[i])

        # expand info button
        try:
            driver.find_element_by_xpath('//*[@id="meta_more_button"]').click()
        except NoSuchElementException:
            pass

        # build row for player, although currently possible exception where player has one name (e.g. Nene)
        try:
            player = [get_player_id(array[i]),  # player_id
                      get_player_name(driver),  # name
                      get_player_short_name(get_player_name(driver)),  # short_name
                      get_player_dob(driver),  # dob
                      get_player_height(driver),  # height
                      get_player_weight(driver),  # weight
                      get_player_hand(driver),  # hand
                      get_player_position(driver)  # position
                      ]
        except AttributeError:
            player = [get_player_id(array[i]),  # player_id
                      get_player_name_exception(driver),  # name
                      get_player_short_name(get_player_name_exception(driver)),  # short_name
                      get_player_dob(driver),  # dob
                      get_player_height(driver),  # height
                      get_player_weight(driver),  # weight
                      get_player_hand(driver),  # hand
                      get_player_position(driver)  # position
                      ]

        df = pd.DataFrame([player], columns=columns)

        try:
            connection_raw.execute(f'delete from nba.players where player_id = "{df.player_id.item()}"')
        except ProgrammingError:
            break

        status = write_data(df=df,
                            name='players',
                            to_csv=False,
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(array),
                 iteration_name=df.name.item(),
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])


if __name__ == '__main__':
    columns = ['player_id', 'name', 'short_name', 'dob', 'height', 'weight', 'hand', 'position']

    players = initialise_df(table_name='players',
                            columns=columns,
                            sql_engine=engine,
                            meta=metadata)

    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    team_season = pd.DataFrame({'team': games.home_team, 'season': games.season}).drop_duplicates().reset_index()

    get_players(team_season)

    print(Colour.green + 'Player Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

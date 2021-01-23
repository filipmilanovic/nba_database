# GET PLAYER_IDS ON THE COURT FOR EACH PLAY
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.utils import *
from modelling.projects.nba.data.scraping import *  # importing scraping for certain exceptions

# GENERATING LIST OF ON-COURT PLAYERS
# get players on the court in a key format by period
def get_on_court_player_ids(df):
    # set game_id
    game_id = df.game_id[0]

    # get list of game periods
    periods = set(df.period)

    # get teams and initialise series
    home_team = games.home_team[games.game_id == game_id].item()
    away_team = games.away_team[games.game_id == game_id].item()
    home_players = pd.Series(dtype='str')
    away_players = pd.Series(dtype='str')

    for i in periods:
        # get players from known plays data
        home_players_period = get_players_period(df, home_team, i)
        away_players_period = get_players_period(df, away_team, i)

        # check if 5 players on each team, and scrape from box scores if there is an issue
        home_players_period = check_on_court_data(home_players_period, home_team, game_id, i)
        away_players_period = check_on_court_data(away_players_period, away_team, game_id, i)

        # append players to base series
        home_players = home_players.append(home_players_period)
        away_players = away_players.append(away_players_period)

    # add full dataframe index, then fill in blanks for both teams
    home_players = home_players.reindex(range(len(df))).fillna(method='ffill').fillna(method='bfill')
    away_players = away_players.reindex(range(len(df))).fillna(method='ffill').fillna(method='bfill')

    # set players as players on court for given team_id, and opp_players as opposition
    players = home_players[df.team_id == home_team].append(away_players[df.team_id == away_team]).sort_index()
    opp_players = home_players[df.team_id == away_team].append(away_players[df.team_id == home_team]).sort_index()

    log_performance()
    return players, opp_players


# get the player_ids key for each play for a given team and period
def get_players_period(df, team, period):
    # save index for later use
    index = df[(df.team_id == team) & (df.period == period)].index

    # get team specific plays
    team_plays = df[(df.team_id == team) & (df.period == period)].reset_index(drop=True)

    # generate series of players by period
    players_period = []

    # firstly starting from the end and adding players who made plays
    for j in reversed(range(len(team_plays))):
        # initialise the series with the first player
        if j == len(team_plays) - 1:
            # leave blank if final play has no player_id (e.g. Team rebound)
            players = str(if_none(team_plays.player_id[j], '')) + '|'
        else:
            # add current row players by checking information and known players of last 2 plays
            players = get_player_array(team_plays[j:j+2], players_period[len(team_plays)-j-2], j)

        # append current row players to series
        players_period.append(players)

    # go back from start to end and fill down new information from each row to the next
    players_period = fill_down_players(players_period)

    # convert to series
    output = pd.Series(players_period)

    # re-index based on initial index of plays for the team
    output.index = index

    log_performance()
    return output


# get on court player list by adding new player to known list (this runs backwards)
def get_player_array(plays_info, previous_player_ids, iteration):
    play = plays_info.loc[iteration]

    # use previous play in the event of a substitution, and substitute player
    previous_play = plays_info.loc[iteration + 1]
    if previous_play.event == 'Substitution':
        previous_player_ids = re.sub(previous_play.player_id, previous_play.event_detail, previous_player_ids)

    # get list of players from the previous play
    players = extract_players(previous_player_ids)

    # sometimes players on the bench get a tech, so we will just exclude this
    if play.event == 'Technical foul':
        pass

    else:
        # add player if they are not in existing list
        try:
            if play.player_id not in previous_player_ids:
                players.append(play.player_id)
        except TypeError:
            pass

    # combine players back into player_id key
    output = convert_to_string(players)

    log_performance()
    return output


# turn on court player key to list of player_ids
def extract_players(x):
    output = [i for i in x.split('|') if i]

    log_performance()
    return output


# turn list of on court player_ids to key
def convert_to_string(x):
    # join first 4 players with separator
    players = [str(i) + '|' for i in x[0:4]]
    if len(x) == 5:
        # add final player without separator
        players += x[4]
    # join player_ids
    output = ''.join(players)

    log_performance()
    return output


# fill down list generated by get_player_array to flesh out each play to 5 players
def fill_down_players(array):
    array = list(reversed(array))
    for i in range(1, len(array)):
        # get list of players from each row
        play_list = extract_players(array[i])

        # find number of players
        play_players = len(play_list)

        # get list of players from previous row
        previous_play_list = extract_players(array[i-1])

        # compare number of players to previous row
        previous_play_players = len(previous_play_list)

        if previous_play_players > play_players:
            # check if current row of players shorter than previous row, then fill in missing positions
            missing = previous_play_list[play_players:previous_play_players+1]
            [play_list.append(i) for i in missing]

        # convert player list to player_id key
        array[i] = convert_to_string(play_list)

    log_performance()
    return array


# SCRAPING OF DATA WHEN MISSING PLAYERS
# check that each row has 5 players, as a player that plays a whole period with no contribution will not show up
def check_on_court_data(series, team_id, game_id, period):
    # checking
    check_result = on_court_player_check(series)
    output = series

    # if check results in fewer than 5 players, then get the missing players
    if check_result != 5:
        output = get_missing_players(series, team_id, game_id, period)

    # check if issue resolved
    check_updated = on_court_player_check(output)

    if check_updated != 5:
        print(f'Missing players in {period} period of {game_id}')
        exit()

    log_performance()
    return output


# check to ensure there are always 10 players on the court
def on_court_player_check(series):
    # generate empty series
    count_check = pd.Series(dtype=bool)

    # check number of players on court by counting number of 0 (player_id's to date all contain one 0)
    for i in series.index:
        count_check.loc[i] = series[i].count('0')

    # return minimum number of players found in list
    output = min(count_check)

    log_performance()
    return output


# if there are fewer than 5 players, then we need to find the missing players
def get_missing_players(series, team_id, game_id, period):
    # index for later re-indexation
    index = series.index

    # visit game box scores to figure out which players played in the desired period
    error = scrape_box_score(team_id, game_id, period)

    # check which player did not show up in the initial series of on-court players
    missing_index = [all([i not in j for j in series]) for i in error]

    # get missing player_id
    missing_player_id = error[missing_index]

    # add missing player to each row
    output = add_missing_player(series, missing_player_id)

    # match initial index
    output.index = index

    log_performance()
    return output


# interacting with basketball reference to get the box score data
def scrape_box_score(team_id, game_id, period):
    all_periods = 'Game', 'Q1', 'Q2', 'Q3', 'Q4', 'OT1', 'OT2', 'OT3', 'OT4'

    # calculate data missing in OT1 by difference between total game time and regulation game time
    periods = [i for i in all_periods if i != period_name[period]]
    if any(period == i for i in ['1st', '2nd', '3rd', '4th']):
        seconds = 720
    else:
        seconds = 300
    # Method not perfect, check later if issues arise

    # load website using index
    url = f"https://www.basketball-reference.com/boxscores/{game_id}.html"
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)
    driver.get(url)

    # get minutes by player by period
    player_minutes = get_player_minutes(driver, periods, team_id)

    # get minutes by player in desired period
    missing_period_minutes = get_missing_period_minutes(player_minutes, periods)

    # get players who played in the desired period
    output = player_minutes.loc[missing_period_minutes.between(seconds-1, seconds+2), 'player_id_Game']

    # close the driver
    driver.close()

    log_performance()
    return output


# get a DataFrame of number of minutes played by player by period
def get_player_minutes(driver, periods, team_id):
    player_minutes = pd.DataFrame()

    # for each of the desired periods, scrape player_ids and minutes
    for i in periods:
        # get the key for the box score
        box_key = get_box_key(team_id, i)

        # Only for periods that exist in the game
        try:
            # access the relevant box score by selecting the desired period
            click_period(driver, i)

            # get box score stats for the period
            player_minutes_period = get_box_score(driver, box_key)

            # convert column names to show which period
            player_minutes_period.columns = [f'player_id_{i}', f'minutes_{i}']

            # join together all periods
            player_minutes = pd.concat([player_minutes, player_minutes_period], axis=1)
        except IndexError:
            pass

    log_performance()
    return player_minutes


# get box score key to use for accessing correct box score
def get_box_key(team_id, period):
    output = 'box-' + team_id + '-' + period.lower() + '-basic'

    log_performance()
    return output


# click on the correct period in the box score screen on basketball reference
def click_period(driver, period):
    # scroll down the page so that the tabs show aren't covered by an ad
    driver.execute_script("window.scrollTo(0, 800);")

    # wait to ensure everything has loaded properly
    time.sleep(0.5)

    # get all tabs
    tabs = driver.find_elements_by_class_name('sr_preset')

    # select tab which matches desired period
    tab = [x for x in tabs if x.text == period][0]

    # click on tab to open desired period box score
    tab.click()

    log_performance()


# get the box score of a given period
def get_box_score(driver, key):
    # grab table based on box_score_key
    table = driver.find_element_by_id(key)

    # get table data from BeautifulSoup
    soup = BeautifulSoup(table.get_attribute('innerHTML'), 'html.parser')

    # want to scrape player_ids and number of minutes
    players_columns = ['player_id', 'minutes']

    # get player link and minutes for all players who played for the team
    output = pd.DataFrame([[x.findChild('th').findChild('a').get('href'), x.findChild('td').text]
                           for x in soup.find_all('tr')
                           if x.findChild('th').findChild('a') is not None
                           and 'Did Not' not in x.findChild('td').text],
                          columns=players_columns)

    # isolate player_id from href
    output.player_id = [re.search('players/[a-z]/(.*).html', i).group(1) for i in output.player_id]

    # replace empty minutes played with 0 and convert series to time
    output.minutes = [dt.strptime(i.replace('\xa0', '0:00'), '%M:%S').time() for i in output.minutes]

    log_performance()
    return output


# get the number of minutes played in desired period by calculating (as players with no plays are blank in pbp)
def get_missing_period_minutes(df, periods):
    # select only periods which exist
    n = int(len(df.columns)/2)
    periods = periods[:n]

    # convert seconds played into dataframe by player, by period
    minutes_played = pd.DataFrame([[get_seconds(i) for i in df[f'minutes_{periods[j]}']]
                                   for j in range(len(periods))],
                                  index=periods).transpose()

    # calculate the number of minutes the players played in the desired period
    output = minutes_played[periods[0]]

    for i in range(1, len(minutes_played.columns)):
        output -= minutes_played[periods[i]]

    log_performance()
    return output


# concatenate missing player_ids onto end of each row
def add_missing_player(series, player_id):
    try:
        # if multiple players, join by the '|' separator
        separator = '|'
        to_append = separator.join(player_id)
    except TypeError:
        # if only one player, append without separator
        to_append = player_id
    # loop through each row in the series
    output = pd.Series([i + to_append for i in series])

    log_performance()
    return output

# get players on the court for each play
        # on_court_players = get_on_court_player_ids(game_plays)

        # get players for given team_id
        # game_plays.players = on_court_players[0]

        # get opposition players for given team_id
        # game_plays.opp_players = on_court_players[1]

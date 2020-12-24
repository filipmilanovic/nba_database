# SCRAPING PLAY BY PLAY DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_game_id(df):
    short_date = pd.to_datetime(df.date).dt.strftime('%Y%m%d')
    short_name = [x for x in df.home_team]
    output = short_date + '0' + short_name
    return output


def get_starters(game, team, soup):
    game_id = [game] * 5
    team_id = [team] * 5
    player_id = [x.findChildren('th')[0].get('data-append-csv') for x in soup.find_all('tr')
                 if x.get('data-row') is not None and int(x.get('data-row')) < 5]
    role = ['Starter'] * 5
    output = pd.DataFrame({'game_id': game_id,
                           'team_id': team_id,
                           'player_id': player_id,
                           'role': role})
    return output


def get_bench(game, team, soup):
    player_id = [x.findChildren('th')[0].get('data-append-csv') for x in soup.find_all('tr')
                 if x.get('data-row') is not None and int(x.get('data-row')) > 5]
    players = len(player_id)-1
    game_id = [game] * players
    team_id = [team] * players

    dnp = ['DNP' for x in soup.find_all('tr') if len(x.findChildren('td')) == 1]

    role = ['Bench'] * (players - len(dnp)) + dnp

    output = pd.DataFrame({'game_id': game_id,
                           'team_id': team_id,
                           'player_id': pd.Series(player_id).dropna(),
                           'role': role})
    return output


def scrape_lineups(driver, game_id):
    output = pd.DataFrame(columns=columns)

    # get home team information
    home_team = right(game_id, 3)
    home_box = driver.find_element_by_xpath(f'//*[@id="div_box-{home_team}-game-basic"]')
    home_soup = BeautifulSoup(home_box.get_attribute('innerHTML'), 'html.parser')

    # get away team information
    away_team = games.away_team[games.game_id == game_id].item()
    away_box = driver.find_element_by_xpath(f'//*[@id="div_box-{away_team}-game-basic"]')
    away_soup = BeautifulSoup(away_box.get_attribute('innerHTML'), 'html.parser')

    output = output.append(get_starters(game_id, home_team, home_soup))  # home starters
    output = output.append(get_bench(game_id, home_team, home_soup))  # home bench
    output = output.append(get_starters(game_id, away_team, away_soup))  # away starters
    output = output.append(get_bench(game_id, away_team, away_soup))  # away bench

    return output


def get_lineups_data(iterations):
    # selenium driver
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    for i in range(len(iterations)):
        # load website using index
        driver.get("https://www.basketball-reference.com/boxscores/" + iterations[i] + ".html")

        game_lineups = scrape_lineups(driver, iterations[i])

        # game_lineups = pd.DataFrame(game_lineups, columns=['plays'])
        game_lineups['game_id'] = iterations[i]

        # clear rows where play data already exists
        try:
            connection_raw.execute(f'delete from nba.games_lineups where game_id = "{iterations[i]}"')
        except ProgrammingError:
            pass

        status = write_data(df=game_lineups,
                            name='games_lineups',
                            to_csv=False,
                            sql_engine=engine,
                            db_schema='nba',
                            if_exists='append',
                            index=False)

        progress(iteration=i,
                 iterations=len(iterations),
                 iteration_name=iterations[i],
                 lapsed=time_lapsed(),
                 sql_status=status['sql'],
                 csv_status=status['csv'])

    # return to regular output writing
    sys.stdout.write('\n')

    driver.close()


if __name__ == '__main__':
    # column names for plays_raw table
    columns = ['game_id', 'team_id', 'player_id', 'role']

    # get plays_raw dataframe from DB, or build from scratch
    games_lineups = initialise_df(table_name='games_lineups',
                                  columns=columns,
                                  sql_engine=engine,
                                  meta=metadata)

    # load games table to help set up loop
    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    # pick up date range from parameters
    date_range = pd.date_range(start_date_lineups, end_date_lineups)

    # load games in selected date range
    games = games.loc[games.date.isin(date_range.strftime('%Y-%m-%d'))].reset_index()

    # create game index for accessing website
    game_ids = get_game_id(games)

    # skip games that have already been scraped
    if SKIP_SCRAPED_DAYS:
        game_ids = game_ids[~game_ids.isin(games_lineups.game_id)]

    # get data and write to DB/CSV
    get_lineups_data(game_ids)

    print(Colour.green + 'Lineup Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)

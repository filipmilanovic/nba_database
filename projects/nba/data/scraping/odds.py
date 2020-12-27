# SCRAPING ODDS DATA

from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_max_page_number(driver):
    page_parent = driver.find_element_by_id("pagination")
    page_list = page_parent.find_elements_by_css_selector("*")
    pages = [x.get_attribute("href") for x in page_list if x.get_attribute("href")]
    page_numbers = [int(right(x, 3).replace('/', '')) for x in pages if right(x, 2) != "#/"]
    output = max(page_numbers)
    return output


def get_raw_rows(driver):
    # grab html data
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # set type of rows to be scraped (Date and game data)
    rows = ['center nob-border', 'odd deactivate', 'deactivate']

    # get raw text from html
    output = [x.getText() for x in soup.find_all('tr', {'class': rows})]
    return output


# Get game date for game_id
def get_raw_date(x):
    try:
        formatted_date = dt.strptime(x, '%d %b %Y')
        output = formatted_date.strftime('%Y%m%d')
    except ValueError:
        output = None
    return output


# Convert scraped date to Western US Time (note that odds portal timezone selection is unreliable)
def convert_date(df_1, df_2, x):
    try:
        formatted_datetime = dt.strptime(df_2[x] + left(df_1[x], 5), '%Y%m%d%H:%M')
        default_timezone = pytz.timezone("Etc/GMT")
        target_timezone = pytz.timezone("US/Pacific")
        updated_datetime = default_timezone.localize(formatted_datetime).astimezone(target_timezone)
        output = updated_datetime.strftime('%Y%m%d')
    except ValueError:
        output = None
    return output


# Get short team name for game_id
def get_short_name(x):
    try:
        output = Team.team_ids[Team.full_names.index(mid(x, 5, x.find('-') - 6))]
    except ValueError:
        output = None
    return output


def get_game_id(raw_df, dates):
    # get short name for home team for game_id
    short_names = [get_short_name(x) if mid(x, 2, 1) == ':' else None for x in raw_df]

    # get game_id
    output = pd.Series(dates) + '0' + pd.Series(short_names)
    return output


def get_scores(df):
    home_scores = df.game_id.map(games.set_index('game_id')['home_score'])
    away_scores = df.game_id.map(games.set_index('game_id')['away_score'])
    output = home_scores + ':' + away_scores
    return output


# Get odds for home team
def get_home_odds(df, scores, x):
    try:
        odds_data = right(df[x], len(df[x]) - df[x].find(scores[x]) - len(scores[x]))
        output = left(odds_data, odds_data.find('.') + 3)
    except TypeError:
        output = None
    return output


# Get odds for away team
def get_away_odds(df, scores, x):
    try:
        odds_data = right(df[x], len(df[x]) - df[x].find(scores[x]) - len(scores[x]))
        home_odds = left(odds_data, odds_data.find('.') + 3)
        trimmed_odds_data = right(odds_data, len(odds_data) - len(home_odds))
        output = left(trimmed_odds_data, trimmed_odds_data.find('.') + 3)
    except TypeError:
        output = None
    return output


def get_odds_data(seasons):
    # selenium driver
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    for i in seasons:
        # go to season page
        driver.get(f'https://www.oddsportal.com/basketball/usa/nba-{i-1}-{i}/results/')

        # clear rows where game already exists
        try:
            connection_raw.execute(f'delete from nba.odds where left(game_id, 8)*1 <= "{i}0630"'
                                   f'and left(game_id, 8)*1 >= {i-1}0701')
        except ProgrammingError:
            pass

        get_season_data(driver, i)

    driver.close()

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Odds Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)


def get_season_data(driver, season):
    page_number = 1
    max_page_number = get_max_page_number(driver)
    while True:
        try:
            # initialise df
            odds = pd.DataFrame(columns=columns)

            # get raw rows
            odds_raw = get_raw_rows(driver)

            # remove OT indicator
            odds_raw = pd.Series(odds_raw).str.replace('\sOT', '')

            # set a date for each row, then convert to Western US timezone
            odds_date_gmt = pd.Series([get_raw_date(left(x, 11)) for x in odds_raw]).fillna(method='ffill')
            odds_date = [convert_date(odds_raw, odds_date_gmt, i) for i in range(len(odds_raw))]

            # get game_ids
            odds.game_id = get_game_id(odds_raw, odds_date)

            # get game scores to help scrape from raw text
            scores = get_scores(odds)

            # get odds
            odds.home_odds = [get_home_odds(odds_raw, scores, x) for x in range(len(odds_raw))]
            odds.away_odds = [get_away_odds(odds_raw, scores, x) for x in range(len(odds_raw))]

            # drop rows where no game information exists
            odds = odds[odds['home_odds'].notna()]

            odds.home_odds = pd.to_numeric(odds.home_odds)
            odds.away_odds = pd.to_numeric(odds.away_odds)

            status = write_data(df=odds,
                                name='odds',
                                to_csv=False,
                                sql_engine=engine,
                                db_schema='nba',
                                if_exists='append',
                                index=False)

            progress(iteration=page_number-1,
                     iterations=max_page_number,
                     iteration_name=str(season) + ' Season',
                     lapsed=time_lapsed(),
                     sql_status=status['sql'],
                     csv_status=status['csv'])

            page_number += 1

            driver.find_element_by_xpath(f"//span[text()='{page_number}']").click()
            time.sleep(1)
        except NoSuchElementException:
            break


if __name__ == '__main__':
    # Load games
    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    columns = ['game_id', 'home_odds', 'away_odds']

    season_range = range(start_season_odds, end_season_odds + 1)

    get_odds_data(season_range)

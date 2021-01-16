# SCRAPING ODDS DATA
from modelling.projects.nba import *  # import all project specific utils
from modelling.projects.nba.data.scraping import *


def get_max_page_number():
    page = BeautifulSoup(driver.page_source, 'lxml')
    page_button = page.find('span', text=re.compile(r'»\|')).find_parent()
    output = int(page_button.get('x-page'))

    log_performance()
    return output


def get_raw_rows():
    # grab html data
    soup = BeautifulSoup(driver.page_source, 'lxml')

    # set type of rows to be scraped (Date and game data)
    rows = ['center nob-border', 'odd deactivate', 'deactivate']

    # get raw text from html
    output = [x.getText() for x in soup.find_all('tr', {'class': rows})]

    log_performance()
    return output


# Get game date for game_id
def get_raw_date(x):
    try:
        formatted_date = dt.strptime(x, '%d %b %Y')
        output = formatted_date.strftime('%Y%m%d')
    except ValueError:
        output = None

    log_performance()
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

    log_performance()
    return output


# Get short team name for game_id
def get_short_name(x):
    try:
        output = Team.team_ids[Team.full_names.index(mid(x, 5, x.find('-') - 6))]
    except ValueError:
        output = None

    log_performance()
    return output


def fix_game_id(name_series, date_series, old_name, new_name, valid_date):
    output = [name_series[i] and name_series[i].replace(old_name, new_name)
              if int(if_none(date_series[i], 0)) < valid_date
              else name_series[i]
              for i in range(len(name_series))]

    log_performance()
    return output


def get_game_id(raw_df, dates):
    # get short name for home team for game_id
    short_names = [get_short_name(x) if mid(x, 2, 1) == ':' else None for x in raw_df]

    # fix for team names
    short_names = fix_game_id(short_names, dates, 'NOP', 'NOH', 20130701)
    short_names = fix_game_id(short_names, dates, 'BRK', 'NJN', 20120701)
    short_names = fix_game_id(short_names, dates, 'CHO', 'CHA', 20140520)

    # get game_id
    output = pd.Series(dates) + '0' + pd.Series(short_names)

    log_performance()
    return output


def get_scores(df):
    home_scores = df.game_id.map(games.set_index('game_id')['home_score']).fillna(0).astype(int)
    away_scores = df.game_id.map(games.set_index('game_id')['away_score']).fillna(0).astype(int)

    output = [str(home_scores[i]) + ':' + str(away_scores[i]) for i in range(len(home_scores))]

    log_performance()
    return output


# Get odds for home team
def get_home_odds(df, scores, x):
    try:
        odds_data = right(df[x], len(df[x]) - df[x].find(scores[x]) - len(scores[x]))
        output = left(odds_data, odds_data.find('.') + 3)
    except TypeError:
        output = None

    log_performance()
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

    log_performance()
    return output


def get_odds_data(seasons):
    # map get_season_data onto list of seasons
    for i in seasons:
        get_season_data(i)

    # return to regular output writing
    sys.stdout.write('\n')

    print(Colour.green + 'Odds Data Loaded' + ' ' + str('{0:.2f}'.format(time.time() - start_time))
          + ' seconds taken' + Colour.end)


@retry(ElementNotInteractableException, tries=5, delay=1)
def get_page_data(page_number):
    driver.find_element_by_xpath(f"//span[text()='{page_number}']").click()

    time.sleep(1)

    # initialise df
    page_odds = pd.DataFrame(columns=columns)

    # get raw rows
    odds_raw = get_raw_rows()

    # remove OT indicator
    odds_raw = pd.Series(odds_raw).str.replace(r'\sOT', '')

    # set a date for each row, then convert to Western US timezone
    odds_date_gmt = pd.Series([get_raw_date(left(x, 11)) for x in odds_raw]).fillna(method='ffill')
    odds_date = [convert_date(odds_raw, odds_date_gmt, i) for i in range(len(odds_raw))]

    # get game_ids
    page_odds.game_id = get_game_id(odds_raw, odds_date)

    # get game scores to help scrape from raw text
    scores = get_scores(page_odds)

    # get odds
    page_odds.home_odds = [get_home_odds(odds_raw, scores, x) for x in range(len(odds_raw))]
    page_odds.away_odds = [get_away_odds(odds_raw, scores, x) for x in range(len(odds_raw))]

    # convert to numeric and clear any dirty data
    page_odds['home_odds'] = pd.to_numeric(page_odds['home_odds'], errors='coerce')
    page_odds['away_odds'] = pd.to_numeric(page_odds['away_odds'], errors='coerce')
    page_odds.loc[page_odds['home_odds'].isnull(), 'away_odds'] = None

    # keep only games in the games folder (i.e. excluding All-Star and Pre-season)
    output = page_odds.loc[page_odds['game_id'].isin(games['game_id'])]

    log_performance()
    return output


def get_season_data(season):
    # initialise season DataFrame
    season_odds = pd.DataFrame(columns=columns)

    # get season url
    url = f'https://www.oddsportal.com/basketball/usa/nba-{season-1}-{season}/results/'

    # go to season page
    driver.get(url)

    # start from page 1
    page_number = 1

    # find max page number for season
    max_page_number = get_max_page_number()
    while page_number <= max_page_number:
        page_odds = get_page_data(page_number)

        season_odds = season_odds.append(page_odds)

        progress(iteration=page_number - 1,
                 iterations=max_page_number,
                 iteration_name=str(season) + ' Season',
                 lapsed=time_lapsed(),
                 sql_status='',
                 csv_status='')

        page_number += 1

    season_odds = season_odds.drop_duplicates(ignore_index=True)

    write_data(df=season_odds,
               name='odds',
               to_csv=False,
               sql_engine=engine,
               db_schema='nba',
               if_exists='append',
               index=False)


if __name__ == '__main__':
    columns = ['game_id', 'home_odds', 'away_odds']

    # get plays_raw dataframe from DB, or build from scratch
    odds = initialise_df(table_name='odds',
                         columns=columns,
                         sql_engine=engine,
                         meta=metadata)

    # Load games
    games = load_data(df='games',
                      sql_engine=engine,
                      meta=metadata)

    create_table_odds()

    season_range = range(start_season_odds, end_season_odds + 1)

    game_ids = games.loc[games['season'].isin(season_range), 'game_id']

    # get the game_ids to clear
    clear_game_ids = "', '".join(game_ids)

    try:
        connection_raw.execute(f"delete from nba.odds where game_id in ('{clear_game_ids}')")
    except ProgrammingError:
        pass

    # using selenium web driver as requests seem to return 'page not found' issues
    driver = webdriver.Chrome(executable_path=str(ROOT_DIR) + "/utils/chromedriver.exe",
                              options=options)

    get_odds_data(season_range)

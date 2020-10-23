#  DEFINE FUNCTIONS FOR SCRAPING
def scrape(date, driver, df):
    # grab all game information and load into daily table
    hteams = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[1]/a")
    hscore = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[2]/td[2]")
    ateams = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[1]/a")
    ascore = driver.find_elements_by_xpath(
        "//*[@class='game_summary expanded nohover']/table[1]/tbody/tr[1]/td[2]")
    # there is a loose game_summary on every page that returns an empty result
    for j in range(1, len(hteams)):
        df.loc[j, 'date'] = str(date.strftime('%Y-%m-%d'))
        df.loc[j, 'home_team'] = hteams[j].text
        df.loc[j, 'home_score'] = hscore[j].text
        df.loc[j, 'away_team'] = ateams[j].text
        df.loc[j, 'away_score'] = ascore[j].text


### Define left, mid, and right functions
def left(x, length):
    return x[:length]

def right(x, length):
    return x[-length:]

def mid(x, start, length):
    return x[start:start+length]


### Used to make predictions based on odds mispricing
def predmisprice(data):
    data.loc[(data['HomeOdds'] > data['AwayOdds']), 'Prediction'] = 0
    data.loc[(data['HomeOdds'] == data['AwayOdds']), 'Prediction'] = 0
    data.loc[(data['HomeOdds'] < data['AwayOdds']), 'Prediction'] = 1
    data.loc[(data['HomeOdds'] < 0) & (data['AwayOdds'] < 0), 'Prediction'] = 2
    return data

### Grid search to tune model for returns by odds or by mispricing
def grid_search(data, model, variables, target, a = 1, b = [], c = [], d = [], e = [], f = []):
    if model == 'xgb':
        cv = pd.DataFrame(columns = ['return', 'correct', 'predictions', 'home', 'away', 'seed', \
                                     'depth', 'weights', 'gamma', 'subsample', 'colsample'])
    elif model == 'svm':
        cv = pd.DataFrame(columns = ['return', 'correct', 'predictions', 'home', 'away', 'seed', \
                                     'cost', 'gamma'])
    elif model == 'rf':
        cv = pd.DataFrame(columns = ['return', 'correct', 'predictions', 'home', 'away', 'seed', \
                                     'depth', 'estimators'])
    for m in range(max(len(f),1)):
        for l in range(max(len(e),1)):
            for k in range(max(len(d),1)):
                for j in range(max(len(c),1)):
                    for i in range(max(len(b),1)):
                        for h in range(0,a+1):
                            oddcol = ['HomeOdds', 'AwayOdds']
                            train = data.loc[(data['Season']>=2012) & (data['Season']<=2016)]
                            test = data.loc[data['Season']==2017]
                            if model == 'xgb':
                                np.random.seed(h)
                                fitted = XGBClassifier(max_depth = b[i], min_child_weight = c[j], \
                                                   gamma = d[k], subsample = e[l], \
                                                   colsample_bytree = f[m])
                                fitted.fit(train[variables], train['Result'])
                            elif model == 'svm':
                                np.random.seed(h)
                                fitted = svm.SVC(C=b[i], gamma=c[j], probability=True)
                                fitted.fit(train[variables], train['Result'])
                            elif model == 'rf':
                                np.random.seed(h)
                                fitted = ensemble.RandomForestClassifier(max_depth = b[i], n_estimators = c[j])
                                fitted.fit(train[variables], train['Result'])
                            test_odds = test.loc[:,oddcol]
                            test_odds.index = range(len(test_odds))
                            test_odds = test_odds.astype(float)
                            test.index = range(len(test))
                            if target == 'accuracy':
                                predictions = fitted.predict(test[variables])
                                test_odds.insert(0,column = 'Result', value = test['Result'])
                                test_odds.insert(0,column = 'Prediction', value = predictions)
                            elif target == 'probs':
                                probs = pd.DataFrame(fitted.predict_proba(test[variables]), columns = oddcol)
                                misprice = probs - 1/test_odds
                                predictions = predmisprice(misprice)['Prediction'].astype(int)
                                test_odds.insert(0,column = 'Result', value = test['Result'])
                                test_odds.insert(0,column = 'Prediction', value = predictions)
                                #test_odds = test_odds.loc[((predictions == 0) & (probs['HomeOdds'] < 0.6)) | \
                                #                          ((predictions == 1) & (probs['AwayOdds'] < 0.6))]
                            test_odds.loc[(test_odds['Result'] == test_odds['Prediction']) & test_odds['Result']==0, 'Return'] = \
                            10*test_odds['HomeOdds'] - 10
                            test_odds.loc[(test_odds['Result'] == test_odds['Prediction']) & test_odds['Result']==1, 'Return'] = \
                            10*test_odds['AwayOdds'] - 10
                            test_odds.loc[(test_odds['Result'] != test_odds['Prediction']), 'Return'] = -10
                            test_odds = test_odds.loc[test_odds['Prediction'] != 2]
                            conf = metrics.confusion_matrix(test_odds['Result'], test_odds['Prediction'], labels = [0,1])
                            row = h+(a+1)*i+(a+1)*len(b)*j+(a+1)*len(b)*len(c)*k+(a+1)*len(b)*len(c)*len(d)*l+(a+1)*len(b)*len(c)*len(d)*len(e)*m
                            cv.loc[row] = 0
                            cv.iloc[row, 0] = sum(test_odds['Return']) # Return
                            cv.iloc[row, 1] = sum(np.diagonal(conf)) # Correct
                            cv.iloc[row, 2] = len(test_odds) # Predictions
                            cv.iloc[row, 3] = sum(conf[:,0]) # Home Predictions
                            cv.iloc[row, 4] = sum(conf[:,1]) # Away Predictions
                            try:
                                cv.iloc[row, 5] = a # First variable
                                cv.iloc[row, 6] = b[i] # Second variable
                                cv.iloc[row, 7] = c[j] # Third variable
                                cv.iloc[row, 8] = d[k] # Fourth variable
                                cv.iloc[row, 9] = e[l] # Fifth variable
                                cv.iloc[row, 10] = f[m] # Sixth variable
                            except Exception:
                                pass
                            print(cv.loc[[row]])
                    #print(str(h) + ' ' + str(time.time() - start_time))
    return cv


### Used to produce output csvs of predictions
def performance(model, data, namemod, namedat, odds, variables, type):
    data_pred = model.predict(data[variables])
    data_prob = model.predict_proba(data[variables])
    data.index = range(len(data))
    odds.index = range(len(odds))
    odds = odds.astype(float)
    if type == 'probs':
        probs = pd.DataFrame(data_prob, columns = ['HomeOdds', 'AwayOdds'])
        misprice = probs - 1/odds
        predictions = predmisprice(misprice)['Prediction'].astype(int)
        perf = pd.concat([data['Date'], data['HomeTeam'], data['AwayTeam'], odds, data['Result'], pd.Series(predictions), probs], axis = 1)
        #perf = perf.loc[((predictions == 0) & (probs['HomeOdds'] < 0.6)) | \
        #                ((predictions == 1) & (probs['AwayOdds'] < 0.6))]
        perf.to_csv(p+'/modeling/output/perf_'+str(namedat)+'_'+namemod+'.csv')
    elif type == 'preds':
        perf = pd.concat([data['Date'], data['HomeTeam'], data['AwayTeam'], odds, data['Result'], pd.Series(data_pred)], axis = 1)
        perf.to_csv(p+'/modeling/output/perf_'+str(namedat)+'_'+namemod+'.csv')
    return perf

def apipredict(x,y):
    gamedata = pd.read_csv(p+'/data/output/gamedata.csv')
    gamelog = pd.read_csv(p+'/data/output/gamelog.csv')
    variables = ['HomeTeam', 'AwayTeam', 'HomeWinTotal', 'HomeWinHome', 'AwayWinTotal', 'AwayWinAway', 'HomeWinLast', 'AwayWinLast', \
                 'HomeForm', 'AwayForm', 'HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', \
                 'HomeTravelLast', 'AwayTravelLast', 'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', \
                 'HomeGameWeek', 'AwayGameWeek', 'HomeVsOpp', 'AwayVsOpp']
    scale = ['HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', 'HomeTravelLast', 'AwayTravelLast', \
             'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', 'HomeGameWeek', 'AwayGameWeek']
    scaler = preprocessing.MinMaxScaler()
    scaler.fit(gamedata[scale])
    gamedata[scale] = scaler.transform(gamedata[scale])
    homevars = ['HomeWinTotal', 'HomeWinHome', 'HomeWinLast', 'HomeForm', 'HomePPG', 'HomeOPPG', 'HomeDiffPPG', \
                'HomeTravelLast', 'HomeTravelWeek', 'HomeRest', 'HomeGameWeek', 'HomeVsOpp']
    awayvars = ['AwayWinTotal', 'AwayWinAway', 'AwayWinLast', 'AwayForm', 'AwayPPG', 'AwayOPPG', 'AwayDiffPPG', \
                'AwayTravelLast', 'AwayTravelWeek', 'AwayRest', 'AwayGameWeek', 'AwayVsOpp']
    homepred = pd.DataFrame(columns = homevars)
    awaypred = pd.DataFrame(columns = awayvars)
    home = x
    homelog = gamelog[gamelog['Team'] == home]
    gameid = int(homelog.loc[homelog['Date'] == max(homelog['Date']), 'GameID'])
    game = gamedata.loc[gamedata['GameID']==gameid, variables]
    if (game['HomeTeam'] == home).bool():
        homepred[homevars] = game[homevars]
    elif (game['AwayTeam'] == home).bool():
        homepred[homevars] = game[awayvars]
    away = y
    awaylog = gamelog[gamelog['Team'] == away]
    gameid = int(awaylog.loc[awaylog['Date'] == max(awaylog['Date']), 'GameID'])
    game = gamedata.loc[gamedata['GameID']==gameid, variables]
    if (game['HomeTeam'] == away).bool():
        awaypred[awayvars] = game[homevars]
    elif (game['AwayTeam'] == away).bool():
        awaypred[awayvars] = game[awayvars]
    homepred.index = range(1)
    awaypred.index = range(1)
    pred = pd.concat([homepred, awaypred], axis = 1)
    variables = ['HomeWinTotal', 'HomeWinHome', 'AwayWinTotal', 'AwayWinAway', 'HomeWinLast', 'AwayWinLast', \
                 'HomeForm', 'AwayForm', 'HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', \
                 'HomeTravelLast', 'AwayTravelLast', 'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', \
                 'HomeGameWeek', 'AwayGameWeek', 'HomeVsOpp', 'AwayVsOpp']
    svm1 = pickle.load(open(p+'/modeling/output/svm1.pkl', 'rb'))
    predictions = svm1.predict(pred[variables])
    probabilities = svm1.predict_proba(pred[variables])
    if predictions == 0:
        return home#, probabilities[0][0]]
    elif predictions == 1:
        return away#, probabilities[0][1]]

def makejson(x,y):
    data = {}
    data["HomeTeam"] = x
    data["AwayTeam"] = y
    json_data = json.dumps(data)
    return json_data


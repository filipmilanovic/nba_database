from nba import *
from nba.functions import *
import inspect

gamedata = pd.read_csv(p+'/data/output/gamedata.csv')

train = gamedata.loc[(gamedata['Season']>=2012) & (gamedata['Season']<=2016)]
test = gamedata.loc[gamedata['Season']==2017]
eval = gamedata.loc[gamedata['Season']==2018]

oddcol = ['HomeOdds', 'AwayOdds']

train_odds = gamedata.loc[(gamedata['Season']>=2012) & (gamedata['Season']<=2016), oddcol]
test_odds = gamedata.loc[gamedata['Season']==2017, oddcol]
eval_odds = gamedata.loc[gamedata['Season']==2018, oddcol]

variables = ['HomeWinTotal', 'HomeWinHome', 'AwayWinTotal', 'AwayWinAway', 'HomeWinLast', 'AwayWinLast', \
             'HomeForm', 'AwayForm', 'HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', \
             'HomeTravelLast', 'AwayTravelLast', 'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', \
             'HomeGameWeek', 'AwayGameWeek', 'HomeVsOpp', 'AwayVsOpp']

depth = [5, 10, 15, 20, 25, 30, 35, 40]
estimators = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

params_rf = grid_search(gamedata, 'rf', variables, 'probs', 0, depth, estimators)
params_rf.to_csv(p+'/modeling/output/params_rf.csv')

depth = int(params_rf.loc[params_rf['return'] == max(params_rf['return']), 'depth'].head(1))
estimators = int(params_rf.loc[params_rf['return'] == max(params_rf['return']), 'estimators'].head(1))
seed = int(params_rf.loc[params_rf['return'] == max(params_rf['return']), 'seed'].head(1))

np.random.seed(seed)
rf1 = ensemble.RandomForestClassifier(max_depth = depth, n_estimators = estimators)
rf1.fit(train[variables], train['Result'])
pickle.dump(rf1, open(p+'/modeling/output/rf1.pkl', 'wb'))

performance(rf1, test, 'rf', 'test', test_odds, variables, 'probs')
performance(rf1, eval, 'rf', 'eval', eval_odds, variables, 'probs')
from modelling.projects.nba.utils.functions import *

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


depth = [10, 20, 30, 40, 50]
weights = [2, 4, 6]
gamma = [0, 1, 2, 3]
subsample = [0.25, 0.5, 0.75]
colsample = [0.25, 0.5, 0.75, 1]

params_xgb = grid_search(gamedata, 'xgb', variables, 'probs', 0, depth, weights, gamma, subsample, colsample)
params_xgb.to_csv(p+'/modeling/output/params_xgb.csv')

depth = int(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'depth'].head(1))
weights = int(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'weights'].head(1))
gamma = int(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'gamma'].head(1))
subsample = float(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'subsample'].head(1))
colsample = float(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'colsample'].head(1))
seed = int(params_xgb.loc[params_xgb['return'] == max(params_xgb['return']), 'seed'].head(1))

np.random.seed(seed)
xgb1 = XGBClassifier(max_depth = depth, min_child_weight = weights, gamma = gamma, \
                     subsample = subsample, colsample_bytree = colsample)
xgb1.fit(train[variables], train['Result'])

pickle.dump(xgb1, open(p+'/modeling/output/xgb1.pkl', 'wb'))

performance(xgb1, test, 'xgb', 'test', test_odds, variables, 'probs')
performance(xgb1, eval, 'xgb', 'eval', eval_odds, variables, 'probs')
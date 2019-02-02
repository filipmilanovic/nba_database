from nba import *
from nba.functions import *

gamedata = pd.read_csv(p+'/data/output/gamedata.csv')

variables = ['HomeWinTotal', 'HomeWinHome', 'AwayWinTotal', 'AwayWinAway', 'HomeWinLast', 'AwayWinLast', \
             'HomeForm', 'AwayForm', 'HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', \
             'HomeTravelLast', 'AwayTravelLast', 'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', \
             'HomeGameWeek', 'AwayGameWeek', 'HomeVsOpp', 'AwayVsOpp']

scale = ['HomePPG', 'AwayPPG', 'HomeOPPG', 'AwayOPPG', 'HomeDiffPPG', 'AwayDiffPPG', 'HomeTravelLast', 'AwayTravelLast', \
         'HomeTravelWeek', 'AwayTravelWeek', 'HomeRest', 'AwayRest', 'HomeGameWeek', 'AwayGameWeek']

for i in scale:
    gamedata.loc[pd.isnull(gamedata[i]), i] = 0

gamedata_scale = gamedata
scaler = preprocessing.MinMaxScaler()
scaler.fit(gamedata[scale])
gamedata[scale] = scaler.transform(gamedata[scale])

train = gamedata_scale.loc[(gamedata_scale['Season']>=2012) & (gamedata_scale['Season']<=2016)]
test = gamedata_scale.loc[gamedata_scale['Season']==2017]
eval = gamedata_scale.loc[gamedata_scale['Season']==2018]

oddcol = ['HomeOdds', 'AwayOdds']

train_odds = gamedata.loc[(gamedata['Season']>=2012) & (gamedata['Season']<=2016), oddcol]
test_odds = gamedata.loc[gamedata['Season']==2017, oddcol]
eval_odds = gamedata.loc[gamedata['Season']==2018, oddcol]

params = pd.DataFrame(columns = ['cost', 'gamma'])
cost = [1, 10, 100, 1000, 10000]
gamma = [0.0001, 0.001, 0.01, 0.1, 1, 10, 100]

params_svm = grid_search(gamedata, 'svm', variables, 'probs', 0, cost, gamma)
params_svm.to_csv(p+'/modeling/output/params_svm.csv')

seed = int(params_svm.loc[params_svm['return'] == max(params_svm['return']), 'seed'].head(1))
cost = float(params_svm.loc[params_svm['return'] == max(params_svm['return']), 'cost'].head(1))
gamma = float(params_svm.loc[params_svm['return'] == max(params_svm['return']), 'gamma'].head(1))

np.random.seed(seed)
svm1 = svm.SVC(C=cost, gamma=gamma, probability=True)
svm1.fit(train[variables], train['Result'])

pickle.dump(svm1, open(p+'/modeling/output/svm1.pkl', 'wb'))

performance(svm1, test, 'svm', 'test', test_odds, variables, 'probs')
performance(svm1, eval, 'svm', 'eval', eval_odds, variables, 'probs')
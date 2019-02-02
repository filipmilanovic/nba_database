from nba import *
from functions import * # @UnresolvedImport
# http://localhost:5000

app = Flask(__name__)
@app.route('/', methods = ['POST'])
def api_message():
    if request.headers['Content-Type'] == 'application/json':
        try:
            data = json.dumps(request.json)
            data = json.loads(data)
        except Exception:
            data = json.loads(request.body)
        return apipredict(data['HomeTeam'], data['AwayTeam'])

    else:
        return "Incorrect input"
    
if __name__ == '__main__':
    app.run()
    #app.run(host='0.0.0.0')
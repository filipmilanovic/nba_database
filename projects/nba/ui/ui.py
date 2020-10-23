import tkinter as tk # used for ui
import json # used for json creation
import requests as r # used to interact with api

def makejson(x,y):
    data = {}
    data["HomeTeam"] = x
    data["AwayTeam"] = y
    json_data = json.dumps(data)
    return json_data

# Create main window
root = tk.Tk()

# Function to close window
def quit(event=None):
    root.destroy()
root.bind('<Escape>', quit)
button1 = tk.Button(text="Close", command=quit)
button1.pack(side='bottom', fill = 'both')

frame = tk.Frame(root)
frame.pack(side='top')

homeentry = tk.Entry(frame, width = 8)
homeentry.pack(side='top')

awayentry = tk.Entry(frame, width = 8)
awayentry.pack(side='top')

output = tk.StringVar()

# Predicting locally
#def predict():
#    home = str(homeentry.get())
#    away = str(awayentry.get())
#    prediction = apipredict(home, away)
#    output.set(prediction)

# Predicting through API
def predict():
    home = str(homeentry.get())
    away = str(awayentry.get())
    data = makejson(home, away)
    headers = {'Content-Type': 'application/json'}
    req = r.post('http://localhost:5000', data = data, headers = headers)
    output.set(req.content)
   
# Create calculation button
compute = tk.Button(frame, text='Predict', command=predict)
compute.pack(side='bottom')

outbox = tk.Entry(frame, textvariable=output, width=8)
outbox.pack(side='bottom')

# Activate main window
root.mainloop()

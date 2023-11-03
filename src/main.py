""" hello """
import json
# import requests as r
from classes.endpoint import NBAEndpoint


with open('src/utils/header.json', 'r') as file:
    header = json.load(file)

with open('src/utils/parameters.json', 'r') as file:
    parameters = json.load(file)

TARGET_TABLE = 'draft'

target_endpoint = parameters[TARGET_TABLE]['endpoint']
target_parameters = parameters[TARGET_TABLE]['parameters']
# target_parameters['Season'] = 2020

TargetEndpoint = NBAEndpoint(endpoint=target_endpoint,
                             header=header)

print(TargetEndpoint.send_request(target_parameters))

# games_endpoint.send_request(parameters[TARGET_TABLE])


# TARGET_TABLE = 'transactions'
# TABLE_PRIMARY_KEY = 'transaction_id'

# url = 'https://stats.nba.com/js/data/playermovement/NBA_Player_Movement.json'

# response = r.request(
#     method='GET',
#     url=url,
#     headers=header
# )

# print(response.text)

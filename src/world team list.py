# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from pandas import json_normalize
import json
import os
import requests
import pandas as pd

user_id = ''
user_token = ''

# Construct the path to the Documents directory
# downloaded from API call from http://ftc-api.firstinspires.org
documents_path = os.path.join(os.path.expanduser("~"), "Downloads")
# Construct the full file path
file_path = os.path.join(documents_path, "team-list.json")

# get all teams in World championship
with open(file_path, 'r') as f:
    data = json.load(f)

df_event = json_normalize(data, record_path="advancement", meta=['advancedFrom', 'advancedFromRegion', 'slots'])



# get team details
url = "http://ftc-api.firstinspires.org/v2.0/2024/teams"
params = {"page": 1}  # Adjust parameters as needed
response = requests.get(url, params=params, auth=(user_id, user_token))
response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
data = response.json()

df_details = json_normalize(data, record_path="teams")
df_details.drop(df_details.index, inplace=True)
    
page_total = data['pageTotal']

for i in range(page_total-1):
    params = {"page": i+1}  # Adjust parameters as needed
    print(f"page: {i+1}")
    response = requests.get(url, params=params, auth=(user_id, user_token))
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    df_delta = json_normalize(data, record_path="teams")
    df_details = pd.concat([df_details, df_delta], ignore_index = True)


df_shorten = df_details[['teamNumber', 'nameShort',
        'city', 'stateProv', 'country', 'website', 'rookieYear','homeRegion']]

df_summary = df_event.merge(df_shorten, how='left', left_on='team', right_on='teamNumber')

# get team record
# downloaded from http://www.ftcstats.org/2025/index.html
file_path = os.path.join(documents_path, "team-record.crdownload")

# get all teams in World championship
with open(file_path, 'r') as f:
    data = json.load(f)

df_record = json_normalize(data)


# Sort by 'col1' and 'col2' (ascending)
df_sorted = df_record.sort_values(by=['team','np_opr'], ascending=False)

# Group by 'col1' and keep the first record
df_first = df_sorted.groupby('team').first().reset_index()
#Alternative: df_sorted.groupby('col1').head(1)


df_first_shorten = df_first[['team', 'team_name', 'np_opr', 'opr', 'np_oprc', 'auto_opr',
       'teleop_opr', 'eg_opr', 'event_name', 'auto-sample-count',
       'auto-specimen-count', 'tele-sample-high', 'tele-specimen-low',
       'tele-specimen-high', 'end-ascent-score']]


df_first_shorten['game_type'] = df_first_shorten.apply(lambda x: 'specimen' if x['auto-specimen-count']>x['auto-sample-count'] else 'sample', axis=1)


# merge with master file
df_first_shorten['team'] = df_first_shorten['team'].astype(int)
df_summary = df_summary.merge(df_first_shorten, how='left', on='team')

# output
file_path = os.path.join(documents_path, "2025-world-scouting.csv")
df_summary.to_csv(file_path)

import requests
import os
import json
import time
from datetime import datetime

import tweepy

def make_progress_bar(current_date):   
    total_days_in_year = 365 if not current_date.year % 4 else 366  # Leap year check

    days_passed = current_date.timetuple().tm_yday
    percentage_passed = round((days_passed / total_days_in_year) * 100)

    bar = '█' * (int(percentage_passed) // 4) 

    empty = 100 - int(percentage_passed) 
    empty_bar = '░' * (empty // 4)    
    
    return percentage_passed, f"{bar}{empty_bar} {percentage_passed}%"

def get_holiday_data(current_date):
    holiday_api_key = os.environ.get('HOLIDAY_API_KEY')
    url = f'https://holidayapi.com/v1/holidays?key={holiday_api_key}&country=US&year={current_date.year - 1}&month={current_date.month}&day=9'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['holidays']:
            return data['holidays'][0]['name']
        else:
            return None
    else:
        print(f"Error with getting holiday data {response.status_code}")

def get_json_data(item):
    with open(item + '.json', "r") as f:
        data = json.load(f)
    return data

    
    
def add_json_data(item, amount = 1):
    """Adds one to a json counter
       For example, adds one to the 'sent_tweets' counter
    """    
    data = get_json_data(item)
    data += amount
    with open(item + '.json', "w") as f:
        json.dump(data, f)
    
    
def delete_json_data(item, amount = 1):
    data = get_json_data(item)
    data -= amount
    with open(item + '.json', "w") as f:
        json.dump(data, f)
    

    
bearer_token = os.environ.get('BEARER_TOKEN')
api_key = os.environ.get('API_KEY')
api_secret = os.environ.get('API_SERCET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SERCET')
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
#auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
#api = tweepy.API(auth)    
    
    

while True:
    current_date = datetime.now()
    
    percentage, progress_bar = make_progress_bar(current_date)
    percentage_check = get_json_data('year_progress')

    if percentage == 100:
        delete_json_data('year_progress', 100)

    if percentage_check != percentage:
        holiday = get_holiday_data(current_date)

        if holiday:
            try:
                client.create_tweet(text = f"Today is also: {holiday}\n{progress_bar}")
                time.sleep(24 * 60 * 60)
                add_json_data('holidays_sent')
            except tweepy.TweetError as e:
                print('Error: ', e) 
                time.sleep(24 * 60 * 60)
                continue
            print(f"{holiday}\n{progress_bar}")
        else:
            try:
                client.create_tweet(text = f"{progress_bar}")
                time.sleep(24 * 60 * 60)
            except tweepy.TweetError as e:
                print('Error: ', e) 
                time.sleep(24 * 60 * 60)
                continue
            print(f"{progress_bar}")
        add_json_data('year_progress')
        add_json_data('tweets_sent')
    time.sleep(24 * 60 * 60)

# import hashlib
import json
from datetime import datetime, timedelta
import pytz
from random import choice
us_central_timezone = pytz.timezone('US/Central')
import random

import socket

def get_local_ip():
    try:
        # Create a socket object to get the local IP address
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote server (in this case, Google's DNS server)
            s.connect(("8.8.8.8", 80))
            # Get the local IP address
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception as e:
        print(f"Error: {e}")
        return None



# files to read information from
#client_credential_file = 'confidential_information\\client_logins.txt'
# server_connection_information_file = 'confidential_information\\server_connection_information.txt'
twitter_history_file = 'confidential_information\\twitter_history.txt'



def write_to_file(dictionary, filename):
    with open(filename, "w") as file:
        json.dump(dictionary, file)


def random_date(start, end):
  return start + timedelta(
      seconds=random.randint(0, int((end - start).total_seconds())))


def create_history_file(number_of_tweets):
    # let history be of the format
    # {id : [tweet, threat_level, zipcode, location, date_time_of_tweet]}
    end = datetime.now(tz=us_central_timezone) - timedelta(days=1)   # to today
    start = end - timedelta(days=7)
    
    places = ['the Farmhouse', 'the Power Lines', 'the house', 'the local factory', 'the Power Plant', 'the school','Kyle Field', 'Texas A&M', 'Zachary', 'the Dorms']
    threats = ['heavy ice', 'a fire', 'a wildfire', 'some heavy winds', 'icing']
    closeness = ['near', 'close to', 'by']
    #threat_tweets =  f'There is {choice(threats)} '

    location_zipcode = {'77840' : ['College Station', 'Bryan'],
                        '76020' : ['Azle', 'Springtown', 'Boyd', 'Reno'],
                        '77843' : ['College Station', 'Bryan'],
                        '77845' : ['College Station']}

    zipcodes = ['77840', '77845', '77843', '76020']
    zipcode = choice(zipcodes)
    loc = str((choice(location_zipcode[zipcode]))) + ', TX'
    threat_tweet =  f'There is {choice(threats)} {choice(closeness)} {choice(places)}.'
    tweet_time = random_date(start, end)
    my_history = {0 : [tweet_time.strftime('%m/%d/%Y, %H:%M:%S'), str(choice(["Moderate", 'Immediate'])), threat_tweet, loc + ", TX",  zipcode]}

    while len(my_history) < number_of_tweets:
        #time.sleep(4)
        zipcode = choice(zipcodes)
        loc = str((choice(location_zipcode[zipcode]))) + ', TX'
        threat_tweet =  f'There is {choice(threats)} {choice(closeness)} {choice(places)}.'
        tweet_time = random_date(start, end).strftime('%m/%d/%Y, %H:%M:%S')
        my_history[len(my_history)] = [tweet_time, str(choice(["Moderate", 'Immediate'])), threat_tweet, loc, zipcode]
    print(f"Length of my History file : {len(my_history)}")
    write_to_file(my_history, twitter_history_file)



with open(twitter_history_file, 'r') as file:
    history_information = json.load(file)



if __name__ == '__main__':
    create_history_file(50)


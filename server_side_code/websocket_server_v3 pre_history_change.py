import asyncio
import websockets
# import hashlib
import time
from random import randint, choice
import os
import json
from datetime import datetime, timedelta

from confidential_information.confidential import client_credentials, host, port, history_information, us_central_timezone
from confidential_information.confidential import write_to_file, client_credential_file, twitter_history_file #within_timeframe, sort_by_date
from confidential_information.confidential import places, threats, closeness, location_zipcode

# from my_constants import *
from import_file import *
from demo_predictor_manual_input import make_prediction

# for debugging (ic function ~~ print function   but much better)
from icecream import ic



# stores client information in form of {"username", [zipcode, websocket1, websocket2, etc]}
#client_info = {}

fake_twitter_results = {}

fake_twitter_connection_info = {}



def within_timeframe(date_and_time):
    my_date = datetime.strptime(date_and_time, "%m/%d/%Y, %H:%M:%S").date()
    today = datetime.now().date()
    delta = today - my_date
    #print(f'Delta days = {delta.days}')
    if delta.days <= 7:
        #print('Within Timeframe')
        return True
    else:
        return False
    

def sort_by_date(tweet_list_list):
    sorted_tweet_list = []
    #print(f'Tweet List List : {tweet_list_list}')
    if len(tweet_list_list) == 0:
        return tweet_list_list
    # first tweet is reference
    sorted_tweet_list.append(tweet_list_list[0])

    for tweet_information in tweet_list_list:
        date_and_time = tweet_information[0]
        tweet_date = datetime.strptime(date_and_time, "%m/%d/%Y, %H:%M:%S")
        #tweet_date = datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds))

        # get each tweet date in sorted_list
        for sorted_tweet_loc in range(len(sorted_tweet_list)):
            
            sorted_tweet = sorted_tweet_list[sorted_tweet_loc]
            # tweet references
            sorted_tweet_date = datetime.strptime(sorted_tweet[0], "%m/%d/%Y, %H:%M:%S")
            #sorted_tweet_date = datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds))

            # if tweet is after the compared tweet, append to that point
            if sorted_tweet_date < tweet_date:
                sorted_tweet_list.insert(sorted_tweet_loc, tweet_information)
                break

    return sorted_tweet_list
    
# called by manual update and periodic update
# takes in an zipcode
# returns list (a list of lists)
# runs parser
# if parser hits, runs model
async def run_parser(zipcode_to_search):
    message = f'Search Zipcode:{zipcode_to_search}'
    try:
        fake_twitter_websocket = fake_twitter_connection_info["Connection"]
        await fake_twitter_websocket.send(message)
        #return await fake_twitter_websocket.recv()   # recieve   [{type: type ,  zipcode : []}]
    except:
        print('FAKE TWITTER IS NOT CONNECTED')

    


async def run_parser_and_model(zipcode):
    pass_along =[]
    return_list = []
    tmp_pass_along = []
    ###   PARSER   ###
    parser_start_time = time.time()
    parser_hits = False
    print(f"This statement is indicating running of the parser for Zip - {zipcode}")

    try:
        twitter_websocket = fake_twitter_connection_info['Connection']
        await twitter_websocket.send(f'Search Zipcode:{zipcode}')
        # async sleep 5 sec for server to get info from fake twitter
        asyncio.sleep(5)
        # check a fake twitter dict
        if zipcode in fake_twitter_results.keys():
            # there were hits
            parser_hits = True
            parser_results = fake_twitter_results[zipcode]
        # else
            # no hits
        parser_end_time = time.time()
    except:
        pass

    if parser_hits:
        # let the tweet results be in the form [ [loc, tweet, time]  ]
    # let twitter_response be in the for [ {zipcode : [ [res1], [res2]]} ]
        pass

    
    current_update_datetime = datetime.now()
    past_tweet_time_1 = (current_update_datetime - timedelta(minutes=10)).strftime("%m/%d/%Y, %H:%M:%S")
    past_tweet_time_4 = (current_update_datetime - timedelta(minutes=13)).strftime("%m/%d/%Y, %H:%M:%S")
    past_tweet_time_2 = (current_update_datetime - timedelta(days=1, hours= 2,minutes=15)).strftime("%m/%d/%Y, %H:%M:%S")
    past_tweet_time_3 = (current_update_datetime - timedelta(minutes=30)).strftime("%m/%d/%Y, %H:%M:%S")
    current_tweet_time = current_update_datetime.strftime("%m/%d/%Y, %H:%M:%S")

    data =[
            [current_tweet_time, 'Immediate',"There is a wildfire by Zachary.",'College Station, TX', '77840']
            ,[past_tweet_time_4, 'Immediate', "Watch out, there is a fire breaking out at Texas A&M",'College Station, TX', '77840']
            ,[past_tweet_time_3, 'Immediate', "A raging longhorn was found near down power lines.", 'Fort Worth, TX','77840']
            ,[past_tweet_time_2, "Moderate", "Please be careful, the is major flooding over by the Library.", 'Houston, TX','77840']
            ,[past_tweet_time_2, "Moderate", "Please be careful, the is major flooding over by the Library.", 'Houston, TX', '77840']
            ,[past_tweet_time_2, "Moderate", "Please be careful, the is major flooding over by the Library.", 'Houston, TX', '77840']
            ]
    #return data

    ###    ML MODEL   ###
    if parser_hits == True: 
        
        model_start_time = time.time() 
        print('This statement is indicating running of the Machine Model\n')
            
        ic(parser_results)
        # what does parser_results need to look like
        # tweets from parser should be in the form : [loc, tweet, time] 
        # where time is a datetime str in the form ["%m/%d/%Y, %H:%M:%S"]  so i can use datetime.strptime("%m/%d/%Y, %H:%M:%S")
        # where loc is the city, state_abbr
        # where tweet is the tweet that had the keyword the parser found

        tmp_pass_along = make_prediction(parser_results)
        #print(f'Passing along : {tmp_pass_along}')
        #print(f'Length of Temp Pass Along : {len(tmp_pass_along)}')
        for item in tmp_pass_along:
            if item != None and item not in pass_along:
                pass_along.append(item)

            # append to history and pass along
            if len(pass_along) != 0  and pass_along != 'null':
                if isinstance(pass_along[0], list):
                    for item in pass_along:
                        if item[0] != 'null' and item[0] != None:
                            #print(f'item[0] : {item[0]}')
                            length_of_hist = len(history_information)
                            history_information[length_of_hist] = item
                            return_list.append(item)
                            write_to_file(history_information, twitter_history_file)
                elif(pass_along[0] != None  and  pass_along[0] != 'null'):
                    #print(pass_along[0])
                    length_of_hist = len(history_information)
                    history_information[length_of_hist] = pass_along
                    return_list.append(pass_along)
                    write_to_file(history_information, twitter_history_file)
                    
                    
        model_end_time = time.time()
        # delete the dictionary entry for the zipcode in the fake twitter results
        # to prevent multiple predictions on the same tweet
        del fake_twitter_results[zipcode]
    else:
        model_end_time = 0
        model_start_time = model_end_time

    # validation statistics
    print('Statistics')
    print(f'Parser Run Time : {parser_end_time - parser_start_time} sec') 
    print(f'Model Run Time : {model_end_time - model_start_time} sec\n')
    
    return return_list



async def command_execution(message, websocket):
    # what user is associated with this websocket connection
    username, zipcode, command = message.split(':')

    # manual update
    # decision-> manual update will update all connections associated with the user
    if 'update' in command.lower():
        try:
            info_to_send = await run_parser_and_model(zipcode)
            if len(info_to_send) >= 1:
                sorted_info_to_send = sort_by_date(info_to_send)
                update = {"type" : f"{command} for {username}", "info" : sorted_info_to_send}
                json_data = json.dumps([update])
                await websocket.send(json_data)
            elif info_to_send[0] == 'No Tweets':
                pass
        except websockets.exceptions.ConnectionClosed:
                # websocket.close()  #exception is for if the websocket was closed
                print("Client disconnected during update")
        return True

        
    elif command == "get history":
        return await get_zipcode_history(websocket, zipcode)


    # delete for deployment (laziness for early TAMU campus departure)
    elif command == 'shutdown':
        await websocket.send("Shutting Down Main Server")
        os.system("shutdown /s /t 1")  # shutdown
        # os.system('shutdown /r /t 1') # restart
        quit()

    # delete for deployment (make sure server isnt running after lab time) (no harm but good practice)
    elif command == 'destroy server':
        await websocket.send("Shutting Down Main Server")
        quit()

    else:
        response = "Unknown request"
        await websocket.send(response)
        return True

# commands from the client
async def handle_client(websocket, path):
    if websocket != fake_twitter_connection_info['Connection']:
        try:
            async for message in websocket:
                #username, zipcode, command = message.split(':')
                executed_command = await command_execution(message, websocket)
                if not executed_command:
                    print(f"ERROR EXECUTING THE COMMAND {message}")

            #handle_client(websocket, path)

        # if connection is closed, remove websocket for 
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
    else:
        # this is just for fake twitter
        try:
            async for message in websocket:
                #ic(message)
                message_dec = json.loads(message.decode())
                ic(message_dec)
                # should only be 1 key (zipcode)
                for zipcode_key in message_dec.keys():
                    #ic(message_dec[zipcode_key][0])
                    if 'There are 0 hits' in message_dec[zipcode_key][0]:
                        #print('No Hits')
                        pass
                    else:
                        print('There are possible hits')
                        if zipcode_key in fake_twitter_results.keys():
                            current_results_list = fake_twitter_results[zipcode_key]
                            # check if the tweets are already in list
                            # check tweet and time
                            for possible_result in message_dec[zipcode_key]:
                                new_entry = True
                                for current_result in current_results_list:
                                    if possible_result[0] == current_result[0] and possible_result[-1] == current_result[-1]:
                                        print('Not a new Entry')
                                        new_entry = False
                                        break
                                #  check if tweet is already in history file
                                if new_entry:
                                    for key_id in history_information.keys():
                                        historical_tweet = history_information[key_id]
                                        if possible_result[0] == historical_tweet[0] and possible_result[-1] == historical_tweet[-1]:
                                            print('Not a new Entry')
                                            new_entry = False
                                            break
                            
                                
                                if new_entry:
                                    fake_twitter_results[zipcode_key].insert(0, possible_result)

        # if connection is closed, remove websocket for 
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")


# Right now, history is text file stored on the server side
async def get_zipcode_history(websocket, zipcode):
    print(f'Getting History for {zipcode}')
    info_to_send = []
    #curr_index = 0
    for tweet_id in history_information:
        #print(history_information[tweet_id])
        if history_information[tweet_id][-1] == zipcode:
            #print(history_information[tweet_id])
            #print(history_information[tweet_id][4])
            if within_timeframe(history_information[tweet_id][0]):
            # check time of tweet (limit to 1 week (7 days))
                info_to_send.append(history_information[tweet_id])
            #curr_index = curr_index + 1
    try:
        sorted_info_to_send = sort_by_date(info_to_send)
        update = {"type" : f"Current History for {zipcode}", "info" : sorted_info_to_send}
        json_data = json.dumps([update])
        print(f'Sending {len(sorted_info_to_send)} for get history')
        await websocket.send(json_data)
        return True
    except websockets.exceptions.ConnectionClosed:
        # websocket.close()
        print("Client disconnected during History Update")
        return False


async def main(websocket, path):
    # get user + password
    # let them come as username
    message = await websocket.recv()
    ic(message)

    # normal operations
    if 'fake twitter' not in message.lower():
        username, zipcode, command = message.split(':')

        #print(f'New Connection established with {username}')
        ic(username)
        ic(zipcode)
        ic(command)

        try:
            await websocket.send('Connection established with the server')
            await command_execution(message, websocket)
        except websockets.exceptions.ConnectionClosed:
            curr_time = datetime.now().strftime("%m/%d/%Y, %I:%M %p")
            print(f'{username} disconnected a connection at {curr_time}')
        except:
            print(f'Error running command {command}')
            await websocket.close()
        
        await handle_client(websocket, path)
    
    # this is a fake twitter
    elif 'fake twitter' in message.lower():
        fake_twitter_connection_info['Connection'] = websocket
        print('Fake twitter connected')
        await handle_client(websocket, path)
  
  
# this is the main program
start_server = websockets.serve(main, host , port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

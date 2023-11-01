import asyncio
import websockets
# import hashlib
import time
#from random import randint, choice
import os
import json
from datetime import datetime

from confidential_information.confidential import host, port, history_information
from confidential_information.confidential import write_to_file, twitter_history_file

# from my_constants import *
from import_file import *
from demo_predictor_manual_input import make_prediction

# for debugging (ic function ~~ print function   but much better for debugging)
from icecream import ic

FAKE_TWITTER_HASHWORD = 'ea0d3e1e7cd045772170ece99e9db0ebd701f9ad72c8bdb43c513cea14953660'
FAKE_TWITTER_HASHWORD_2 = 'this is fake twitter connection'

fake_twitter_results = {}

fake_twitter_connection_info = {'Connection': None}


def within_timeframe(date_and_time, num_days=7):
    my_date = datetime.strptime(date_and_time, "%m/%d/%Y, %H:%M:%S").date()
    today = datetime.now().date()
    delta = today - my_date
    if delta.days <= num_days:
        return True
    else:
        return False
    

# this used to be a bigger function
# then I found sorted and key=lambda x use with datetime.strptime to make it easier
def sort_by_date(tweet_list_list):
    sorted_tweet_list = sorted(tweet_list_list, key=lambda x: datetime.strptime(x[0], "%m/%d/%Y, %H:%M:%S"), reverse=True) 
    return sorted_tweet_list
    
# functioned called by run_parser_and_model

async def run_parser(zipcode_to_search):
    message = f'Search Zipcode:{zipcode_to_search}'
    if fake_twitter_connection_info['Connection'] != None:
        try:
            fake_twitter_websocket = fake_twitter_connection_info["Connection"]
            await fake_twitter_websocket.send(message)
            #return await fake_twitter_websocket.recv()   # recieve   [{type: type ,  zipcode : []}]
        except:
            pass
    else:
        print('Fake Twitter is not Connected')


# overall function that calls parser to search a zipcode
# runs model on any results not in history
async def run_parser_and_model(zipcode):
    pass_along =[]
    return_list = []
    tmp_pass_along = []
    ###   PARSER   ###
    parser_start_time = time.time()
    parser_hits = False
    print(f"This statement is indicating running of the parser for Zip - {zipcode}")

    try:
        if fake_twitter_connection_info['Connection'] != None:
            twitter_websocket = fake_twitter_connection_info['Connection']
            await twitter_websocket.send(f'Search Zipcode:{zipcode}')
            # async sleep 3 sec for server to get info from fake twitter
            await asyncio.sleep(3)
            # check a fake twitter dict
            ic(fake_twitter_results)
            if zipcode in fake_twitter_results.keys():
                # there were hits
                parser_hits = True
                parser_results = fake_twitter_results[zipcode]

            parser_end_time = time.time()
        else:
            parser_hits = False
            parser_end_time = time.time()
    except:
        pass

    ###    ML MODEL   ###
    if parser_hits == True: 
        
        model_start_time = time.time() 
        print('This statement is indicating running of the Machine Model\n')
        
        # what does parser_results need to look like
        # tweets from parser should be in the form : [[loc, tweet, datetime, zipcode]] 
        # where time is a datetime str in the form ["%m/%d/%Y, %H:%M:%S"]  so i can use datetime.strptime("%m/%d/%Y, %H:%M:%S")
        # where loc is the city, state_abbr
        # where tweet is the tweet that had the keyword the parser found
        #print('Before the model')
        #ic(parser_results)
        tmp_pass_along = make_prediction(parser_results)
        #ic(tmp_pass_along)
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
                        #ic(item)
                        length_of_hist = len(history_information)
                        history_information[length_of_hist] = item
                        return_list.append(item)
                        write_to_file(history_information, twitter_history_file)
            elif(pass_along[0] != None  and  pass_along[0] != 'null'):
                #print(pass_along[0])
                length_of_hist = len(history_information)
                #ic(pass_along)
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
    print(f'Model Run Time : {model_end_time - model_start_time} sec')
    
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
                await websocket.close()  #exception is for if the websocket was closed
                print("Client disconnected during update\n")
        return True

        
    elif command.lower() == "get history":
        
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
            print("Client disconnected\n")
            await websocket.close()
    else:
        # this is just for fake twitter
        try:
            async for message in websocket:
                #ic(message)
                message_dec = json.loads(message.decode())
                #ic(message_dec)
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
                                    if possible_result[1] == current_result[1] and possible_result[-2] == current_result[-2]:
                                        print('Not a new Entry')
                                        new_entry = False
                                        break
                                #  check if tweet is already in history file
                                if new_entry:
                                    for key_id in history_information.keys():
                                        historical_tweet = history_information[key_id]
                                        # if tweet = tweet    AND   time=time
                                        if possible_result[1] == historical_tweet[2] and possible_result[-2] == historical_tweet[0]:
                                            print('Not a new Entry')
                                            new_entry = False
                                            break
                            
                                
                                if new_entry:
                                    fake_twitter_results[zipcode_key].insert(0, possible_result)
                        else:
                            for possible_result in message_dec[zipcode_key]:
                                #ic(possible_result)
                                new_entry = True
                                # just check if in history
                                for key_id in history_information.keys():
                                    historical_tweet = history_information[key_id]
                                    #  if tweet in historical tweets  (tweet = hist_tweet    AND    time=hist_tweet_time)
                                    if possible_result[1] == historical_tweet[2] and possible_result[-2] == historical_tweet[0]:
                                        print(f'Not a new Entry : {possible_result[1]}')
                                        new_entry = False
                                        break
                                if new_entry:
                                    if zipcode_key not in fake_twitter_results.keys():
                                        fake_twitter_results[zipcode_key] = [possible_result]
                                    else:
                                        fake_twitter_results[zipcode_key].insert(0, possible_result)

        # if connection is closed, remove websocket for 
        except websockets.exceptions.ConnectionClosed:
            print("FAKE TWITTER DISCONECTED")
            fake_twitter_connection_info['Connection'] = None
            await websocket.close()


# Right now, history is text file stored on the server side
async def get_zipcode_history(websocket, zipcode):
    print(f'Getting History for {zipcode}')
    #twitter_websocket = fake_twitter_connection_info['Connection']
    twitter_results = await run_parser_and_model(zipcode)
    #ic(twitter_results)
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
        # verify that these are in the same format
        # because I add the twitter stuff before, i dont need to append
        sorted_info_to_send = sort_by_date(info_to_send)
        update = {"type" : f"Current History for {zipcode}", "info" : sorted_info_to_send}
        print('Sending this information')
        ic(update)
        json_data = json.dumps([update])
        curr_time = datetime.now().strftime("%m/%d/%Y, %I:%M %p")
        #print(f'Sending {len(sorted_info_to_send)} items for get history for {zipcode} at {curr_time}')
        if websocket != None:
            await websocket.send(json_data)
            print(f'Sent {len(sorted_info_to_send)} items for get history for {zipcode} at {curr_time}\n')
        return True
    except websockets.exceptions.ConnectionClosed:
        await websocket.close()
        print("Client disconnected during History Update\n")
        return False


# main program for server
async def main(websocket, path):
    # get user + password
    # let them come as username
    message = await websocket.recv()
    ic(message)

    # normal operations
    # fake twitter initial message is SHA-256(Fake Twitter Connection) to guarrentee no accidental confusion
    if FAKE_TWITTER_HASHWORD_2 not in message.lower():
        username, zipcode, command = message.split(':')

        #print(f'New Connection established with {username}')
        ic(username)
        ic(zipcode)
        ic(command)

        try:
            await websocket.send('Connection established with the server')
            await command_execution(message.lower(), websocket)
        except websockets.exceptions.ConnectionClosed:
            curr_time = datetime.now().strftime("%m/%d/%Y, %I:%M %p")
            print(f'{username} disconnected a connection at {curr_time}')
            await websocket.close()
        except:
            print(f'Error running command {command}')
            await websocket.close()
        
        await handle_client(websocket, path)
    
    # this is a fake twitter
    elif FAKE_TWITTER_HASHWORD_2 in message.lower():
        fake_twitter_connection_info['Connection'] = websocket
        print('\n\nFake twitter connected\n\n')
        await handle_client(websocket, path)


# delete this for deployment
async def periodic_updates():
    while True:
        await asyncio.sleep(11)
        print()
        print('trying to update')
        #ic(fake_twitter_connection_info)
        if fake_twitter_connection_info['Connection'] != None:
            await get_zipcode_history(None, str(77840))
            #twitter_websocket = fake_twitter_connection_info['Connection']
            #await twitter_websocket.send('Search Zipcode: 77840')
        else:
            print('No Twitter')

  
# this is the main program
print(f'\nServer info :   ws://{host}:{port}\n')
start_server = websockets.serve(main, host , port)
asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().create_task(periodic_updates())           # only for initial testing of twitter parser
asyncio.get_event_loop().run_forever()

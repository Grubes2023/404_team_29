import asyncio
import websockets
# import hashlib
import time
from random import randint, choice
import os
import json
from datetime import datetime
from icecream import ic

from confidential_information.confidential import client_credentials, host, port, history_information, us_central_timezone
from confidential_information.confidential import write_to_file, client_credential_file, twitter_history_file #within_timeframe, sort_by_date
from confidential_information.confidential import places, threats, closeness, location_zipcode

# from my_constants import *
from import_file import *
from demo_predictor_manual_input import make_prediction


# stores client information in form of {"username", [zipcode, websocket1, websocket2, etc]}
client_info = {}

# called by manual update and periodic update
# takes in an INTEGER zipcode
# returns list (a list of lists)
# runs parser
# if parser hits, runs model
# if model hits, adds [tweet, threat_level, zipcode, date_time_str] to return list (a list of lists)
# if no hits, return list will be empty

def within_timeframe(date_and_time):
    #date_and_time = tweet_information[4]
    my_date = date_and_time.split(',')[0]
    month, day, year = my_date.split('/')
    tweet_date = datetime(int(year), int(month), int(day)).date()
    today = datetime.now().date()
    delta = today - tweet_date
    if delta.days <= 7:
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
        my_date, my_time = date_and_time.split(', ')
        month, day, year = my_date.split('/')
        hour, minutes, seconds = my_time.split(':')
        # tweet in question
        tweet_date = datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds))

        # get each tweet date in sorted_list
        for sorted_tweet_loc in range(len(sorted_tweet_list)):
            sorted_tweet = sorted_tweet_list[sorted_tweet_loc]
            date_and_time = sorted_tweet[0]
            my_date, my_time = date_and_time.split(', ')
            month, day, year = my_date.split('/')
            hour, minutes, seconds = my_time.split(':')
            # tweet in question
            sorted_tweet_date = datetime(int(year), int(month), int(day), int(hour), int(minutes), int(seconds))

            # if tweet is after the compared tweet, append to that point
            if sorted_tweet_date < tweet_date:
                sorted_tweet_list.insert(sorted_tweet_loc, tweet_information)
                break

    return sorted_tweet_list
    

async def run_parser_and_model(zipcode):
    pass_along =[]
    return_list = []
    tmp_pass_along = []
    ###   PARSER   ###
    parser_start_time = time.time()
    print(f"This statement is indicating running of the parser for Zip - {zipcode}")
    parser_hits = randint(0, 2)
    time.sleep(0.08)
    parser_end_time = time.time()

    ###    ML MODEL   ###
    if parser_hits != 0:
        
        model_start_time = time.time() 
        print('This statement is indicating running of the Machine Model\n')
        threat_tweet_input = []      
        for i in range(0, parser_hits):        
            #simulated_threat_level = choice(['No Threat', 'Caution', 'Immediate Threat'])
            time.sleep(1)
            time_of_tweet = datetime.now(us_central_timezone).strftime('%m/%d/%Y, %H:%M:%S')
            loc = str((choice(location_zipcode[str(zipcode)]))) + ', TX'
            threat_tweet =  f'There is {choice(threats)} {choice(closeness)} {choice(places)}.'
            threat_tweet_input.append([threat_tweet, zipcode, loc, time_of_tweet])
            
            tmp_pass_along = make_prediction(threat_tweet_input)
            #print(f'Passing along : {tmp_pass_along}')
            #print(f'Length of Temp Pass Along : {len(tmp_pass_along)}')
            for item in tmp_pass_along:
                if item != None and item not in pass_along:
                    pass_along.append(item)
            #print(f'Passing Along 2: {pass_along}')

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
                    
        time.sleep(0.1)
        model_end_time = time.time()
    else:
        model_end_time = time.time()
        model_start_time = time.time()

    # validation statistics
    print('Statistics')
    print(f'Parser Run Time : {parser_end_time - parser_start_time} sec') 
    print(f'Model Run Time : {model_end_time - model_start_time} sec\n')
    
    return return_list

# because of how I am doing client_info, this is needed to 
# find user who is associated with the websocket connection
def websocket_lookup(websocket):
    # find out who the websocket belongs to
    for user in client_info:
        for i in range(1, len(client_info[user])):
            if websocket == client_info[user][i]:
                return user   
                
    return "INVALID WEBSOCKET"


async def command_execution(message, websocket):
    # what user is associated with this websocket connection
    curr_user = websocket_lookup(websocket)

    # failsafe (CRASH THE SERVER because something isn't right)
    if curr_user == "INVALID WEBSOCKET":
        print("An invalid websocket tried to communicate with the server")
        exit()

    print(f"Received message from {curr_user} : {message}")

    # let command be in the form "Add User:Username:zipcode" -> no spaces near ":"
    # once added, idk. either move socket to new user or dont
    # depends on if the app wants to "switch user" on creating a new user (Probably so)
    if "New User" in message:
        new_user = message.split(":")[1]
        # hashed_password = message.split(":")[2]
        zipcode = message.split(":")[2]
        client_credentials[new_user] = zipcode
        write_to_file(dictionary=client_credentials, filename=client_credential_file)
        # del websocket from curr_user
        client_info[curr_user].remove(websocket)
        # add "new user" to client_info
        # add "zipcode" to client_info
        client_info[new_user] = [zipcode]
        # add previous websocket to client info
        client_info.append(websocket)
        #await get_zipcode_history(websocket, zipcode)
        return True


    # manual update
    # decision-> manual update will update all connections associated with the user
    elif message.lower() == "manual update":
        if client_info[curr_user][0] != '00000':
            zipcode_to_search = int(client_info[curr_user][0])
            info_to_send = run_parser_and_model(zipcode_to_search)
            if len(info_to_send) != 0:
                sorted_info_to_send = sort_by_date(info_to_send)
            else:
                sorted_info_to_send = [] #[['None', 'NA', 'NA', 'NA', 'NA']]
            # send out update information to all connections associated with the user
            for i in range(1, len(client_info[curr_user])):  # dont include zipcode index
                try:
                    curr_connection = client_info[curr_user][i]
                    update = {"type" : f"Manual Update for {curr_user}", "info" : sorted_info_to_send}
                    json_data = json.dumps([update])
                    await curr_connection.send(json_data)
                except websockets.exceptions.ConnectionClosed:
                    # websocket.close()  #exception is for if the websocket was closed
                    print("Client disconnected during update")
            return True

        # edge case if something goes wrong
        # wont happen from client side, would have to be that server side screwed something up
        else:
            await websocket.send("Send Zipcode")
            return True
        
    elif message.lower() == "get history":
        if client_info[curr_user][0] != '00000':
            return await get_zipcode_history(websocket, client_info[curr_user][0])

    # let command be of for "update zipcode:username:new_zipcode"
    elif "update zipcode" in message.lower():
        new_zipcode = message.split(":")[2]
        client_info[curr_user][0] = str(int(new_zipcode))  # make sure there are no spaces zipcode and convert to str because of json req
        client_credentials[curr_user] = str(int(new_zipcode))
        write_to_file(client_credentials, client_credential_file)  # update the main file so when user relogs on, after true disconnect, new zipcode will be saved
        await websocket.send("Zipcode has been updated")
        # for every connection on user
        for connection in client_info[curr_user][1:]:
            # print(connection)
            await get_zipcode_history(connection, client_info[curr_user][0])
        return True

    # delete for deployment (laziness for early TAMU campus departure)
    elif message == 'shutdown':
        await websocket.send("Shutting Down Main Server")
        os.system("shutdown /s /t 1")  # shutdown
        # os.system('shutdown /r /t 1') # restart
        quit()

    # delete for deployment (make sure server isnt running after lab time) (no harm but good practice)
    elif message == 'destroy server':
        await websocket.send("Shutting Down Main Server")
        quit()

    else:
        response = "Unknown request"
        await websocket.send(response)
        return True

# commands from the client
async def handle_client(websocket, path):
    try:
        async for message in websocket:

            executed_command = await command_execution(message, websocket)
            if not executed_command:
                print(f"ERROR EXECUTING THE COMMAND {message}")

    # if connection is closed, remove websocket for 
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        # find out who the websocket belonged to
        curr_user = websocket_lookup(websocket)
        print(f"{curr_user} disconnected a connection")
        client_info[curr_user].remove(websocket)
        # are all devices on curr user disconnected?
        if len(client_info[curr_user]) == 1:  # only zipcode remains
            print(f"{curr_user} has completely disconnected from the server")
            del client_info[curr_user]
        # websocket.close()
        


async def get_zipcode_history(websocket, zipcode):
    info_to_send = []
    #curr_index = 0
    for tweet_id in history_information:
        if history_information[tweet_id][3] == zipcode:
            #print(history_information[tweet_id])
            #print(history_information[tweet_id][4])
            if within_timeframe(history_information[tweet_id][5]):
            # check time of tweet (limit to 1 week (7 days))
                info_to_send.append(history_information[tweet_id])
            #curr_index = curr_index + 1
    try:
        sorted_info_to_send = sort_by_date(info_to_send)
        update = {"type" : f"Current History for {zipcode}", "info" : sorted_info_to_send}
        json_data = json.dumps([update])
        await websocket.send(json_data)
        return True
    except websockets.exceptions.ConnectionClosed:
        # websocket.close()
        print("Client disconnected during Histroy Update")
        return False

    
# should be updated for new client info list
async def periodic_updates():
    while True:
        await asyncio.sleep(30)  # Send updates every so often (XX seconds)
        # for every user that has connected
        for user in client_info:
            # make sure there are active connections and deal with edge case of perfectly synced up initializing user
            if (len(client_info[user]) > 1 and client_info[user][0] != '00000'):
                zipcode_to_search = int(client_info[user][0])
                info_to_send = await run_parser_and_model(zipcode=zipcode_to_search)

            if len(info_to_send) != 0:
                sorted_info_to_send = sort_by_date(info_to_send)
            else:
                sorted_info_to_send = [] 

            for i in range(1, len(client_info[user])):  # dont include zipcode index
                sorted_info_to_send = sort_by_date(info_to_send)
                try:
                    curr_connection = client_info[user][i]
                    update = {"type" : f"Periodic Update for {user}", "info" : sorted_info_to_send}
                    json_data = json.dumps([update])
                    await curr_connection.send(json_data)
                except websockets.exceptions.ConnectionClosed:
                    # websocket.close()
                    print("Client disconnected during update")


async def authenticate(websocket, credentials):
    username = credentials
    
    # authentication handled by Firebase database. All server is doing is making sure user is in server database
    if username in client_credentials: #and hashed_password == client_credentials[username][0]:
        await websocket.send("Authentication successful")
        #print("sending auth succ")
        return True
    else:
        await websocket.send("Authentication failed")
        return False

async def main(websocket, path):
    # get user + password
    # let them come as username
    credentials = await websocket.recv()
    ic(credentials)

    # "edge case" when a new user is being added from a new device with no user attached
    # let command come in as ('New User:username:zipcode')
    if "New User" in credentials:
        new_user = credentials.split(":")[1]
        zipcode = credentials.split(":")[2]
        client_credentials[new_user] = zipcode
        write_to_file(dictionary=client_credentials, filename=client_credential_file)
        client_info[new_user] = [zipcode, websocket]
        # add previous websocket to client info
        # client_info.append(websocket)
        # credentials = new_user
        #await websocket.send("Send Zipcode")
        #websocket.close()
        
        # Monica wants it this way----should recieve    'username'
        credentials = await websocket.recv()
        ic(credentials)
        if ":" in credentials:
            print('Error in Monica\'s credential code')
        
        

    # authenticate user 
    if await authenticate(websocket, credentials):
        username, zipcode = credentials.split(':')
        #zipcode = credentials[1]# this is authentication message (initial message for each websocket)
        # connected_clients.append([username, websocket])  # Add the websocket to the list
        new_connector = True
        # check if user is already in client info (already is connected and has zipcode in list)
        for user in client_info:
            # if user is already connected-> add a new socket to the list
            if username == user and websocket not in client_info[user]:
                # zipcode = client_info[user][0]
                client_info[user].append(websocket)
                new_connector = False
                break


        # if not in the client info
        if new_connector:
            # get zipcode on file first
            # zipcode = client_credentials[username]
            client_info[username] = [zipcode, websocket]

            # failsafe in case user has not submitted a zipcode yet (on any device)
            if zipcode == '00000':
                await websocket.send("Send Zipcode")

        print(f'New Connection established with {username}')
        await handle_client(websocket, path)
    else:
        await websocket.close()

start_server = websockets.serve(main, host , port)

asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().create_task(periodic_updates())
asyncio.get_event_loop().run_forever()

import asyncio
import websockets
# import hashlib
import time
from random import randint
import os
import json

from confidential_information.confidential import client_credentials, host, port
from confidential_information.confidential import write_to_file, client_credential_file

# stores client information in form of {"username", [zipcode, websocket1, websocket2, etc]}
client_info = {}

# called by manual update and periodic update
# takes in an INTEGER zipcode
# returns list (a list of lists)
# runs parser
# if parser hits, runs model
# if model hits, adds [tweet, threat_level, zipcode] to return list (a list of lists)
# if no hits, return list will be empty
def run_parser_and_model(zipcode):
    return_list =[]
    
    ###   PARSER   ###
    parser_start_time = time.time()
    print(f"This statement is indicating running of the parser for Zip - {zipcode}")
    parser_hits = randint(0, 3)
    time.sleep(0.08)
    parser_end_time = time.time()

    ###    ML MODEL   ###
    if parser_hits != 0:
        model_start_time = time.time() 
        print('This statement is indicating running of the Machine Model\n')      
        for i in range(0, parser_hits):        
            simulated_threat_level = randint(0, 2)
            if (simulated_threat_level != 0):
                tweet = f"This is the {i} testing tweet this round"
                return_list.append([tweet, str(simulated_threat_level), str(zipcode)])

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

    # let command be in the form "Add User:Username:Hashed_Password:zipcode" -> no spaces near ":"
    # once added, idk. either move socket to new user or dont
    # depends on if the app wants to "switch user" on creating a new user (Probably so)
    if "Add User" in message:
        new_user = message.split(":")[1]
        hashed_password = message.split(":")[2]
        zipcode = message.split(":")[3]
        client_credentials[new_user] = [hashed_password, zipcode]
        write_to_file(dictionary=client_credentials, filename=client_credential_file)
        # del websocket from curr_user
        client_info[curr_user].remove(websocket)
        # add "new user" to client_info
        # add "zipcode" to client_info
        client_info[new_user] = [zipcode]
        # add previous websocket to client info
        client_info.append(websocket)
        return True
    
    # let command be of the form "Change Password:New_Hashed_Password"
    elif "Change Password" in message:
        # user = message.split(":")[1]
        hashed_password = message.split(":")[1]            
        client_credentials[curr_user][0] = hashed_password
        write_to_file(dictionary=client_credentials, filename=client_credential_file)
        return True

    # manual update
    # decision-> manual update will update all connections associated with the user
    elif message == "manual update":
        if client_info[curr_user][0] != '00000':
            zipcode_to_search = int(client_info[curr_user][0])
            info_to_send = run_parser_and_model(zipcode_to_search)
            # send out update information to all connections associated with the user
            for i in range(1, len(client_info[curr_user])):  # dont include zipcode index
                try:
                    curr_connection = client_info[curr_user][i]
                    update = {"type" : f"Manual Update for {curr_user}", "info" : info_to_send}
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

    # let command be of for "update zipcode:new_zipcode"
    elif "update zipcode" in message:
        new_zipcode = message.split(":")[1]
        client_info[curr_user][0] = str(int(new_zipcode))  # make sure there are no spaces zipcode and convert to str because of json req
        client_credentials[curr_user][1] = str(int(new_zipcode))
        write_to_file(client_credentials, client_credential_file)  # update the main file so when user relogs on, after true disconnect, new zipcode will be saved
        await websocket.send("Zipcode has been updated")
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
        

# should be updated for new client info list
async def periodic_updates():
    while True:
        await asyncio.sleep(60)  # Send updates every so often (XX seconds)
        # for every user that has connected
        for user in client_info:
            # make sure there are active connections and deal with edge case of perfectly synced up initializing user
            if (len(client_info[user]) > 1 and client_info[user][0] != '00000'):
                zipcode_to_search = int(client_info[user][0])
                info_to_send = run_parser_and_model(zipcode=zipcode_to_search)

                # send out update information to all connections associated with the user
                for i in range(1, len(client_info[user])):  # dont include zipcode index
                    try:
                        curr_connection = client_info[user][i]
                        update = {"type" : f"Periodic Update for {user}", "info" : info_to_send}
                        json_data = json.dumps([update])
                        await curr_connection.send(json_data)
                    except websockets.exceptions.ConnectionClosed:
                        # websocket.close()
                        print("Client disconnected during update")

async def authenticate(websocket, credentials):
    username, hashed_password = credentials.split(":")
    #print(f'Username : {username}')
    #print(f'Password : {hashed_password}')
    #print(f'Password : {client_credentials[username][0]}')
      
    if username in client_credentials and hashed_password == client_credentials[username][0]:
        await websocket.send("Authentication successful")
        #print("sending auth succ")
        return True
    else:
        await websocket.send("Authentication failed")
        return False

async def main(websocket, path):
    # get user + password
    # let them come as username:hashed_password
    credentials = await websocket.recv()
    # authenticate
    if await authenticate(websocket, credentials):
        username = credentials.split(":")[0]
        # connected_clients.append([username, websocket])  # Add the websocket to the list
        new_connector = True
        # check if user is already in client info (already is connected and has zipcode in list)
        for user in client_info:
            # if user is already connected-> add a new socket to the list
            if username == user:
                # zipcode = client_info[user][0]
                client_info[user].append(websocket)
                new_connector = False
                break

        # if not in the client info
        if new_connector:
            # get zipcode on file first
            zipcode = client_credentials[username][1]
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
asyncio.get_event_loop().create_task(periodic_updates())
asyncio.get_event_loop().run_forever()

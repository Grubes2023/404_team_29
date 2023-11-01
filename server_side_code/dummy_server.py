import asyncio
import websockets
# import hashlib
from datetime import datetime
import time
from random import randint, choice
import os
import json
from datetime import datetime, timedelta
from icecream import ic


from confidential_information.confidential import client_credentials, host, port, history_information, us_central_timezone
from confidential_information.confidential import write_to_file, client_credential_file, twitter_history_file #within_timeframe, sort_by_date
from confidential_information.confidential import places, threats, closeness, location_zipcode

fake_twitter_results = {'77840': [['Test Location', 'Test Tweet', 'Test Time']]}


Test_info = ["There is a wildfire by Zachary.", "Immediate", "77840", "College Station, TX", "07/21/2023, 00:43:47"]
data =[[Test_info[4], Test_info[1], Test_info[0], Test_info[3]] , ["07/22/2023, 00:41:47", Test_info[1], Test_info[0], Test_info[3]]]

#update = {'type' : 'Dummy Server'}
#update['info'] = data

#{data : [a, b ,c]}


# {data : [datetime, Threat_level_string, Tweet, Location (no zipcode)]}
all_sockets = []

twitter_connection_info = {}

# this is just checking data transfer stuff
async def periodic_updates():
    while True:
        await asyncio.sleep(15)
        print('trying to update')
        if 'Connection' in twitter_connection_info.keys():
            if twitter_connection_info['Connection'] != None:
                twitter_websocket = twitter_connection_info['Connection']
                await twitter_websocket.send('Search Zipcode: 77840')
                #parser_results = await twitter_websocket.recv()
                #ic(parser_results)
            
            

# commands from the client
async def handle_client(websocket, path):
    try:
        async for message in websocket:
            if websocket != twitter_connection_info['Connection']:
                #executed_command = await command_execution(message, websocket)
                print(f'Message from websocket : {message}')
                curr_time = datetime.now().strftime("%I:%M:%S")
                print(f"Message recieved at {curr_time}\n")
                
            else:
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
                                if new_entry:
                                    fake_twitter_results[zipcode_key].insert(0, possible_result)
                                    

                                
 
            
    # if connection is closed, remove websocket for 
    except websockets.exceptions.ConnectionClosed:
        curr_time = datetime.now().strftime("%I:%M:%S %p")
        print(f"Client disconnected at {curr_time}")
        print()
        # websocket.close()
            
        

async def main(websocket, path):
    # get user + password
    # let them come as username
    credentials = await websocket.recv()
    #print(f'Trying to Connect {credentials}')
    ic(credentials)
    
    await websocket.send("This is a Test Message")
    print('Data Sent')
    print()
    if 'fake twitter' in credentials.lower():
        twitter_connection_info['Connection'] = websocket
        await handle_client(websocket, path)
    else:
        await handle_client(websocket, path)
    

start_server = websockets.serve(main, host , port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().create_task(periodic_updates())
asyncio.get_event_loop().run_forever()

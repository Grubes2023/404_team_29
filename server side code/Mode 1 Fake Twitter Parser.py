#INITIAL SKELETON CODE
import asyncio
import websockets
import requests
from datetime import datetime
import json
from threading import Thread

# debugging print statement
from icecream import ic

#using the google maps api key
GMAPS_API_KEY = 'AIzaSyC-tZmKbgyRMKcQL2ZxcfIlR0Zx7ThR2ZA'

# this is how server knows connection is fake twitter (to guarentee no confusion)
# this is SHA-256(Fake Twitter Connection)
FAKE_TWITTER_HASHWORD = 'ea0d3e1e7cd045772170ece99e9db0ebd701f9ad72c8bdb43c513cea14953660'

# global zipcode -> tweet dictionary
# this is how we store the user created tweets
tweet_dict = {}

# key words will be gotten from the database
KEY_WORDS = ['fire', 'ice', 'storm']


# return str(city, State_abbr)
# parameter String zipcode
def get_location_from_zip(zipcode):
    # use google maps api to get a city from the zipcode
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={GMAPS_API_KEY}'
    response = requests.get(url)
    data = response.json()

    # Extract city and state from API response
    if data['status'] == 'OK':
        results = data['results'][0]['address_components']
        city = None
        state = None
        for component in results:
            if 'locality' in component['types']:
                city = component['long_name']
            elif 'administrative_area_level_1' in component['types']:
                state = component['short_name']
        
        if city and state:
            location = f'{city}, {state}'
            return location
        else:
            return 'Unknown Location'
    else:
        print('Error: Could not geocode zip code')

# this is the function to continuously get user input
# this function is threaded at the bottom
def user_interaction():
    user_message = input("Please enter your message: ")
    while 'quit' != user_message.lower():
        user_zipcode = input("Please enter your Zip Code: ")
        valid_zipcode = False

        # verify zipcode stuff
        # if len != 5 or cannot int(user_location)
        while not valid_zipcode:
            try:
                user_zipcode = str(int(user_zipcode))  # is the zipcode numbers 
                if len(user_zipcode) == 5:
                    valid_zipcode = True
                else:
                    user_zipcode = input("Please enter a 5 digit Zip Code: ")
            except:
                user_zipcode = input("Please enter a VALID Zip Code: ")

        # see if the user message has a keyword in it
        has_keyword = False
        for keyword in KEY_WORDS:
            if keyword in user_message:
                has_keyword = True
                break

        # if it has a keyword (parser hit)
        if has_keyword:
            user_location = get_location_from_zip(user_zipcode)
            curr_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            tweet_information = [user_location, user_message, curr_time, user_zipcode]

            if user_zipcode in tweet_dict.keys():
                tweet_dict[user_zipcode].insert(0, tweet_information)
            else:
                tweet_dict[user_zipcode] = [tweet_information]

        else:
            print('No keywords in message indicating the possibility of a threat.\n')

        # this is just a debugging thing
        # can be removed later if wanted
        ic(tweet_dict)

        # start the loop over (enter quit to quit)
        user_message = input("Please enter your message: ")



async def main():
    ws_url = "ws://10.230.215.173:12345"
    # continously run
    while True:
        # try statement should be able to handle timeout errors
        try:
            async with websockets.connect(ws_url) as websocket:
                #print("WebSocket connection opened")
                message = FAKE_TWITTER_HASHWORD #"Fake Twitter Connection"    # this message is how server knows this websocket is fake twitter
                await websocket.send(message)

                # Handle incoming WebSocket messages
                async for message in websocket:
                    #print(f"WebSocket message received: {message}")
                    if "search zipcode" in message.lower():
                        zipcode_to_search = message.split(':')[1].strip()
                        if zipcode_to_search not in tweet_dict.keys():
                            results = [f'There are 0 hits for {zipcode_to_search}']
                            dict_to_send = {zipcode_to_search : results}
                            # tell Brandon how to filter based on above
                        else:
                            results = tweet_dict[zipcode_to_search]
                            dict_to_send = {zipcode_to_search : results}
                            
                        # why i have to encode message, I dont know
                        message = json.dumps(dict_to_send)
                        await websocket.send(message.encode())
        except:
            pass


if __name__ == "__main__":
    # "multithread" so that we can do user interaction and have an ongoing connection with server
    user_thread = Thread(target=user_interaction, args=())
    user_thread.start()

    # connection with the server
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()

    


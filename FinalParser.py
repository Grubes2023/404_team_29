import asyncio
import websockets
import requests
from datetime import datetime
import json
from threading import Thread
import csv

# debugging print statement
from icecream import ic

#using the google maps api key
GMAPS_API_KEY = 'AIzaSyBHdnPc-_li0jsWTVyV8aCHZbt1ddDm0ak'

# this is how server knows connection is fake twitter
# this is SHA-256(Fake Twitter Connection)
FAKE_TWITTER_HASHWORD = 'ea0d3e1e7cd045772170ece99e9db0ebd701f9ad72c8bdb43c513cea14953660'
#ea0d3e1e7cd045772170ece99e9db0ebd701f9ad72c8bdb43c513cea14953660

# global zipcode -> tweet dictionary
# this is how we store the user created tweets
tweet_dict = {}

# key words will be gotten from the database - have been moved here for speed purposes
KEY_WORDS = ['ablaze', 'fire', 'downed power lines', 'tornado', 'hurricane', 'flood', 'earthquake',
             'flooding', 'burned', 'forest fire', 'hanging power lines', 'power lines on the ground',
             'blizzard', 'burning', 'collapse', 'collapsed', 'danger', 'debris', 'seek shelter',
             'Tsunami', 'tropical storm', 'tropical cyclone', 'cyclone', 'fires', 'floods', 'hurricanes',
             'tornados', 'earthquakes', 'burned', 'forest fires', 'hanging power line', 'power line on the ground',
             'blizzards', 'cyclones', 'power outage', 'outage', 'outages', 'transformer exploded', 'wildfires',
             'wildfire', 'lightning strikes', 'high wind', 'lightning strike', 'high winds', 'no power', 'ice',
             'solar flare', 'solar flares', 'Heavy Thunder storms', 'storm', 'downed powerlines']


# return str(city, State_abbr)
# parameter String zipcode
def get_location_from_zip(zipcode):
    # use google maps api to get a city from the zipcode
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={zipcode}&key={GMAPS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    #Using google maps api structure to call and convert the zip code to a city and state

    # Extract city and state from API response
    if data['status'] == 'OK': #checking to see if the connnection is good
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
    mode = input("Please enter the mode (1 or 2). Enter quit to return here at any time: ")
    #initial input mode to come back too
    while mode not in ['1', '2']:
        print("Invalid mode. Please enter 1 or 2.")
        mode = input("Please enter the mode (1 or 2): ")

    if mode == '1': #mode 1, input based off of user inputted tweets and a zipcode
        while True: #this is done so that it can be quit at any time
            user_message = input("Please enter your message: ")
            if user_message.lower() == 'quit':
                print("Exiting...") #quitting takes you back to the mode looops
                user_interaction()
            user_zipcode = input("Please enter your Zip Code: ")
            if user_zipcode.lower() == 'quit':#quitting takes you back to the mode looops
                print("Exiting...")
                user_interaction()
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
                for keyword in KEY_WORDS: #keywords is the list at the beginnnig
                    if keyword in user_message:
                        has_keyword = True
                        break

            # if it has a keyword (parser hit)
            if has_keyword:
                user_location = get_location_from_zip(user_zipcode) #using google maps to convert
                curr_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") #taking in the time of the tweet to be displayed
                tweet_information = [user_location, user_message, curr_time, user_zipcode] #building the tweet

                if user_zipcode in tweet_dict.keys():
                    tweet_dict[user_zipcode].insert(0, tweet_information) #inserting the tweet to send
                else:
                    tweet_dict[user_zipcode] = [tweet_information] #adding the tweet to send

            else:
                print('No keywords in the message indicating the possibility of a threat.\n')

            # this is just a debugging thing
            # can be removed later if wanted
            ic(tweet_dict)

            # start the loop over (enter quit to quit)
            user_message = input("Please enter your message: ")
            if user_message.lower() == 'quit':
                print("Exiting...")
                user_interaction()
            
        

            
    elif mode == '2':

    # Open the CSV file
        while True: #used so we can break when we want too
                csv_filename = 'FINAL_TWEETBANK.csv' #tweetbank of over 9000 tweets assigned to diffrent zipcodes in texas, full exaustive list
                with open(csv_filename, 'r') as csv_file: #opening the csv as read only
                    csv_reader = csv.reader(csv_file) 
                    valid_zipcode2 = False #setting up for validation

                    # Get the target zip code from the user
                    while not valid_zipcode2: #testing the zipcode to check if it is in the full Texas Zip Code List
                        target_zipcode = input("Enter the Texas Zip Code you are looking for: ")
                        if target_zipcode.lower() == 'quit': #taked the string and makes it all lowercase to match the format
                            print("Exiting...")
                            user_interaction()
                        for row in csv_reader:
                            # Check if the zip code in the first column matches the target zip code
                            if row and row[0] == target_zipcode:
                                valid_zipcode2 = True #this shows that the inputted zipcode is in the bank
                                break
                        
                        if not valid_zipcode2:
                            print(f"No Zip code was found in the Texas Database for Zip code {target_zipcode}, please enter a valid Zip code.") #provides reasing as eto why the zipcode did not work
                            csv_file.seek(0) #resets the csv reader to begin from the top again
                        
                        
                    
                            
                                
                    
                    
                    
                        # Initialize a list to store matching values
                    matching_values = []
                    csv_file.seek(0) 

                    # Iterate through each row in the CSV file
                    for row in csv_reader:
                        # Check if the zip code in the first column matches the target zip code
                        if row and row[0] == target_zipcode:
                            # checking the value of the column for the zipcode
                            matching_values.append(row[1])#making sure there is no other values, and then appending it to the list


                
                    # print(f"Values for zip code {target_zipcode}: {matching_values}")

                    # Initialize a new list for matching keywords
                    matching_keywords_values = []
                


                    # Iterate through the matching values and check for keyword matches
                    for value in matching_values: #value is iterating as the matching values
                        for keyword in KEY_WORDS: #keyword is the keywords from the list above
                            if keyword in value: #if the keyword matches one of the words in the "hit" portion, it will be added to the new list
                                matching_keywords_values.append(value)
                                break
                                # Stop checking other keywords for this value

                    # Display the results with matching keywords
                    if matching_keywords_values:
                        matching_keywords_values = list(set(matching_keywords_values))
                        print(f"Values with matching keywords: {matching_keywords_values}")
                        

                        # Send messages to the server for each matching keyword value
                        #counter = 0 #debugging
                        #same process as before, but in a loop within the matching values
                        for value in matching_keywords_values:
                            user_location = get_location_from_zip(target_zipcode) 
                            curr_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                            tweet_information = [user_location, value, curr_time, target_zipcode]

                            #messages_to_send.append(tweet_information)

                            if target_zipcode in tweet_dict.keys():
                                tweet_dict[target_zipcode].insert(0, tweet_information)
                               
                                
                            else:
                                tweet_dict[target_zipcode] = [tweet_information]

                            # Display the message and zipcode
                            
                            print(f"Message sent: {value} | Zip Code: {target_zipcode}")
                        user_interaction()
                            
                    else:
                        print(f"No Zip code was found in the Texas Database for Zip code {target_zipcode}, please enter a valid Zip code.")   #error message for anything entered except a texas zipcode

                            
                            

            


async def main():
    ws_url = "ws://10.254.202.63:12345" #websocket connection key
    # continously run
    while True:
        # try statement should be able to handle timeout errors
        try:
            async with websockets.connect(ws_url) as websocket: #websocket connect for python
                #print("WebSocket connection opened")
                message = FAKE_TWITTER_HASHWORD #"Fake Twitter Connection"    # this message is how server knows this websocket is fake twitter
                await websocket.send(message)

                # Handle incoming WebSocket messages
                async for message in websocket: #usign await in async method to send all messages
                    #print(f"WebSocket message received: {message}")
                    if "search zipcode" in message.lower():
                        zipcode_to_search = message.split(':')[1].strip() #processing the message
                        if zipcode_to_search not in tweet_dict.keys(): #chceckig keys
                            results = [f'There are 0 hits for {zipcode_to_search}'] #parser check for zipcodes previous
                            dict_to_send = {zipcode_to_search : results}
                            # tell Brandon how to filter based on above
                        else:
                            results = tweet_dict[zipcode_to_search]
                            dict_to_send = {zipcode_to_search : results}
                            
                        
                        message = json.dumps(dict_to_send) #encoding the message #not sure why
                        await websocket.send(message.encode()) #encoding the message #not sure why
        # this is for timeout exceptions when first booting up server/parser
        except:
            pass


if __name__ == "__main__":
    # "multithread" so that we can do user interaction and have an ongoing connection with server
    user_thread = Thread(target=user_interaction, args=())
    user_thread.start() #starting the threads
 
    # connection with the server
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever() #no stopping

    


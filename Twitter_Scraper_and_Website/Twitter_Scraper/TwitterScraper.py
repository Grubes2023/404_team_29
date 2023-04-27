import tweepy #this iss REQUIRED for the Twitter API, and with SNScrape being taken down, its th only way to scrape data legally from twitter
import pandas as pd #for our dataframe
import csv #for reading and export



api_key = '' # my personal keys that eill give me access to the twitter API
api_key_secret = '' # my personal keys that eill give me access to the twitter API
bearer_token = '' # my personal keys that eill give me access to the twitter API
access_token = '' # my personal keys that eill give me access to the twitter API
access_token_secret =  # my personal keys that eill give me access to the twitter API

# authentication
auth = tweepy.OAuthHandler(api_key, api_key_secret) #this loads the twitter API access keys to access the data
auth.set_access_token(access_token, access_token_secret)#this loads the twitter API access keys to access the data

api = tweepy.API(auth) #this authenticates the access keys that were provided and gives me access to scraoe twitter

# search for tweets within 25 mile of a specific latitude and longitude
latitude = 30.6280 # latitude of college station
longitude = -96.3344 # longitude of college station
radius = '25mi' # radius in which the scraper will search for tweets with the specific location tag
columns = ['Time', 'User', 'Tweet', 'Location'] #this creates the header of thee dataframe, that will be implemented into thye csv file later
data = [] #creates the list that is going to be used in the pandsas dataframe later
with open('Capstone_Words_and_Phrases.csv', newline='') as csvfile: #opening the csv file that has all of the preloaded words that shoukd be flagged
    reader = csv.reader(csvfile, delimiter=',', quotechar='"') #creating a reader oject that can read the lines of the csv file quotechar surrounds the variable in double quites
    for row in reader: #starts a loop that iterates over each row in the CSV file
        for column in row: #starts a nested for loop that iterates over each column of the file, which in this case is only a single column. THerefore the column variable contains the value or word that we are looking for
            query = column #assigning the search critera for this iterarion of the api pull
            public_tweets = api.search_tweets(q=query, geocode=f"{latitude},{longitude},{radius}") #this sends a pull request to the twitter API to search for tweets that contain the word in the query and the location parameters associated

            for tweet in public_tweets: # iterates through th tweets collected 
                 if tweet.place is not None: # this checks to make sure that the location column has a value in it, specifically the location that we searched for. We MUST do this because the search_tweets location uses both tweet and profile location 
                    data.append([tweet.created_at, tweet.user.screen_name, tweet.text, tweet.place.full_name]) # adds the data colleced on that specific tweet to the list that will later be pushed to a csv
                 else: #this excutes if the location is empty, hich is an invalid tweet for us to check 
                     continue #pushes the code onto the next iteration without it failing

            df = pd.DataFrame(data, columns=columns) # appends the data and tweets that were found to the datafram, which will be outputted later. This will be done each time a tweet is found to be correct and with each new query


df.to_csv('tweets.csv', index=False) # Taking the dataframe that I created and sending it to the csv file, which will be the inputs for the machine learning model
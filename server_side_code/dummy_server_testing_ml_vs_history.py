
# from twitter history file
random_tweet = ["10/15/2023, 18:15:32", "Moderate", "There is a wildfire close to Texas A&M.", "College Station, TX", "77840"]

# format = [datetime, threat, tweet, loc, zipcode]


# from fake twitter
# info [loc, tweet, datetime, zipcode]
# recv_format = [loc, tweet, datetime, zipcode]

# after going through the model
# format = [datetime, threat, tweet, loc, zipcode]

from datetime import datetime

def to_seconds(date_time_str):
    a = datetime.strptime(date_time_str, "%m/%d/%Y, %H:%M:%S")
    reference = datetime.strptime("1/1/2000, 10:00:00", "%m/%d/%Y, %H:%M:%S")
    return (a-reference).total_seconds()

dateee = "5/9/2023, 18:20:30"

print(to_seconds(dateee))
# from my_constants import *
from import_file import *

# make sure the program is at least decently fast
# from timeit import default_timer as timer

#from icecream import ic



# tweet will be passed in the form of [ [loc, tweet, datetime, zipcode] , [loc, tweet, datetime, zipcode]]

# [[loc, tweet, datetime, zipcode]]

def make_prediction(my_input):
    data_to_send_along = []

    ### if my input is of the format   [ [tweet 1] , [tweet 2] , [tweet 3]]      
    if isinstance(my_input[0], list):
            my_prediction = make_batch_pred(my_input)

            # decide if to pass the tweet along to the user application or website
            for i in range(len(my_prediction)):
                #print()
                data_to_send_along.append(prediction_decision(my_prediction[i], input_tweet=my_input[i]))

                
            my_prediction.clear()

    ### if my input is of the format:  tweet      where tweet = [loc, tweet, time]
    elif isinstance(my_input, list):
        input_tweet = my_input[1]
    
        # make the prediction
        my_prediction = make_single_pred(input_tweet)

        # decide if to pass the tweet along to the user application
        data_to_send_along.append(prediction_decision(my_prediction, input_tweet=my_input))
        #my_prediction.clear()
    ### else something went wrong with the input
    else:
        print('ERROR: Something went really wrong. I dont know if the input is a list or not.')
        print('Check Input')

    return data_to_send_along

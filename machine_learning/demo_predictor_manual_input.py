# from my_constants import *
from import_file import *

# make sure the program is at least decently fast
from timeit import default_timer as timer

# notes from manual inputs
'''
More time-based examples (of no concern category)
more painting/photography examples (if no concern category)
more snow examples (right now it assumes category 1/2)
'''



def make_prediction(my_input):
    ### if my input is of the format   [ [tweet 1] , [tweet 2] , [tweet 3]]      where each tweet is of the format = [loc, tweet, time]
    if isinstance(my_input[0], list):
            my_prediction = make_batch_pred(my_input)

            # decide if to pass the tweet along to the user application or website
            for i in range(len(my_prediction)):
                prediction_decision(my_prediction[i], input_tweet=my_input[i])

            my_prediction.clear()

    ### if my input is of the format:  tweet      where tweet = [loc, tweet, time]
    elif isinstance(my_input, list):
        input_tweet = my_input[1]
    
        # make the prediction
        my_prediction = make_single_pred(input_tweet)

        # decide if to pass the tweet along to the user application
        prediction_decision(my_prediction, input_tweet=my_input)
        my_prediction.clear()
    ### else something went wrong with the input
    else:
        print('ERROR: Something went really wrong. I dont know if the input is a list or not.')
        print('Check Input')

    # clearing everything for consistency
    my_input.clear()


#############################
## manually getting inputs ##
#############################

location = 'Bryan, College Station'
cur_time = '1930'

test_tweet = input('Type out a test Tweet: ')

while (test_tweet != 'q') and (test_tweet != 'quit') and (test_tweet != 'done'):
    test_input_list_2 = [location, test_tweet, cur_time]
    start = timer()
    print('')
    make_prediction(test_input_list_2)
    end = timer()
    print(f'Time elapsed : {round((end - start), 3)} seconds')
    print('')

    test_tweet = input('Type out a test Tweet (\'q\' to exit): ')

    
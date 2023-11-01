# from my_constants import *
from import_file import *

# make sure the program is at least decently fast
from timeit import default_timer as timer
from time import sleep
total_time_start = timer()

# notes from manual inputs
'''
More time-based examples (of no concern category)
more painting/photography examples (if no concern category)
more snow examples (right now it assumes category 1/2)
'''

#############################
## manually getting inputs ##
#############################
test_input_list_1 = [ 
                      ['Bryan, College Station', 'There is a fire heading towards the power plant', '1645']
                    , ['Azle', '@joe Tornado reported near the town', '3826'] 
                    , ['Boyd', 'Just Got fired from my job', '1258']
                    , ['Washington', 'This wildfire is spreading fast. Everyone in the area is advised to evacuate', '2422']
                    , ['Zachary', 'New Barbeque grill. Testing it out this weekend. Anyone want to help me fire it up', '0420']
                    , ['Houston', 'Tropical Storm Jackson has been upgraded to a class 0 hurricane', '0900']
                    , ['Mineral Wells', '5 years ago, hurricane harvey devastated south texas', '0900']
                    , ['Ryzen', 'Look at this beautiful painting of the power of God #hurricane #storm', '0900']
                    , ['Amarillo', 'a 8.7 magnitude earthquake was just recorded in Michigan', '0900']
                    , ['Jackson', 'Snow has been reported on the highway', '0500']
                    ]



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
    # my_input.clear()

print('Starting Test')
end_iteration = 10
for i in range(1,end_iteration):
    print(f'\nIteration {i}')
    start = timer()
    print('')
    make_prediction(test_input_list_1)
    end = timer()
    print(f'Time elapsed in iteration: {round((end - start), 3)} seconds')
    print('')
    if (i != end_iteration):
        sleep(45)

final_end = timer()
print(f'Total Time elapsed: {round((final_end - total_time_start), 3)} seconds')
print('Change pass along function to print')
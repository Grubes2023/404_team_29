# import the required libraries
import pandas as pd
import numpy as np
import re
import pickle
# import nltk
from nltk.stem import WordNetLemmatizer

#from nltk import download
#download('wordnet')

# only really needed for training the model or numerically evaluating the model
# pip install scikit-learn    not sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils import shuffle
from collections import Counter

# import tensorflow as tf
from keras.optimizers import Adam
from keras.models import Model, load_model, Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, Input
from keras.callbacks import EarlyStopping
from keras.utils import pad_sequences, to_categorical
from keras.preprocessing.text import Tokenizer
from keras.losses import CategoricalCrossentropy  #,SparseCategoricalCrossentropy

# not needed for deployment
from os import mkdir, path, getcwd, environ
environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from my_constants import *
from icecream import ic

################################
### FUNCTIONS FOR DEPLOYMENT ###
################################
#creating a function to prepocess tweet
def data_processing(tweet):
    tweet = tweet.lower()                                                         # Make tweet lowercase for consistency
    tweet = re.sub(r"https\S+|www\S+http\S+", '', tweet, flags = re.MULTILINE)    # get rid of any websites in tweet
    tweet = re.sub(r'\@w+|\#','', tweet)                                          # gets rid of any @ because it is useless for the model

    # i honestly dont know exactly what these do
    # but one of the twitter ML models I took inspiration from
    # had these in it, so it at least doesnt hurt                                          
    tweet = re.sub(r'[^\w\s]', '', tweet)
    tweet = re.sub(r'ð', '', tweet)  
    return tweet

# a function to lemmatize (get the root of the word) to help minimize vocab size
def lemmatizing(data):
    # split string into list of words
    word_list = data.split()
    # lemmatize each word in the list
    word_list = [WordNetLemmatizer().lemmatize(word) for word in word_list]
    # combine the list into 1 string and return that string
    tweet = ' '.join(word_list)
    return tweet

# def a function to combine all prepocessing
def preprocess(dataframe):
    # apply preprocessing function to tweets and save as itself
    dataframe.tweet = dataframe['tweet'].astype(str)
    dataframe.tweet = dataframe['tweet'].apply(data_processing)
    # get rid of any duplicate tweets and save as itself
    dataframe = dataframe.drop_duplicates('tweet')
    # return dataframe

def load_model_and_tok(model_version):
    ### loading the model ###
    parent_dir = MY_WORKING_DIRECTORY + '\\trained_models\\'
    directory = 'version_' + model_version
    model_path = path.join(parent_dir, directory)
    loaded_model = load_model(model_path)

    ### loading the tokenizer ###
    tok_file = 'tokenizer_version_' + model_version +'.pickle'
    tok_par_directory = MY_WORKING_DIRECTORY + '\\tokenizers\\'
    tok_path = tok_par_directory + tok_file
    with open(tok_path, 'rb') as handle:
        loaded_tok = pickle.load(handle)
        
    return loaded_model, loaded_tok


###   Predictions   ###

## defining a function to make a prediction
## input is a single tweet
### returns a list of the format [category_label, confidence_as_float_percentage]
def make_single_pred(inp_tweet, model_v='0.8_' + 'charlie'):

    #####################
    ### PREPROCESSING ###
    #####################
    proc_tweet = data_processing(tweet=inp_tweet)
    proc_tweet = lemmatizing(proc_tweet)

    ################################
    ### LOAD MODEL and TOKENIZER ###
    ################################
    model, tok = load_model_and_tok(model_version=model_v)

    proc_tweet_seq = tok.texts_to_sequences([proc_tweet])
    tweet_matrix = pad_sequences(proc_tweet_seq, maxlen=MAX_LEN)

    #############################
    ### MAKING THE PREDICTION ###
    #############################
    predictions = model.predict(tweet_matrix)
    single_prediction = predictions[0]
    predicted_label = np.argmax(single_prediction)

    ##############################
    ### PARSING THE PREDICTION ###
    ##############################
    confidence = int(round(single_prediction[predicted_label]*100, 0))

    return [predicted_label, confidence]

## defining a function to make a prediction on a lot of tweets
## input is a list of tweets
### returns a list of the format [category_label, confidence_as_float_percentage]
# [[loc, tweet, datetime, zipcode]]
def make_batch_pred(inp_tweets, model_v='0.8_' + 'beta'):
    print('Making a batch prediction')
    tweets_df = pd.DataFrame(inp_tweets, columns =['location', 'tweet','time', 'zipcode'], dtype=object) 
    ################################
    ### LOAD MODEL and TOKENIZER ###
    ################################
    model, tok = load_model_and_tok(model_version=model_v)
    
    #####################
    ### PREPROCESSING ###
    #####################

    preprocess(tweets_df)
    # lemmatize all the tweets
    tweets_df.tweet = tweets_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer
        
    # getting data into sets
    features = tweets_df['tweet']
    seq = tok.texts_to_sequences(features)
    padded = pad_sequences(seq, maxlen=MAX_LEN)

    pred = model.predict(padded)
    # containers and statistic measurement initialization
    passed_on = []

    # parsing predictions
    for i in range(len(features)):
        prediction = np.argmax(pred[i])
        confidence = round(pred[i][prediction]*100,3)
        #print(confidence)
        passed_on.append([prediction, confidence])
        ic([prediction, confidence, tweets_df['tweet'][i]])

        

    ##############################
    ### PARSING THE PREDICTION ###
    ##############################
    return passed_on


###  DATA TRANSFER   ###


# decides if a tweet moves on and passes along if it does\
# input is of the format model_prediction = [label, confidence]   and   input tweet = [tweet, zip, loc, time]
#[[loc, tweet, datetime, zipcode]]
def prediction_decision(model_prediction, input_tweet):
    categ = CATEGORIES[model_prediction[0]]
    confidence = model_prediction[1]
    tweet = input_tweet[1]
    zipcode = input_tweet[3]
    loc = input_tweet[0]
    time = input_tweet[2]

    #print(tweet)
    #print(categ)
    #print()
    #######################
    ### pass along data ###
    #######################
    if ((model_prediction[1] >= MIN_CONFIDENCE_LEVEL) and (model_prediction[0] != 0) ):  # confident that it is a category 1 or 2 (not 0)
        
        # format  [datetime, category(word), tweet, location]

        pass_along = [time, categ, tweet, loc, zipcode]

        ic(pass_along)

        # data_pipeline_to_app(pass_along)
        # data_pipeline_to_website(pass_along)

        return pass_along



##############################
### FUNCTIONS FOR TRAINING ###
##############################

### Creating a model ###
def create_model(
             num_lstm_layers=NUM_LSTM_LAYERS,
             lstm_nodes = LSTM_LAYER_NODES,
             num_dense_layers=NUM_DENSE_LAYERS,
             dense_layer_nodes=DENSE_LAYER_NODES,
             dense_activation=DENSE_LAYER_ACTIVATION,
             dropout=DROPOUT_CHANCE
             ):
    
    model = Sequential()
    model.add(Input(name='inputs',shape=[MAX_LEN]))
    model.add(Embedding(VOCAB_SIZE,OUTPUT_LAYER_DIM,input_length=MAX_LEN))

    # adding num_layers-1 (+1) Long-Short term memory layers
    for i in range(num_lstm_layers-1):
        model.add(LSTM(lstm_nodes // (2**i), return_sequences=True))   # must return sequence so next lstm can use them
        model.add(Dropout(dropout))
    
    # final lstm layer does not return sequences
    model.add(LSTM(lstm_nodes // (2**(num_lstm_layers-1))))
    model.add(Dropout(dropout))

    # adding dense layer blocks
    for i in range(num_dense_layers):
        model.add(Dense(dense_layer_nodes//(2**i), activation=dense_activation))
        model.add(Dropout(dropout))

    # adding the final output layer
    model.add(Dense(3,name='output', activation='softmax'))
    return model

# saves model as a folder structure and tokenizer as a pickle file
def save_model_and_tok(model_version, model, history, token):
    ### Saving the Model ###
    parent_dir = MY_WORKING_DIRECTORY + '\\trained_models\\'
    directory = 'version_' + model_version
    model_path = path.join(parent_dir, directory)
    mkdir(model_path)
    model.save(model_path, history)

    ### Saving the Tokenizer ###
    tok_file = 'tokenizer_version_' + model_version +'.pickle'
    tok_par_directory = MY_WORKING_DIRECTORY + '\\tokenizers\\'
    tok_path = tok_par_directory + tok_file
    with open(tok_path, 'wb') as handle:
        pickle.dump(token, handle, protocol=pickle.HIGHEST_PROTOCOL)

# def a function to get weights for unbalanced training set
def get_weights(label_set, printing=False):
    twos = Counter(label_set)[2]
    ones = Counter(label_set)[1]
    zeros = Counter(label_set)[0]
    length = float(ones + zeros + twos)
    weight_for_0 =  1.0 - float(zeros/length)
    weight_for_1 = 1.0 - float(ones/length)
    weight_for_2 = 1.0 - float(twos/length)
    weights = {0: weight_for_0, 1: weight_for_1, 2: weight_for_2}
    if (printing):
        print(f'Number of Samples : {length}')
        print(f'Weight of 0 entries: {weight_for_0}')
        print(f'Weight of 1 entries: {weight_for_1}')
        print(f'Weight of 2 entries: {weight_for_2}')   
    return weights

# shuffling training dataframe
# for some reason my model likes this but freaks out if I dont do something similar
def shuffle_pd(dataframe, randomness=42):
    ## up and downsampling tweets
    class_2 = dataframe[dataframe['label'] == 2]
    class_1 = dataframe[dataframe['label'] == 1]
    class_0 = dataframe[dataframe['label'] == 0]  #.sample(n=1000)

    shuffled = shuffle(pd.concat([class_2, class_1, class_0], axis=0), random_state=randomness)
    return shuffled
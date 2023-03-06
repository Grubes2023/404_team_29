from import_file import *

model_parameter = 'dense_layer_nodes'
model_parameter_values = [  
                            64,
]

#########################
## My model parameters ##
#########################
BASE_MODEL_VERSION = '0.3.2_saddasd'
VOCAB_SIZE = 7200
MAX_LEN = 250

OUTPUT_LAYER_DIM = 250
LSTM_LAYER_NODES = 128
DENSE_LAYER_NODES = 768
DROPOUT_CHANCE = 0.2
DENSE_LAYER_ACTIVATION = 'relu'

NUM_EPOCHS = 8
EPOCH_TO_CHECK_OVERFITTING = 3
PATIENCE = 2
BATCH_SIZE = 48 # 128 if on a GPU
VAL_SIZE = 0.2
VERBOSE_TRAINING = 1

MY_RANDOM_STATE = 42

def save_model_and_tok(model_version, model, token):
    ### Saving the Model ###
    parent_dir = 'C:\\Users\\Brandon\\Documents\\AI Stuff\\NLP model for 403\\trained_models\\'
    directory = 'version_' + model_version
    model_path = path.join(parent_dir, directory)
    mkdir(model_path)
    model.save(model_path)

    ### Saving the Tokenizer ###
    tok_file = 'tokenizer_version_' + model_version +'.pickle'
    tok_par_directory = 'C:\\Users\\Brandon\\Documents\\AI Stuff\\NLP model for 403\\tokenizers\\'
    tok_path = tok_par_directory + tok_file
    with open(tok_path, 'wb') as handle:
        pickle.dump(token, handle, protocol=pickle.HIGHEST_PROTOCOL)

#creating a function to prepocess tweet
def data_processing(tweet):
    tweet = tweet.lower()                                                         # Make tweet lowercase for consistency
    tweet = re.sub(r"https\S+|www\S+http\S+", '', tweet, flags = re.MULTILINE)    # get rid of any websites in tweet

    tweet = re.sub(r'\@w+|\#','', tweet)                                        
    tweet = re.sub(r'[^\w\s]','',tweet)
    tweet = re.sub(r'ð','',tweet)  
    return tweet

# time to get the stem (lemma) of each word in the tweet
lemmatizer = WordNetLemmatizer()
def lemmatizing(data):
    # split string into list of words
    word_list = data.split()
    # lemmatize each word in the list
    word_list = [lemmatizer.lemmatize(word) for word in word_list]
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

tweet_df = pd.read_csv('disaster_training_multiclass.csv')

preprocess(tweet_df)

# lemmatize all the tweets
tweet_df.tweet = tweet_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer

## up and downsampling tweets
class_2 = tweet_df[tweet_df['label'] == 2]
class_1 = tweet_df[tweet_df['label'] == 1]
class_0 = tweet_df[tweet_df['label'] == 0]  #.sample(n=1000)

shuffled_df = shuffle(pd.concat([class_2, class_1, class_0], axis=0), random_state=MY_RANDOM_STATE)

# getting data into training and testing sets
features = shuffled_df['tweet']
labels = shuffled_df['label']
X_train, X_val, Y_train, Y_val = train_test_split(features,
                                                  labels,
                                                  test_size=VAL_SIZE,
                                                  random_state=MY_RANDOM_STATE)


# create a tokenizer to tokenize the text (words -> numbers)
tok = Tokenizer(num_words=VOCAB_SIZE)
tok.fit_on_texts(X_train)

# apply tokenizer to tweets and pad sequences tget everything the same length
sequences = tok.texts_to_sequences(X_train)
sequences_matrix = pad_sequences(sequences, maxlen=MAX_LEN)

# apply tokenizer and pad sequences to validation data
val_sequences = tok.texts_to_sequences(X_val)
val_sequences_matrix = pad_sequences(val_sequences, maxlen=MAX_LEN)

#############
### MODEL ###
#############
def my_model(parameter_value):
    model = Sequential()
    model.add(Input(name='inputs',shape=[MAX_LEN]))
    model.add(Embedding(VOCAB_SIZE,OUTPUT_LAYER_DIM,input_length=MAX_LEN))

    # adding a Long-Short term memory layer. This is kinda the NLP part of model
    model.add(LSTM(LSTM_LAYER_NODES, return_sequences=True))
    model.add(Dropout(DROPOUT_CHANCE))
    model.add(LSTM(LSTM_LAYER_NODES, return_sequences=True))
    model.add(Dropout(DROPOUT_CHANCE))
    model.add(LSTM(LSTM_LAYER_NODES))

    # adding a dense/activation/dropout block
    model.add(Dense(parameter_value,name='Forward_Comp_1', activation=DENSE_LAYER_ACTIVATION))
    model.add(Dropout(DROPOUT_CHANCE))

    model.add(Dense((parameter_value/2),name='Forward_Comp_2', activation=DENSE_LAYER_ACTIVATION))
    model.add(Dropout(DROPOUT_CHANCE))

    # adding the final output layer
    model.add(Dense(3,name='output', activation='softmax'))
    return model

twos = Counter(Y_train)[2]
ones = Counter(Y_train)[1]
zeros = Counter(Y_train)[0]
length = float(ones + zeros+ twos)
weight_for_0 =  1.0 - float(zeros/length)
weight_for_1 = 1.0 - float(ones/length)
weight_for_2 = 1.0 - float(twos/length)
class_weights = {0: weight_for_0, 1: weight_for_1, 2: weight_for_2}

Y_train= to_categorical(Y_train)
Y_val= to_categorical(Y_val)

for i in range(len(model_parameter_values)):
    value = model_parameter_values[i]
    model = my_model(value)
    model.summary()
    print(f"\n{model_parameter} = {value}")

    # compile the model (does NOT do any training or predicting)
    model.compile(loss=CategoricalCrossentropy(),optimizer=Adam(), metrics=['Recall', 'Precision', 'accuracy'])

    # callback to stop training if starting to overtrain
    ES_callback = EarlyStopping(monitor='loss', min_delta=0.0001, 
                                start_from_epoch=EPOCH_TO_CHECK_OVERFITTING, mode='max', 
                                restore_best_weights=True, 
                                patience=PATIENCE)

    # TRAINING
    model.trainable = True
    model.fit(sequences_matrix,Y_train,
            batch_size=BATCH_SIZE,epochs=NUM_EPOCHS,
            validation_data=(val_sequences_matrix, Y_val),
            verbose=VERBOSE_TRAINING,
            callbacks=[ES_callback],
            class_weight=class_weights)
    model.trainable = False

    model_v = BASE_MODEL_VERSION + "_" + model_parameter + "_" + str(value)
    # saving the model and tokenizer to call in the testing python file
    save_model_and_tok(model_version=model_v, model=model, token=tok)

print("\nFINISHED BATCH TRAINING\n")
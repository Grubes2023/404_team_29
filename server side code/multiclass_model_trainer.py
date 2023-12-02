from import_file import *   # imports all external libraries
# from my_constants import *  # imports all my model parameters (to ensure consistency)

# getting data
tweet_df = pd.read_csv('disaster_training.csv')

# gets rid of ...  websites, duplicates, other stuff
tweet_df = preprocess(tweet_df)

# lemmatize all the tweets
tweet_df.tweet = tweet_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer

shuffled_df = shuffle_pd(tweet_df, randomness=MY_RANDOM_STATE)

# getting data into training and testing sets
features = shuffled_df['tweet']
labels = shuffled_df['label']
X_train, X_val, Y_train, Y_val = train_test_split(features,
                                                  labels,
                                                  stratify=labels,    #makes training and validation sets look like original dataset (same percentages ish)
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

class_weights = get_weights(Y_train)

model = create_model()

model.summary()

# 1 bit encodes labels  [0]->[1,0,0] ,  [1] -> [0,1,0]  ,  [2] -> [0,0,1]
# required for categoricalentropy
Y_train = to_categorical(Y_train)
Y_val = to_categorical(Y_val)

# compile the model (does NOT do any training or predicting)
model.compile(loss=CategoricalCrossentropy(), optimizer=Adam(), metrics=['accuracy', 'Recall', 'Precision'])

# callback to stop training if starting to overtrain
ES_callback = EarlyStopping(monitor='loss', min_delta=0.005, 
                            start_from_epoch=EPOCH_TO_CHECK_OVERFITTING,
                            mode='auto', 
                            restore_best_weights=True, 
                            patience=PATIENCE)

# TRAINING
model.trainable = True
hist = model.fit(sequences_matrix,Y_train,
                batch_size=BATCH_SIZE,epochs=NUM_EPOCHS,
                validation_data=(val_sequences_matrix, Y_val), # comment out when final model
                verbose=VERBOSE_TRAINING,
                callbacks=[ES_callback],
                class_weight=class_weights)
model.trainable = False

# saving the model and tokenizer to call in the testing python file
save_model_and_tok(model_version='1.2', model=model, history=hist, token=tok)

print('Finished Training')
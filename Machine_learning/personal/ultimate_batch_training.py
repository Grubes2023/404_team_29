from import_file import *

lstm_layers_list = [2] # [3]
lstm_nodes_list = [256, 512] # [64, 128, 256, 512]

dense_layers_list =  [2, 3, 4]
dense_nodes_list = [64, 128, 256, 512, 1024]

tweet_df = pd.read_csv('disaster_training.csv')

# format [1, 2, 3]  where each number = [lstm_layers, lstm_nodes, dense_layers, dense_nodes] 
final_parameters_test = [
                        [1,64,1,256], [1,128,2,128], [1,128,4,512] , [1,512,3,64],
                        [2,64,2,128], [2,64,4,64], [2,128,3,256], [2,128,4,64], [2,256,2, 512], [2,256,3,64]
                        ]

preprocess(tweet_df)

# lemmatize all the tweets
tweet_df.tweet = tweet_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer

shuffled_df = shuffle_pd(tweet_df, randomness=MY_RANDOM_STATE)

# Very ugly nested for loops to do ultimate batch training
for i in range(len(lstm_layers_list)):
    lstm_layers = lstm_layers_list[i]

    for j in range(len(lstm_nodes_list)):
 
        lstm_nodes = lstm_nodes_list[j]
        
        for k in range(len(dense_layers_list)):

            dense_layers = dense_layers_list[k]

            for l in range(len(dense_nodes_list)):

                dense_nodes = dense_nodes_list[l]
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

                # get weights to help with uneven dataset
                class_weights = get_weights(Y_train, printing=False)

                # one bit encode training and eval labels (for categorical crossentropy)
                Y_train = to_categorical(Y_train)
                Y_val = to_categorical(Y_val)
                

                model = create_model(num_lstm_layers=lstm_layers
                                    ,lstm_nodes=lstm_nodes
                                    ,num_dense_layers=dense_layers
                                    ,dense_layer_nodes=dense_nodes
                                    )  
                model.summary()
                print(f"\nNUM LSTM LAYERS = {lstm_layers}")
                print(f"MAX LSTM NODES = {lstm_nodes}")
                print(f"NUM DENSE LAYERS = {dense_layers}")
                print(f"MAX DENSE NODES = {dense_nodes}\n")

                # compile the model (does NOT do any training or predicting)
                model.compile(loss=CategoricalCrossentropy(),optimizer=Adam(), metrics=['Recall', 'Precision', 'accuracy'])

                # arbitrary value to make sure model can warm up the layers 
                epoch_check = (lstm_layers + dense_layers) + 3

                # callback to stop training if starting to overtrain
                ES_callback = EarlyStopping(monitor='loss', min_delta=0.001, 
                                            start_from_epoch=epoch_check, #EPOCH_TO_CHECK_OVERFITTING, 
                                            mode='min', 
                                            restore_best_weights=True, 
                                            patience=PATIENCE)

                # TRAINING
                model.trainable = True
                hist = model.fit(sequences_matrix,Y_train,
                        batch_size=BATCH_SIZE,epochs=NUM_EPOCHS,
                        validation_data=(val_sequences_matrix,Y_val),
                        verbose=VERBOSE_TRAINING,
                        callbacks=[ES_callback],
                        class_weight=class_weights)
                model.trainable = False

                # model names for easy identification later
                model_v = BASE_MODEL_VERSION + "_lstm_" + str(lstm_layers) + 'x' + str(lstm_nodes)
                model_v = model_v + "_dense_" + str(dense_layers) +  'x'  + str(dense_nodes)
                # saving the model and tokenizer to call in the testing python file
                save_model_and_tok(model_version=model_v, model=model, history=hist, token=tok)


print("\nFINISHED BATCH TRAINING\n")
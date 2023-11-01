from import_file import *
import matplotlib.pyplot as plt

batch_testing = False
DISP_CONFUSION_MATRIX = False
current_testing_version = ''
# only for batch testing
def get_model_version(model_base
                      ,num_lstm_layers
                      ,num_lstm_nodes
                      ,num_dense_layers
                      ,num_dense_nodes):
    model_v = model_base + "_lstm_" + str(num_lstm_layers) + 'x' + str(num_lstm_nodes)
    model_v = model_v + "_dense_" + str(num_dense_layers) +  'x'  + str(num_dense_nodes)
    return model_v

def confusion_calculations(confusion_matrix, true_labels, predicted_labels, model_version):
    perfect = confusion_matrix[0][0] + confusion_matrix[1][1] + confusion_matrix[2][2]
    pos_threats_detect = confusion_matrix[1][1] + confusion_matrix[2][2] + confusion_matrix[1][2] + confusion_matrix[2][1]
    false_no_threats = confusion_matrix[1][0] + confusion_matrix[2][0]
    false_threats = confusion_matrix[0][1] + confusion_matrix[0][2]
    modified_recall = round(pos_threats_detect/(pos_threats_detect+false_no_threats), 3) * 100
    modified_precision = round(pos_threats_detect/(pos_threats_detect+false_threats), 3) * 100
    inner_accuracy = round((confusion_matrix[1][1] + confusion_matrix[2][2]) / (confusion_matrix[1][2] + confusion_matrix[2][1] + confusion_matrix[1][1] + confusion_matrix[2][2]),  3) * 100
    print(f'Model Version ({model_version})')
    # print(f'Total Tweets : {len(true_labels)}')
    print(f'Unconfident Tweets : {unconfident_predictions}')
    # print(f'Very Confident Tweets : {very_confident}')
    print(f'Very Confident Right : {very_confident_right}')
    print(f'Very Confident Wrong : {very_confident_wrong}')
    print(f'Perfect Predictions : {perfect}')
    print(f'Modified Recall : {round(modified_recall,1)} %')
    print(f'Modified Precision : {round(modified_precision,1)} %')
    print(f'The Inner Accuracy (between 1 and 2) is : {round(inner_accuracy,1)} %')

# format [1, 2, 3]  where each number = [lstm_layers, lstm_nodes, dense_layers, dense_nodes] 
final_parameters_test = [
                    [1,64,1,256], [1,128,2,128], [1,128,4,512] , [1,512,3,64],
                    [2,64,2,128], [2,64,4,64], [2,128,3,256], [2,128,4,64], [2,256,2, 512], [2,256,3,64]
                    ]

for i in range(len(final_parameters_test)):
    lstm_layers = final_parameters_test[i][0]
    lstm_nodes = final_parameters_test[i][1]
    dense_layers = final_parameters_test[i][2]
    dense_nodes = final_parameters_test[i][3]

    if (batch_testing):
        current_testing_version = get_model_version(model_base = BASE_MODEL_VERSION
                                            ,num_lstm_layers=lstm_layers
                                            ,num_lstm_nodes=lstm_nodes
                                            ,num_dense_layers=dense_layers
                                            ,num_dense_nodes=dense_nodes
                                            )
    else:
        current_testing_version = BASE_MODEL_VERSION

    # actual testing portion
    model, tok = load_model_and_tok(current_testing_version)

    tweet_df = pd.read_csv('ultimate_testing.csv')

    preprocess(tweet_df)
    # lemmatize all the tweets
    tweet_df.tweet = tweet_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer
        
    # getting my Testing Dataframe
    my_dataframe = shuffle_pd(tweet_df)
    # getting data into sets
    features = my_dataframe['tweet']
    labels = my_dataframe['label']
    seq = tok.texts_to_sequences(features)
    padded = pad_sequences(seq, maxlen=MAX_LEN)
    pred = model.predict(padded)
    total_tweets = len(labels)

    # containers and statistic measurement initialization
    pred_preds = []
    confidences = []
    very_confident = 0
    very_confident_right = 0
    very_confident_wrong = 0
    unconfident_predictions = 0
    confident_wrong_preds = []
    unconfident = []
    passed_on = []

    # parsing predictions
    for i in range(len(features)):
        prediction = np.argmax(pred[i])
        confidence = round(pred[i][prediction]*100,3)
        pred_preds.append(prediction)
        confidences.append(confidence)
        if (confidences[i] >= MIN_CONFIDENCE_LEVEL):
            very_confident = very_confident + 1
            if ((prediction == 1 and labels[i] == 0)  or  (prediction == 2 and labels[i] == 0)):
                very_confident_wrong += 1
                confident_wrong_preds.append([features[i], CATEGORIES[prediction], CATEGORIES[labels[i]] , confidence])
            else:
                very_confident_right += 1
            # if threat detected and model is confident, pass on to next stage
            if (prediction >= 1):
                passed_on.append([features[i], CATEGORIES[prediction], confidence])
        else:
            unconfident_predictions += 1
            unconfident.append([features[i], CATEGORIES[prediction], CATEGORIES[labels[i]] , confidence])

    # getting a confusion matrix
    conf = confusion_matrix(labels, pred_preds)

    ## Personal testing information printout
    if (EXPLICIT_PRINTING):
        print('')
        for i in range(len(unconfident)):
            print(f'Unconfident Tweets:\n{unconfident[i][0]}')
            print(f'Predicted : {unconfident[i][1]} when it was really {unconfident[i][2]}')
            print(f'The Model was {round(unconfident[i][3], 1)}% confident')
            print('')
        for i in range(len(confident_wrong_preds)):
            print(f'Confidently WRONG Tweets:\n{confident_wrong_preds[i][0]}')
            print(f'Predicted : {confident_wrong_preds[i][1]} when it was really {confident_wrong_preds[i][2]}')
            print(f'The Model was {round(confident_wrong_preds[i][3], 1)}% confident')
            print('')

        ## displaying which tweets would have been passed on to the next subsystem
        for i in range(len(passed_on)):
            print(f'Passed on Tweet:\n{passed_on[i][0]}\nCategory: {passed_on[i][1]}\nConfidence: {round(passed_on[i][2])} %\n')

    print('')
    ## personal testing calculations
    confusion_calculations(conf, labels, pred_preds, model_version = current_testing_version)
    print('')
    # if debugging, display the confusion matrix
    if DISP_CONFUSION_MATRIX:
        ConfusionMatrixDisplay(conf).plot()
        my_title = 'Confusion Matrix (Model ' + current_testing_version + ')'
        plt.title(my_title)
        plt.show()
    print('Press Enter to Continue')
    input()
    
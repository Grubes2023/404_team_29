from import_file import *

MAX_LEN = 250
CONFUSION_MAT_DISP = True
MODEL_VERSION = '0.4__multiclass'

CATEGORIES = {
              0 : "No Concern",
              1 : "Of Moderate Concern",
              2 : "An Immediate Threat"
              }

# NOTES FROM TESTING
"""
check: need to break connection between 'BREAKING' and label 1
check: need some example of rain in label 0
check: need some highway crash examples in label 0
verify: need something to connect disaster near a power plant to label 1/2


need some examples of crashing into electrical poles in label 1
need some examples of violent rain in label 1
need some more violent storm examples of label 1
"""


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

# def a function to preprocess a dataframe
def preprocess(dataframe):
    # apply preprocessing function to tweets and save as itself
    dataframe.tweet = dataframe['tweet'].astype(str)
    dataframe.tweet = dataframe['tweet'].apply(data_processing)
    # get rid of any duplicate tweets and save as itself
    dataframe = dataframe.drop_duplicates('tweet')
    # return dataframe

# defining a function to load the model and tokenizer (with guarenteed version control)
def load_model_and_tok(model_version):
    ### loading the model ###
    parent_dir = 'C:\\Users\\Brandon\\Documents\\AI Stuff\\NLP model for 403\\trained_models\\'
    directory = 'version_' + model_version
    model_path = path.join(parent_dir, directory)
    loaded_model = load_model(model_path)

    ### loading the tokenizer ###
    tok_file = 'tokenizer_version_' + model_version +'.pickle'
    tok_par_directory = 'C:\\Users\\Brandon\\Documents\\AI Stuff\\NLP model for 403\\tokenizers\\'
    tok_path = tok_par_directory + tok_file
    with open(tok_path, 'rb') as handle:
        loaded_tok = pickle.load(handle)
        
    return loaded_model, loaded_tok

model, tok = load_model_and_tok(MODEL_VERSION)

tweet_df = pd.read_csv('ultimate_testing.csv')

preprocess(tweet_df)

# lemmatize all the tweets
tweet_df.tweet = tweet_df['tweet'].apply(lambda x: lemmatizing(x))    # apply lemmatizer

lowballs = tweet_df[tweet_df['category'] == 'lowball']
moderate = tweet_df[tweet_df['category'] == 'moderate']
difficult = tweet_df[tweet_df['category'] == 'difficult']

tweet_dataframe = pd.concat([lowballs, moderate, difficult], axis=0)

# getting data into training and testing sets
features = tweet_dataframe['tweet']
labels = tweet_dataframe['label']
"""X_train, X_val, Y_train, Y_val = train_test_split(features,
                                                  labels,
                                                  stratify=labels,
                                                  test_size=0,
                                                  random_state=42)"""

seq = tok.texts_to_sequences(features)
padded = pad_sequences(seq, maxlen=MAX_LEN)
pred = model.predict(padded)
pred_preds = []
confidences = []

for i in range(len(features)):
    print(features[i])
    print("Raw Output of Model : ", pred[i])
    prediction = np.argmax(pred[i])
    confidence = pred[i][prediction]
    pred_preds.append(prediction)
    confidences.append(confidence)
    print("Predicted: ", CATEGORIES[prediction], 'with a confidence of', confidences[i], '\n')


# if debugging, display the confusion matrix
if CONFUSION_MAT_DISP:
    conf = confusion_matrix(labels, pred_preds)
    ConfusionMatrixDisplay(conf).plot()
    plt.show()
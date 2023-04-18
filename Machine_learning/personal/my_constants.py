#########################
## My model parameters ##
#########################
from import_file import getcwd

MY_WORKING_DIRECTORY = getcwd()

BASE_MODEL_VERSION = '0.8'
MY_RANDOM_STATE = 42
MIN_CONFIDENCE_LEVEL = 85 #percent   defines what is sent onward

# parameters for tokenizer and embedding layer
VOCAB_SIZE = 6400
MAX_LEN = 250
OUTPUT_LAYER_DIM = 250

# inner model parameters
NUM_LSTM_LAYERS = 1
LSTM_LAYER_NODES = 128
NUM_DENSE_LAYERS = 4
DENSE_LAYER_NODES = 512
DENSE_LAYER_ACTIVATION = 'relu'
DROPOUT_CHANCE = 0.1

# training parameters
NUM_EPOCHS = 40
EPOCH_TO_CHECK_OVERFITTING = 7
PATIENCE = 2
BATCH_SIZE = 64 # 128 if on a GPU
VAL_SIZE = 0.2
VERBOSE_TRAINING = 1

# testing parameters
# EXPLICIT_PRINTING = True
CATEGORIES = {
              0 : "No Concern",
              1 : "Of Moderate Concern",
              2 : "An Immediate Threat"
              }

EXPLICIT_PRINTING = False
# import the required libraries
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import nltk
# from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils import shuffle

import tensorflow as tf
from keras.optimizers import Adam, RMSprop
from keras.models import Model, load_model, Sequential
from keras.layers import Embedding, LSTM, Dense, Dropout, Input, Activation
from keras.callbacks import EarlyStopping
from keras.utils import pad_sequences, to_categorical
from keras.preprocessing.text import Tokenizer
from keras.losses import SparseCategoricalCrossentropy, CategoricalCrossentropy

from os import mkdir, path
import pickle
from collections import Counter
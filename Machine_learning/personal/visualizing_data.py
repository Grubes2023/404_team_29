from import_file import *
import matplotlib.pyplot as plt

def visulalize(filename):
    tweet_df = pd.read_csv(filename)
    features = tweet_df['tweet']
    labels = tweet_df['label']
    plt.pie(tweet_df['label'].value_counts().values,
        labels = ['No Concern','Moderate Concern','Immediate Threat'],
        autopct='%1.2f%%',
        wedgeprops = {'linewidth': 1})
    plt.title(f'{filename} Dataset with ({len(labels)} Samples)')
    plt.show()

# Visualizing the Data

visulalize('disaster_training.csv')
visulalize('ultimate_testing.csv')
import sqlite3
import nltk
import pandas as pd
import numpy
from tweetCleaner import *

def tweetsForModel(tweets):
    modelTweets = []
    for tweet in tweets:
        modelWords = []
        for word in tweet:
            modelwords.append({word:True})
        modelTweets.append(modelWords)
    return modelTweets

df = pd.read_csv('training.1600000.processed.noemoticon.csv',header=0,names=['target','id','date','flag','user','text'])
df = df.drop(columns=['id','date','flag','user'])
df = df.to_numpy()
posTweets = []
negTweets = []
for tweet in df:
    if int(tweet[0]) == 0:
        negTweets.append(tweet)
    else:
        posTweets.append(tweet)
df[:,1] = tweetCleaner(df[:,1])
print(df)

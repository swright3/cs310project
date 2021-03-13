import sqlite3
import nltk
import pandas as pd
import numpy
from tweetCleaner import *
from sklearn.model_selection import KFold
from multiprocessing.dummy import Pool as ThreadPool

def tweetsForModel(tweets):
    modelTweets = []
    for tweet in tweets:
        modelWords = {}
        for word in tweet:
            modelWords[word] = True
        modelTweets.append(modelWords)
    return modelTweets

def trainModel(traintest):
    train = traintest[0]
    test = traintest[1]
    traindata = []
    testdata = []
    for x in train:
        traindata.append(dataset[x])
    for y in test:
        testdata.append(dataset[y])
    # print('traindata')
    # print(traindata)
    # print('testdata')
    # print(testdata)
    classifier = nltk.NaiveBayesClassifier.train(traindata)
    accuracy = nltk.classify.accuracy(classifier, testdata)
    #features = classifier.show_most_informative_features(10)
    return accuracy

df = pd.read_csv('training.1600000.processed.noemoticon.csv',header=0,names=['target','id','date','flag','user','text'])
df = df.drop(columns=['id','date','flag','user'])
df = df.to_numpy()
posTweets = []
negTweets = []
for tweet in df:
    if int(tweet[0]) == 0:
        negTweets.append(tweet[1])
    else:
        posTweets.append(tweet[1])

cleanPosTweets = tweetCleaner(posTweets)
tweetsToTXT(cleanPosTweets,'cleanPosTweets.txt')
cleanNegTweets = tweetCleaner(negTweets)
tweetsToTXT(cleanNegTweets,'cleanNegTweets.txt')
# modelPosTweets = tweetsForModel(cleanPosTweets)
# modelNegTweets = tweetsForModel(cleanNegTweets)
# posDataset = []
# negDataset = []
# for tweet in modelPosTweets:
#     posDataset.append((tweet,"positive"))
# for tweet in modelNegTweets:
#     negDataset.append((tweet,"negative"))
# global dataset
# dataset = posDataset + negDataset

# kfold = KFold(10, shuffle=True, random_state=1)
# splitData = kfold.split(dataset)

# traintest = []
# for train, test in splitData:
#     traintest.append([train,test])

# pool = ThreadPool(4)
# results = []
# results = pool.map(trainModel, traintest)

# print(results)
# # for train, test in kfold.split(posDataset):
# #     print('train')
# #     for x in train:
# #         print(posDataset[x])
# #     print('test')
# #     for y in test:
# #         print(posDataset[y])

# # pool = ThreadPool(4)
# # results = []
# # results = pool.starmap(trainModel,)
# # for train, test in splitData:
# #     results.append(trainModel(train,test))
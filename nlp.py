import sqlite3
import nltk
import pandas as pd
import numpy
from tweetCleaner import *
from sklearn.model_selection import KFold
import multiprocessing
from nltk.corpus import wordnet as wn
import ast
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

if __name__ == '__main__':
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

    # # with open('cleanPosTweets.txt','r',encoding='utf-8') as f:
    # #     cleanPosTweets = f.read()
    # # with open('cleanNegTweets.txt','r',encoding='utf-8') as f:
    # #     cleanNegTweets = f.read()

    print(':)')
    with multiprocessing.Pool(processes=4) as pool:
        cleanPosTweets = pool.map(tweetCleanerP,posTweets)
        cleanNegTweets = pool.map(tweetCleanerP,negTweets)
    tweetsToCSV(cleanPosTweets,'cleanPosTweets.pkl')
    tweetsToCSV(cleanNegTweets,'cleanNegTweets.pkl')
    cleanPosTweets = tweetsFromCSV('cleanPosTweets.pkl')
    cleanNegTweets = tweetsFromCSV('cleanNegTweets.pkl')
    cleanPosTweets = cleanPosTweets['tweets'].tolist()
    cleanNegTweets = cleanNegTweets['tweets'].tolist()

    modelPosTweets = tweetsForModel(cleanPosTweets)
    modelNegTweets = tweetsForModel(cleanNegTweets)
    posDataset = []
    negDataset = []
    for tweet in modelPosTweets:
        posDataset.append((tweet,"positive"))
    for tweet in modelNegTweets:
        negDataset.append((tweet,"negative"))
    global dataset
    dataset = posDataset + negDataset
    
    testResults = []
    for x in range(20):
        kfold = KFold(10, shuffle=True, random_state=1)
        splitData = kfold.split(dataset)

        traintest = []
        for train, test in splitData:
            traintest.append([train,test])

        pool = ThreadPool(4)
        results = []
        results = pool.map(trainModel,traintest)
        testResults.append(["test"+str(x),results])
    # with multiprocessing.Pool(processes=4) as pool:
    #     results = pool.map(trainModel,traintest)

    with open('testResults.txt','w') as f:
        f.write(str(testResults))


# # for train, test in kfold.split(posDataset):
# #     print('train')
# #     for x in train:
# #         print(posDataset[x])
# #     print('test')
# #     for y in test:
# #         print(posDataset[y])


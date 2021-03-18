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
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle
import random

def getRawTweets(file):                              #used for sample tweets
    df = pd.read_csv(file,header=0,names=['target','id','date','flag','user','text'])
    df = df.drop(columns=['id','date','flag','user'])
    df = df.to_numpy()
    posTweets = []
    negTweets = []
    for tweet in df:
        if int(tweet[0]) == 0:
            negTweets.append(tweet[1])
        else:
            posTweets.append(tweet[1])
    return posTweets, negTweets

def getCollectedTweets(file,party):    #gets new tweets where sentiment = 0
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('SELECT '+party+'Id,text,followers FROM '+party+'Tweets WHERE sentiment = ?;',('0',))
    tweets = c.fetchall()
    for tweet in range(len(tweets)):
        tweets[tweet] = list(tweets[tweet])
    return tweets

def cleanTweets(file):                                    #used for sample tweets
    posTweets, negTweets = getRawTweets(file)
    print(':)')
    with multiprocessing.Pool(processes=4) as pool:
        cleanPosTweets = pool.map(tweetCleanerP,posTweets)
        cleanNegTweets = pool.map(tweetCleanerP,negTweets)
    tweetsToPickle(cleanPosTweets,'cleanPosTweets.pkl')
    tweetsToPickle(cleanNegTweets,'cleanNegTweets.pkl')

def cleanCollectedTweets(file,party):
    collectedTweets = getCollectedTweets(file,party)                            #gets new tweets with sentiment = 0
    with multiprocessing.Pool(processes=4) as pool:                             #uses multiprocessing to clean them
        cleanCollectedTweets = pool.map(collectedTweetCleaner,collectedTweets)  #collectedTweetCleaner imported from tweetCleaner.py
    #tweetsToPickle(cleanCollectedTweets,'clean'+party+'Tweets.pkl')            #returns to collectedTweetProcessor  
    return cleanCollectedTweets

def getCleanTweets(file1,file2):                        #used for sample tweets
    cleanPosTweets = tweetsFromPickle(file1)
    cleanNegTweets = tweetsFromPickle(file2)
    cleanPosTweets = cleanPosTweets['tweets'].tolist()
    cleanNegTweets = cleanNegTweets['tweets'].tolist()
    return cleanPosTweets, cleanNegTweets

def getCleanCollectedTweets(file):                       #not used
    cleanCollected = tweetsFromPickle(file)
    cleanCollected = cleanCollected['tweets'].tolist()
    return cleanCollected

def tweetsForModel(tweets):                             #used for sample tweets
    modelTweets = []
    for tweet in tweets:
        modelWords = {}
        for word in tweet:
            modelWords[word] = True
        modelTweets.append(modelWords)
    return modelTweets

def collectedTweetsForModel(tweets):
    for tweet in range(len(tweets)):
        modelWords = {}
        for word in tweets[tweet][1]:
            modelWords[word] = True
        tweets[tweet][1] = modelWords
    return tweets
        
def labelTweets(modelPosTweets,modelNegTweets):
    posDataset = []
    negDataset = []
    for tweet in modelPosTweets:
        posDataset.append((tweet,"positive"))
    for tweet in modelNegTweets:
        negDataset.append((tweet,"negative"))
    return posDataset, negDataset

def trainTestModel(traintest):
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

def trainModel(dataset):
    classifier = nltk.NaiveBayesClassifier.train(dataset)
    return classifier

def testNaiveBayes():
    cleanPosTweets, cleanNegTweets = getCleanTweets('cleanPosTweets.pkl','cleanNegTweets.pkl')
    modelPosTweets = tweetsForModel(cleanPosTweets)
    modelNegTweets = tweetsForModel(cleanNegTweets)
    posDataset, negDataset = labelTweets(modelPosTweets,modelNegTweets)
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
        results = pool.map(trainTestModel,traintest)
        testResults.append(["test"+str(x),results])

    with open('testResultsNaiveBayes.txt','w') as f:
        f.write(str(testResults))

def trainNaiveBayes():
    cleanPosTweets, cleanNegTweets = getCleanTweets('cleanPosTweets.pkl','cleanNegTweets.pkl')
    modelPosTweets = tweetsForModel(cleanPosTweets)
    modelNegTweets = tweetsForModel(cleanNegTweets)
    posDataset, negDataset = labelTweets(modelPosTweets,modelNegTweets)
    global dataset
    dataset = posDataset + negDataset
    random.shuffle(dataset)
    return trainModel(dataset)

def testVader():
    sia = SentimentIntensityAnalyzer()
    posTweets, negTweets = getRawTweets('training.1600000.processed.noemoticon.csv')
    accuracies = []
    for x in range(10):
        pool = ThreadPool(4)
        posResults = pool.map(sia.polarity_scores,posTweets)
        negResults = pool.map(sia.polarity_scores,negTweets)
        correct = 0
        incorrect = 0
        for result in posResults:
            if result['compound']>0:
                correct += 1
            else:
                incorrect += 1
        for result in negResults:
            if result['compound']<0:
                correct += 1
            else:
                incorrect += 1
        accuracy = correct/(correct+incorrect)
        accuracies.append(accuracy)
    with open('testResultsVader.txt','w') as f:
        f.write(str(accuracies))

def saveClassifier(classifier,file):
    with open(file,'wb') as f:
        pickle.dump(classifier,f)

def loadClassifier(file):
    with open(file,'rb') as f:
        classifier = pickle.load(f)
    return classifier

def analyseCollectedTweets(tweets):
    classifier = loadClassifier('naiveBayesClassifier.pkl')
    tweets = collectedTweetsForModel(tweets)
    for tweet in range(len(tweets)):
        tweets[tweet].append(classifier.classify(tweets[tweet][1]))
    return tweets

def updateSentiment(tweets,party,file):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    for tweet in tweets:
        newSentiment = 0
        if tweet[3] == 'positive':
            newSentiment = '1'
        elif tweet[3] == 'negative':
            newSentiment = '-1'
        c.execute('UPDATE '+party+'Tweets SET sentiment = ? WHERE '+party+'Id = ?;',(newSentiment,tweet[0]))
    conn.commit()
    conn.close()

def collectedTweetProcessor(party,file):
    tweets = cleanCollectedTweets(file,party) #gets tweets with no sentiment and cleans them
    tweets = collectedTweetsForModel(tweets)  #formats tweets for model input
    tweets = analyseCollectedTweets(tweets)   #uses classifier to classify tweets
    updateSentiment(tweets,party,file)        #updates the sentiment in sortedTweets.db

    # posResults = []
    # for tweet in posTweets[:10000]:
    #     posResults.append(sia.polarity_scores(tweet)['compound'])
    # correct = 0
    # incorrect = 0
    # for result in posResults:
    #     if result>0:
    #         correct += 1
    #     else:
    #         incorrect += 1
    # accuracy = correct/(correct+incorrect)
    # print(accuracy)


if __name__ == '__main__':
    collectedTweetProcessor('con','sortedTweets.db')
    print('con')
    collectedTweetProcessor('lab','sortedTweets.db')
    print('lab')
    collectedTweetProcessor('libdem','sortedTweets.db')
    print('libdem')
    collectedTweetProcessor('green','sortedTweets.db')
    print('green')
    # classifier = trainNaiveBayes()
    # saveClassifier(classifier,'naiveBayesClassifier.pkl')
    # cleanPosTweets, cleanNegTweets = getCleanTweets('cleanPosTweets.pkl','cleanNegTweets.pkl')
    # print(cleanPosTweets[:10])
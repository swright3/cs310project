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

#Gets the sample tweets from a csv and sorts them into positive and negative tweets
#Sample tweets are only used when training the naive bayes classifier
def getRawTweets(file):
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

#Gets collected tweets from sortedTweets.db that need to be classified
def getCollectedTweets(file,party):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('SELECT '+party+'Id,text,followers FROM '+party+'Tweets WHERE sentiment = ?;',('0',))
    tweets = c.fetchall()
    for tweet in range(len(tweets)):
        tweets[tweet] = list(tweets[tweet])
    return tweets

#Takes the raw sample tweets, cleans/tokenizes them and saves them to pickle files
def cleanTweets(file):
    posTweets, negTweets = getRawTweets(file)
    print(':)')
    with multiprocessing.Pool(processes=4) as pool:
        cleanPosTweets = pool.map(tweetCleanerP,posTweets)
        cleanNegTweets = pool.map(tweetCleanerP,negTweets)
    tweetsToPickle(cleanPosTweets,'cleanPosTweets.pkl')
    tweetsToPickle(cleanNegTweets,'cleanNegTweets.pkl')

#Takes the raw newly collected tweets and cleans/tokenizes them
def cleanCollectedTweets(file,party):
    collectedTweets = getCollectedTweets(file,party)                            #gets new tweets with sentiment = 0
    with multiprocessing.Pool(processes=4) as pool:                             #uses multiprocessing to clean them
        cleanCollectedTweets = pool.map(collectedTweetCleaner,collectedTweets)  #collectedTweetCleaner imported from tweetCleaner.py
    #tweetsToPickle(cleanCollectedTweets,'clean'+party+'Tweets.pkl')            #returns to collectedTweetProcessor  
    return cleanCollectedTweets

#Gets cleaned sample tweets from their pickle files so they don't have to be tokenized each time the model is trained
def getCleanTweets(file1,file2):
    cleanPosTweets = tweetsFromPickle(file1)
    cleanNegTweets = tweetsFromPickle(file2)
    cleanPosTweets = cleanPosTweets['tweets'].tolist()
    cleanNegTweets = cleanNegTweets['tweets'].tolist()
    return cleanPosTweets, cleanNegTweets

#Not used, here in case I need to load clean collected tweets from a pickle file
def getCleanCollectedTweets(file):
    cleanCollected = tweetsFromPickle(file)
    cleanCollected = cleanCollected['tweets'].tolist()
    return cleanCollected

#Takes the cleaned sample tweets and formats them so the model can use them
#The format is an array of tweet dictionaries, with tokens as keys and True as values e.g. {'happy':True, 'birthday':True}
def tweetsForModel(tweets):
    modelTweets = []
    for tweet in tweets:
        modelWords = {}
        for word in tweet:
            modelWords[word] = True
        modelTweets.append(modelWords)
    return modelTweets

#Takes the cleaned collected tweets and formats them for the model
def collectedTweetsForModel(tweets):
    for tweet in range(len(tweets)):
        modelWords = {}
        for word in tweets[tweet][1]:
            modelWords[word] = True
        tweets[tweet][1] = modelWords
    return tweets

#Takes the sample tweet dictionaries and labels each one positive or negative
def labelTweets(modelPosTweets,modelNegTweets):
    posDataset = []
    negDataset = []
    for tweet in modelPosTweets:
        posDataset.append((tweet,"positive"))
    for tweet in modelNegTweets:
        negDataset.append((tweet,"negative"))
    return posDataset, negDataset

#Trains the naive bayes classifier 
def trainNaiveBayes():
    cleanPosTweets, cleanNegTweets = getCleanTweets('cleanPosTweets.pkl','cleanNegTweets.pkl')
    modelPosTweets = tweetsForModel(cleanPosTweets)
    modelNegTweets = tweetsForModel(cleanNegTweets)
    posDataset, negDataset = labelTweets(modelPosTweets,modelNegTweets)
    global dataset
    dataset = posDataset + negDataset
    random.shuffle(dataset)
    return trainModel(dataset)

#Trains the naive bayes model
def trainModel(dataset):
    classifier = nltk.NaiveBayesClassifier.train(dataset)
    return classifier

#Uses k fold cross validation to split the tweets in to training and test tweets with a 9:1 split
#Utilises multiprocessing to create a pool of 4 processes which severely reduces running time
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

#Takes an array with training tweets and test tweets and uses them to train and test the naive bayes model
def trainTestModel(traintest):
    train = traintest[0]
    test = traintest[1]
    traindata = []
    testdata = []
    for x in train:
        traindata.append(dataset[x])
    for y in test:
        testdata.append(dataset[y])
    classifier = nltk.NaiveBayesClassifier.train(traindata)
    accuracy = nltk.classify.accuracy(classifier, testdata)
    #features = classifier.show_most_informative_features(10)
    return accuracy

#Tests the accuracy of the pretrained vader classifier using the sample tweets
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

#Saves the trained naive bayes classifier to pkl file so it doesn't need to be trained every time
def saveClassifier(classifier,file):
    with open(file,'wb') as f:
        pickle.dump(classifier,f)

#Loads the trained classifier from pkl file
def loadClassifier(file):
    with open(file,'rb') as f:
        classifier = pickle.load(f)
    return classifier

#Takes the newly collected tweets and feeds them into the classifier, returns the sentiment of each tweet
def analyseCollectedTweets(tweets):
    classifier = loadClassifier('naiveBayesClassifier.pkl')
    tweets = collectedTweetsForModel(tweets)
    for tweet in range(len(tweets)):
        tweets[tweet].append(classifier.classify(tweets[tweet][1]))
    return tweets

#Updates the newly evaluated sentiment to the sortedTweets database
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

#Classifies all new tweets
def collectedTweetProcessor(party,file):
    tweets = cleanCollectedTweets(file,party) #gets tweets with no sentiment and cleans them
    print('cleaned ' + party + ' tweets examples:')
    print(tweets[:5])
    tweets = collectedTweetsForModel(tweets)  #formats tweets for model input
    tweets = analyseCollectedTweets(tweets)   #uses classifier to classify tweets
    updateSentiment(tweets,party,file)        #updates the sentiment in sortedTweets.db

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
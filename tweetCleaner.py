import nltk
import pandas as pd
import numpy
import re
import string
from nltk.corpus import wordnet as wn

def tweetCleaner(tweets):
    tokenizedTweets = tokenize(tweets)
    normalizedTweets = normalize(tokenizedTweets)
    lemmatizedTweets = lemmatize(normalizedTweets)
    cleanedTweets = clean(lemmatizedTweets)
    return cleanedTweets

def tokenize(tweets):
    tokenizedTweets = []
    for tweet in tweets:
        tokenizedTweets.append(nltk.tokenize.casual.casual_tokenize(tweet))
    return tokenizedTweets

def clean(lemmatizedTweets):
    cleanedTweets = []
    for tweet in lemmatizedTweets:
        cleanedWords = []
        for word in tweet:
            word = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                        '(?:%[0-9a-fA-F][0-9a-fA-F]))+','',word)
            word = re.sub("(@[A-Za-z0-9_]+)","",word)

            if len(word)>0 and word not in nltk.corpus.stopwords.words('english') and word not in string.punctuation:
                cleanedWords.append(word.lower())
        cleanedTweets.append(cleanedWords)
    return cleanedTweets

def normalize(tokenizedTweets):
    normalizedTweets = []
    for tweet in tokenizedTweets:
        normalizedTweets.append(nltk.tag.pos_tag(tweet))
    return normalizedTweets

def lemmatize(normalizedTweets):
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    lemmatizedTweets = []
    for tweet in normalizedTweets:
        lemmatizedWords = []
        for word, tag in tweet:
            if tag.startswith('NN'):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'
            lemmatizedWords.append(lemmatizer.lemmatize(word, pos))
        lemmatizedTweets.append(lemmatizedWords)
    return lemmatizedTweets

def tweetCleanerP(tweet):
    wn.ensure_loaded()
    tokenizedTweet = tokenizeP(tweet)
    normalizedTweet = normalizeP(tokenizedTweet)
    lemmatizedTweet = lemmatizeP(normalizedTweet)
    cleanedTweet = cleanP(lemmatizedTweet)
    return cleanedTweet

def tokenizeP(tweet):
    return nltk.tokenize.casual.casual_tokenize(tweet)

def cleanP(lemmatizedTweet):
    cleanedWords = []
    for word in lemmatizedTweet:
        word = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                    '(?:%[0-9a-fA-F][0-9a-fA-F]))+','',word)
        word = re.sub("(@[A-Za-z0-9_]+)","",word)

        if len(word)>0 and (word.lower() not in nltk.corpus.stopwords.words('english')) and word not in string.punctuation:
            cleanedWords.append(word.lower())
    return cleanedWords

def normalizeP(tokenizedTweet):
    return nltk.tag.pos_tag(tokenizedTweet)

def lemmatizeP(normalizedTweet):
    lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
    lemmatizedWords = []
    for word, tag in normalizedTweet:
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatizedWords.append(lemmatizer.lemmatize(word, pos))
    return lemmatizedWords

def removeStopwords(tweet):
    result = []
    for word in tweet:
        if word not in nltk.corpus.stopwords.words('english'):
            result.append(word)
    return result

def tweetsToTXT(tweets,file):
    # finalTweets = []
    # for tweet in tweets:
    #     newTweet = []
    #     for word in tweet:
    #         if word not in nltk.corpus.stopwords.words():
    #             newTweet.append(word)
    #     finalTweets.append(newTweet)

    with open(file,'w',encoding="utf-8") as f:
        f.write(str(tweets))

def tweetsToPickle(tweets,file):
    df = pd.DataFrame(((tweet,) for tweet in tweets), columns=['tweets'])
    df.to_pickle(file)

def tweetsFromTXT(file):
    with open(file,'r') as f:
        return f.read()

def tweetsFromPickle(file):
    return pd.read_pickle(file)

# df = pd.read_csv('training.1600000.processed.noemoticon.csv',header=0,names=['target','id','date','flag','user','text'])
# df = df.drop(columns=['id','date','flag','user'])
# df2 = df.head(20)
# df2 = df2.append(df.tail(20))
# df2 = df2.to_numpy()
# tweetCleaner(df2[:,1])

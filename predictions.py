import sqlite3
import sklearn
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
from relateTweetsToPolls import getPollRelevantTweets
from sklearn.preprocessing import PolynomialFeatures

def getPercentageAndSentiment(pollId,party,conn,c):
    sql = 'SELECT '+party+'Tweets.sentiment,polls.'+party+' FROM polls INNER JOIN '+party+'PollTweets ON '+party+'PollTweets.pollId = polls.id INNER JOIN '+party+'Tweets ON '+party+'Tweets.'+party+'Id = '+party+'PollTweets.partyId WHERE polls.id = ?;'
    c.execute(sql,(pollId,))
    sentAndPercent = c.fetchall()
    return sentAndPercent

def calculateTotalSentiment(sentAndPercent):
    pos = 0
    neg = 0
    for data in sentAndPercent:
        if data[0] == '1':
            pos += 1
        elif data[0] == '-1':
            neg += 1
    return ((pos-neg)/(pos+neg))*100

def getPercentageAndSentimentScaledByFollowers(pollId,party,conn,c):
    sql = 'SELECT '+party+'Tweets.sentiment,polls.'+party+','+party+'Tweets.followers FROM polls INNER JOIN '+party+'PollTweets ON '+party+'PollTweets.pollId = polls.id INNER JOIN '+party+'Tweets ON '+party+'Tweets.'+party+'Id = '+party+'PollTweets.partyId WHERE polls.id = ?;'
    c.execute(sql,(pollId,))
    sentAndPercent = c.fetchall()
    return sentAndPercent

def calculateTotalSentimentScaledByFollowers(sentAndPercent):
    pos = 0
    neg = 0
    for data in sentAndPercent:
        if data[0] == '1':
            pos += int(data[0])*data[2]
        elif data[0] == '-1':
            neg += int(data[0])*data[2]*-1
    return ((pos-neg)/(pos+neg))*100

def collectData(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT pollId from '+party+'PollTweets')
    pollIds = c.fetchall()
    results = []
    for id in pollIds:
        sentAndPercent = getPercentageAndSentiment(id[0],party,conn,c)
        totalSentiment = calculateTotalSentiment(sentAndPercent)
        results.append([totalSentiment,sentAndPercent[0][1]])
    conn.close()
    return results

def collectDataScaledByFollowers(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT pollId from '+party+'PollTweets')
    pollIds = c.fetchall()
    results = []
    for id in pollIds:
        sentAndPercent = getPercentageAndSentimentScaledByFollowers(id[0],party,conn,c)
        totalSentiment = calculateTotalSentimentScaledByFollowers(sentAndPercent)
        results.append([totalSentiment,sentAndPercent[0][1]])
    conn.close()
    return results

def trainModel(data):
    x = []
    y = []
    for pair in data:
        x.append(pair[0])
        y.append(int(pair[1]))
    x = np.array(x)
    y = np.array(y)
    x = x.reshape((-1, 1))
    model = LinearRegression().fit(x,y)
    r_sq = model.score(x, y)
    modelMetrics = []
    modelMetrics.append(r_sq)
    modelMetrics.append(model.intercept_)
    modelMetrics.append(model.coef_[0])
    return model, modelMetrics

def trainPolynomialModel(data,degree):
    x = []
    y = []
    for pair in data:
        x.append(pair[0])
        y.append(int(pair[1]))
    x = np.array(x)
    y = np.array(y)
    x = x.reshape((-1, 1))
    x_ = PolynomialFeatures(degree=degree, include_bias=False).fit_transform(x)
    model = LinearRegression().fit(x_,y)
    r_sq = model.score(x_, y)
    modelMetrics = []
    modelMetrics.append(r_sq)
    modelMetrics.append(model.intercept_)
    modelMetrics.append(model.coef_[0])
    modelMetrics.append(model.coef_[1])
    print(modelMetrics)
    #return model, modelMetrics

def predictPercentage(party,dates,polynomial,degree):
    data = collectData(party)
    if not polynomial:
        model, modelMetrics = trainModel(data)
    else:
        model, modelMetrics = trainPolynomialModel(data,degree)
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    predictions = []
    for date in dates:
        tweets = getPollRelevantTweets(date,conn,c,party)
        sentiments = []
        for tweet in tweets:
            c.execute('SELECT sentiment FROM '+party+'Tweets WHERE '+party+'Id = ?;',(tweet,))
            sentiments.append(c.fetchone())
        totalSentiment = calculateTotalSentiment(sentiments)
        x = np.array([[totalSentiment]])
        if polynomial:
            x = PolynomialFeatures(degree=degree, include_bias=False).fit_transform(x)
        predictions.append(model.predict(x))
    return predictions, modelMetrics

def predictPercentageScaledByFollowers(party,dates,polynomial,degree):
    data = collectDataScaledByFollowers(party)
    if not polynomial:
        model, modelMetrics = trainModel(data)
    else:
        model, modelMetrics = trainPolynomialModel(data,degree)
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    predictions = []
    for date in dates:
        tweets = getPollRelevantTweets(date,conn,c,party)
        sentiments = []
        for tweet in tweets:
            c.execute('SELECT sentiment,date,followers FROM '+party+'Tweets WHERE '+party+'Id = ?;',(tweet,))
            sentiments.append(c.fetchone())
        totalSentiment = calculateTotalSentimentScaledByFollowers(sentiments)
        x = np.array([[totalSentiment]])
        if polynomial:
            x = PolynomialFeatures(degree=degree, include_bias=False).fit_transform(x)
        predictions.append(model.predict(x))
    return predictions, modelMetrics

def predictPercentageFromPastPolls():
    print()

if __name__ == '__main__':
    predictPercentage('con','2021-03-14')

import sqlite3
import sklearn
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
from relateTweetsToPolls import getPollRelevantTweets
from sklearn.preprocessing import PolynomialFeatures

#Selects the vote percentage and sentiment for each poll
def getPercentageAndSentiment(pollId,party,conn,c):
    sql = 'SELECT '+party+'Tweets.sentiment,polls.'+party+' FROM polls INNER JOIN '+party+'PollTweets ON '+party+'PollTweets.pollId = polls.id INNER JOIN '+party+'Tweets ON '+party+'Tweets.'+party+'Id = '+party+'PollTweets.partyId WHERE polls.id = ?;'
    c.execute(sql,(pollId,))
    sentAndPercent = c.fetchall()
    return sentAndPercent

#Takes all sentiments and calculates the overall sentiment
def calculateTotalSentiment(sentAndPercent):
    pos = 0
    neg = 0
    for data in sentAndPercent:
        if data[0] == '1':
            pos += 1
        elif data[0] == '-1':
            neg += 1
    return ((pos-neg)/(pos+neg))*100

#Selects sentiment, followers and vote percentage for each poll's tweets
def getPercentageAndSentimentScaledByFollowers(pollId,party,conn,c):
    sql = 'SELECT '+party+'Tweets.sentiment,polls.'+party+','+party+'Tweets.followers FROM polls INNER JOIN '+party+'PollTweets ON '+party+'PollTweets.pollId = polls.id INNER JOIN '+party+'Tweets ON '+party+'Tweets.'+party+'Id = '+party+'PollTweets.partyId WHERE polls.id = ?;'
    c.execute(sql,(pollId,))
    sentAndPercent = c.fetchall()
    return sentAndPercent

#Takes all sentiments multiplied by the followers of the poster and calculates the overall sentiment
def calculateTotalSentimentScaledByFollowers(sentAndPercent):
    pos = 0
    neg = 0
    for data in sentAndPercent:
        if data[0] == '1':
            pos += int(data[0])*data[2]
        elif data[0] == '-1':
            neg += int(data[0])*data[2]*-1
    return ((pos-neg)/(pos+neg))*100

#Gets the data needed for predictions, overall sentiment and the percentage the party got in each poll
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

#Does the same as collectData but the overall sentiment is scaled by the no. of followers of the poster of each tweet
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

#Formats the sentiments and percentage votes and uses them to train a linear regression model
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

#Formats the sentiments and percentage votes and uses them to train a polynomial regression model
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
    modelMetrics.append(model.coef_)
    return model, modelMetrics

#Trains the appropriate model and then uses it to predict the outcome of polls on given dates
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

#The same as predictPercentage but with follower scaled sentiment
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

#Main function that gets the predicted percentages for each party on given dates
def finalPredictions(dates,polynomial,degree):
    for party in ['con','lab','libdem','green']:
        predictions, modelMetrics = predictPercentage(party, dates, polynomial, degree)
        for prediction in range(len(predictions)):
            print(party + ' party percentage vote prediction for ' + dates[prediction] + ': ' + str(round(predictions[prediction][0],2)) + '%')

if __name__ == '__main__':
    finalPredictions(['2021-3-14','2021-3-15'],False,1)

import sqlite3
import sklearn
from sklearn.linear_model import LinearRegression
import numpy as np
import datetime
from relateTweetsToPolls import getPollRelevantTweets

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
    print(r_sq)
    return model

def predictPercentage(model,party,date):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    tweets = getPollRelevantTweets(date,conn,c,party)
    sentiments = []
    for tweet in tweets:
        c.execute('SELECT sentiment FROM '+party+'Tweets WHERE '+party+'Id = ?;',(tweet,))
        sentiments.append(c.fetchone())
    totalSentiment = calculateTotalSentiment(sentiments)
    x = np.array([[totalSentiment]])
    print(model.predict(x))

if __name__ == '__main__':
    data = collectData('con')
    model = trainModel(data)
    predictPercentage(model,'con','2021-03-13')
    data = collectData('lab')
    model = trainModel(data)
    predictPercentage(model,'lab','2021-03-13')
    data = collectData('libdem')
    model = trainModel(data)
    predictPercentage(model,'libdem','2021-03-13')
    data = collectData('green')
    model = trainModel(data)
    predictPercentage(model,'green','2021-03-13')

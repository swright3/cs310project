import sqlite3
import sklearn
from sklearn.linear_model import LinearRegression
import numpy as np

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

if __name__ == '__main__':
    data = collectData('con')
    print(data)
    trainModel(data)
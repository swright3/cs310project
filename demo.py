from selectTweets import sortTweets
from dbcontrol import deleteOldTweets
from nlp import collectedTweetProcessor
from pollparser2 import newPollsToDB
from relatetweetstopolls import fillRelationalTable
from predictions import finalPredictions
from analysis import plotRealVsCalculated
from analysis import plotRealVsCalculatedScaledByFollowers
import sqlite3

if __name__ == '__main__':
    input('First step is to take the newly collected tweets and sort them in to tables for each party they are related to')
    sortTweets()
    print('sorted tweets')
    input('Second, delete sorted tweets from the newly collected tweet database to save storage space')
    deleteOldTweets('ukpoliticstweets.db')
    deleteOldTweets('ukpoliticstweets2.db')
    print('deleted tweets')
    input('Next, run collectedTweetProcessor in nlp.py to classify all of the newly sorted tweets')
    collectedTweetProcessor('con','sortedTweets.db')
    collectedTweetProcessor('lab','sortedTweets.db')
    collectedTweetProcessor('libdem','sortedTweets.db')
    collectedTweetProcessor('green','sortedTweets.db')
    input('Then, use pollparser2.py to update the polls table with the newest poll results')
    newPollsToDB()
    input('Use relational sql to link polls in the polls table to each one of the party tweets tables')
    fillRelationalTable('con')
    fillRelationalTable('lab')
    fillRelationalTable('libdem')
    fillRelationalTable('green')
    print('E.g. SELECT * FROM conPollTweets LIMIT 10;')
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM conPollTweets LIMIT 10;')
    print(c.fetchall())
    input('Finally, there is now enough data to predict the results if a poll were to happen today')
    print('The model evaluates the sentiment of all the tweets from 3 days in the past to the present day')
    finalPredictions(['2021-3-19'],False,1)
    print('You can pass any list of dates to the script to get the predicted outcomes for each date')
    input('Here are some analysis statistics for each poll in the last couple of weeks for the lib dem party')
    print('Linear regression')
    plotRealVsCalculated('libdem',False,1)
    print('Polynomial regression order 2')
    plotRealVsCalculated('libdem',True,2)
    print('Polynomial regression order 3')
    plotRealVsCalculated('libdem',True,3)
    print('Linear regression with sentiments scaled by number of followers')
    plotRealVsCalculatedScaledByFollowers('libdem',False,1)
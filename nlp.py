from nltk.sentiment import *
import sqlite3

conn = sqlite3.connect('sortedTweets.db')
c = conn.cursor()
c.execute('SELECT * FROM conTweets WHERE conId<11')
conTweets = c.fetchall()
sia = SentimentIntensityAnalyzer()
for tweet in conTweets:
    print(sia.polarity_scores(tweet[3]),tweet[3])
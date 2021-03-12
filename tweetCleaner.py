import nltk
import sqlite3

conn = sqlite3.connect('sortedTweets.db')
c = conn.cursor()
c.execute('SELECT conId,id,text FROM conTweets WHERE conId<21;')
conTweets = c.fetchall()
conn.close()
conTokens = []
for tweet in conTweets:
    tokenized = list(tweet)
    tokenized.append(nltk.word_tokenize(tweet[2]))
    conTokens.append(tokenized)
print(conTokens)
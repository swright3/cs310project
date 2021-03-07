from dbcontrol import *

def getDB1Tweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    return c.fetchall()

def conTweets():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS vTweets using fts5(newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party, tokenize="porter unicode61");')
    tweets = getDB1Tweets()
    for tweet in tweets:
        print(tweet)
        c.execute('INSERT INTO vTweets (newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);',tweet)
    c.execute('SELECT * FROM vTweets LIMIT 5;')
    print(c.fetchall())
    c.close()
    conn.commit()
    conn.close()

def getPhrases():
    with open('phrases1.txt','r') as f:
        phrases1 = f.read().split(',')
    with open('phrases2.txt','r') as f:
        phrases2 = f.read().split(',')
    print(phrases1[:-1])

#conTweets()
getPhrases()
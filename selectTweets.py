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
    phrases1, phrases2 = getPhrases()
    placeholders = ''
    for x in range(len(phrases1)):
        placeholders += '?,'
    placeholders = placeholders[:-1] + ');'
    sql = 'SELECT * FROM vTweets WHERE text MATCH (' + placeholders
    c.execute(sql,tuple(phrases1))
    print(c.fetchall())
    c.close()
    conn.commit()
    conn.close()

def getPhrases():
    with open('phrases1.txt','r') as f:
        phrases1 = f.read().split(',')
    with open('phrases2.txt','r') as f:
        phrases2 = f.read().split(',')
    return phrases1[:-1], phrases2[:-1]

def formatPhrases(phrases):
    formatted = ''
    for phrase in phrases:
        formatted += (phrase + ' OR ')
    return formatted[:-4]

conTweets()
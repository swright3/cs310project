from dbcontrol import *

def getDB1Tweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    return c.fetchall()

def conTweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    tweets = c.fetchall()
    conn.close()
    conn = sqlite3.connect('ukpoliticstweets2.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    tweets + c.fetchall()
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS vTweets using fts5(newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party, tokenize="porter unicode61");')
    c.executemany('INSERT INTO vTweets (newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);',tweets)
    phrases1, phrases2 = getPhrases()
    phrases1 = formatPhrases(phrases1)
    sql = 'SELECT * FROM vTweets WHERE text MATCH ?;'
    c.execute(sql,(phrases1,))
    relevant = c.fetchall()
    c.execute('DELETE FROM vTweets')
    c.executemany('INSERT INTO vTweets (newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);',relevant)
    c.execute('SELECT * FROM vTweets')
    print(c.fetchall())
    #c.execute('DELETE * FROM vTweets;')
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
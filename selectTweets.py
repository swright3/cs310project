from dbcontrol import *

def getDB1Tweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    return c.fetchall()

def sortTweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    tweets = c.fetchall()
    conn.close()
    conn = sqlite3.connect('ukpoliticstweets2.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets;')
    tweets += c.fetchall()
    for tweet in tweets:
        tweet = list(tweet)
        tweet[5] = tweet[5].replace('?','').replace("'","").replace(',','')
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS vTweets using fts5(newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party, tokenize="porter unicode61");')
    c.execute('CREATE VIRTUAL TABLE IF NOT EXISTS vTweets2 using fts5(newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party, tokenize="porter unicode61");')
    c.executemany('INSERT INTO vTweets (newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);',tweets)
    local = placeSearch(c,conn)
    c.execute('DELETE FROM vTweets;')
    c.executemany('INSERT INTO vTweets (newId,id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);',local)
    partySearch('con',c,conn)
    partySearch('lab',c,conn)
    partySearch('libdem',c,conn)
    partySearch('green',c,conn)
    conn.commit()
    conn.close()

def placeSearch(c,conn):
    with open('formattedPlaces.txt','r') as f:
        places = f.read()
    c.execute('SELECT * FROM vTweets WHERE location MATCH ?;',(places,))
    return c.fetchall()

def partySearch(party,c,conn):
    phrases = formatPhrases(getPhrases(party))
    c.execute('SELECT * FROM vTweets WHERE text MATCH ?;',(phrases,))
    relevant = c.fetchall()
    conn2 = sqlite3.connect('sortedTweets.db')
    c2 = conn2.cursor()
    c2.execute('SELECT id FROM ' + party + 'Tweets;')
    existing = c2.fetchall()
    for tweet in relevant:
        if tweet[1] not in existing:
            tweet[-1] = '0'
            c2.execute('INSERT INTO ' + party + 'Tweets (id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId) VALUES (?,?,?,?,?,?,?,?,?,?,?);',tweet[1:])
    conn2.commit()
    conn2.close()

def getPhrases(party):
    with open(party + 'Phrases.txt','r') as f:
        phrases1 = f.read().split(',')
    return phrases1[:-1]

def formatPhrases(phrases):
    formatted = ''
    for phrase in phrases:
        formatted += (phrase + ' OR ')
    return formatted[:-4]

if __name__ == '__main__':
    sortTweets()
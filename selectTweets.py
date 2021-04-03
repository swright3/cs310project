from dbcontrol import *

#Selects all of the tweet ids from the sorted tweet database
def getOldIds():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    oldIds = set()
    c.execute('SELECT id FROM conTweets')
    ids = c.fetchall()
    for id in ids:
        oldIds.add(id[0])
    c.execute('SELECT id FROM labTweets')
    ids = c.fetchall()
    for id in ids:
        oldIds.add(id[0])
    c.execute('SELECT id FROM libdemTweets')
    ids = c.fetchall()
    for id in ids:
        oldIds.add(id[0])
    c.execute('SELECT id FROM greenTweets')
    ids = c.fetchall()
    for id in ids:
        oldIds.add(id[0])
    conn.close()
    return list(oldIds)

#Selects all of the tweets that haven't been sorted and loads them into a virtual table in memory so the full text search is faster
def sortTweets():
    maxId = getLargestExistingId()
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets WHERE id > ?;',(maxId,))
    tweets = c.fetchall()
    conn.close()
    conn = sqlite3.connect('ukpoliticstweets2.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tweets WHERE id > ?;',(maxId,))
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
    print('con')
    partySearch('lab',c,conn)
    print('lab')
    partySearch('libdem',c,conn)
    print('libdem')
    partySearch('green',c,conn)
    print('green')
    conn.commit()
    conn.close()

#Discards all of the tweets from user that are known to be outside of the UK
def placeSearch(c,conn):
    with open('formattedPlaces.txt','r') as f:
        places = f.read()
    c.execute('SELECT * FROM vTweets WHERE location MATCH ?;',(places,))
    return c.fetchall()

#Given a party, this function performs a full text search on all of the new tweets with the party's associated phrases
#Inserts only the tweets relevant to the specified party into its table in sortedTweets.db
def partySearch(party,c,conn):
    phrases = formatPhrases(getPhrases(party))
    c.execute('SELECT * FROM vTweets WHERE text MATCH ?;',(phrases,))
    relevant = c.fetchall()
    conn2 = sqlite3.connect('sortedTweets.db')
    c2 = conn2.cursor()
    # c2.execute('SELECT id FROM ' + party + 'Tweets;')
    # existing = c2.fetchall()
    print(party + ' tweet examples:')
    print(relevant[:5])
    for tweet in relevant:
        tweet = list(tweet)
        tweet[-1] = '0'
        c2.execute('INSERT INTO ' + party + 'Tweets (id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,sentiment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);',tweet[1:])
    conn2.commit()
    conn2.close()

#Gets the specified party's associated phrases from a text file
def getPhrases(party):
    with open(party + 'Phrases.txt','r') as f:
        phrases1 = f.read().split(',')
    return phrases1[:-1]

#Formats the phrases for a full text search
def formatPhrases(phrases):
    formatted = ''
    for phrase in phrases:
        formatted += (phrase + ' OR ')
    return formatted[:-4]

if __name__ == '__main__':
    sortTweets()
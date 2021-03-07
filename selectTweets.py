from dbcontrol import *
from twitterAuth import mpPhrases

conPhrases = ["tories","conservative","conservatives","tory","toriesout","conservativeparty","fuckthetories","backboris",
            "toryparty","torygovernment","torymps","votetory","torygovt","theresamay","torybrexit","toryvoters"]
labPhrases = ["labour","labourparty","votelabour","labourgovernment","labourmembers","starmerout","uklabour","starmer","corbyn","jeremycorbyn"]
libdemPhrases = ["libdems","libdem","libdemparty","liberaldemocrat","liberaldemocrats","votelibdem","ldconf"]
greenPhrases = ["green","greenparty","greens","greenpartyuk","greensuk","jonathanbartley","sianberry","siânberry"]

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

conTweets()
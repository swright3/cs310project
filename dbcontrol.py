import sqlite3
from selectTweets import getLargestExistingId

def clearTweets():
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS tweets")
    
    c.execute('''CREATE TABLE tweets (
        newId INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        user TEXT,
        text TEXT,
        hashtags TEXT,
        location TEXT,
        coordinates TEXT,
        date TEXT,
        followers INTEGER,
        retweets INTEGER,
        favourites INTEGER,
        replyToId INTEGER,
        party TEXT
    )'''
    )
    conn.commit()
    conn.close()

def sortedTweets():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS conTweets")
    c.execute("DROP TABLE IF EXISTS labTweets")
    c.execute("DROP TABLE IF EXISTS libdemTweets")
    c.execute("DROP TABLE IF EXISTS greenTweets")
    c.execute('''CREATE TABLE conTweets (
        conId INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        user TEXT,
        text TEXT,
        hashtags TEXT,
        location TEXT,
        coordinates TEXT,
        date TEXT,
        followers INTEGER,
        retweets INTEGER,
        favourites INTEGER,
        replyToId INTEGER,
        sentiment TEXT
    )'''
    )
    c.execute('''CREATE TABLE labTweets (
        labId INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        user TEXT,
        text TEXT,
        hashtags TEXT,
        location TEXT,
        coordinates TEXT,
        date TEXT,
        followers INTEGER,
        retweets INTEGER,
        favourites INTEGER,
        replyToId INTEGER,
        sentiment TEXT
    )'''
    )
    c.execute('''CREATE TABLE libdemTweets (
        libdemId INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        user TEXT,
        text TEXT,
        hashtags TEXT,
        location TEXT,
        coordinates TEXT,
        date TEXT,
        followers INTEGER,
        retweets INTEGER,
        favourites INTEGER,
        replyToId INTEGER,
        sentiment TEXT
    )'''
    )
    c.execute('''CREATE TABLE greenTweets (
        greenId INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER,
        user TEXT,
        text TEXT,
        hashtags TEXT,
        location TEXT,
        coordinates TEXT,
        date TEXT,
        followers INTEGER,
        retweets INTEGER,
        favourites INTEGER,
        replyToId INTEGER,
        sentiment TEXT
    )'''
    )
    conn.commit()
    conn.close()

def setSentimentTo0():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('UPDATE conTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE labTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE libdemTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE greenTweets SET sentiment = ?;',('0',))
    conn.commit()
    conn.close()

def formatDate():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    for party in ['con','lab','libdem','green']:
        print(party)
        c.execute('SELECT '+party+'Id,date FROM '+party+'Tweets;')
        tweets = c.fetchall()
        for tweet in range(len(tweets)):
            tweets[tweet] = list(tweets[tweet])
            tweets[tweet][1] = tweets[tweet][1][:4] + '-' + tweets[tweet][1][5:7] + '-' + tweets[tweet][1][8:10]
            sql = 'UPDATE '+party+'Tweets SET date = ? WHERE '+party+'Id = ?'
            c.execute(sql,(tweets[tweet][1],tweets[tweet][0]))
        conn.commit()
    conn.close()

def insertTweet(values):
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute("INSERT INTO tweets (id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);",values)
    c.close()
    conn.commit()
    conn.close()

""" def select(columns,criteria):
    sql = "SELECT "
    for column in columns:
        sql = sql + "?, "
    sql = sql[:-2] + " FROM tweets WHERE "
    for query in range(0,len(criteria),2):
        sql = sql + "? = ? AND "
    sql = sql[:-5] + ";"
    values = columns + criteria
    print(sql,values)
    #c.execute(sql,values)
    #c.execute("SELECT id, text FROM tweets WHERE followers = 2000 AND retweets = 1999")
    c.execute("SELECT ?, ? FROM tweets WHERE ? = ?",("id","text","user","sam"))
    return c.fetchall() """

def delete(table,criteria):
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute('DELETE FROM ? WHERE ?;',(table,criteria))
    conn.commit()
    conn.close()

def deleteOldTweets(file):
    stopAtId = getLargestExistingId()
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('DELETE FROM tweets WHERE id < ?;',(stopAtId,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    deleteOldTweets('ukpoliticstweets.db')
    deleteOldTweets('ukpoliticstweets2.db')
    #formatDate()
#setSentimentTo0()
#sortedTweets()
#clearTweets()
#tweet = (101,"sam","despite all the negative press covfefe","#gymladboris","right here","right now",2000,1999,1998,0)

##insertTweet(tweet)
#print(select(("id","text"),("followers = 2000","retweets = 1999"))
#print(select(("id","text"),("followers",2000,"retweets",1999)))


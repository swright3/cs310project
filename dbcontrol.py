import sqlite3

#Clears and creates the main table for newly collected tweets
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

#Clears and creates each of the party specific tables that tweets are sorted into
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

#Originally didn't set the default sentiment for tweets so this sets all sentiments to '0'
def setSentimentTo0():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('UPDATE conTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE labTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE libdemTweets SET sentiment = ?;',('0',))
    c.execute('UPDATE greenTweets SET sentiment = ?;',('0',))
    conn.commit()
    conn.close()

#Formats the date of each tweet in each party's table to YYYY-MM-DD
def formatTweetDate():
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

#There were some poll dates that start with a space, this removes the space
def formatPollDate():
    conn = sqlite3.connect('sortedTweets.db')            
    c = conn.cursor()
    c.execute('SELECT id,date FROM polls WHERE date LIKE ?;',(' %',))
    polls = c.fetchall()
    for poll in polls:
        c.execute('UPDATE polls SET date = ? WHERE id = ?;',(poll[1][1:],poll[0]))
    conn.commit()
    conn.close()

#Inserts newly collected tweets into the unsorted database
def insertTweet(values):
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute("INSERT INTO tweets (id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId,party) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);",values)
    c.close()
    conn.commit()
    conn.close()

#Deletes unneeded old tweets from the unsorted database to reduce file size, you still need to vacuum the db afterwards
def deleteOldTweets(file):
    stopAtId = getLargestExistingId()
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c.execute('DELETE FROM tweets WHERE id < ?;',(stopAtId,))
    conn.commit()
    c.execute('VACUUM;')
    conn.close()

#Gets the ID of the newest tweet sorted into sortedTweets.db, used to determine where to stop deleting
def getLargestExistingId():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    maxIds = []
    c.execute('SELECT MAX(id) FROM conTweets;')
    maxIds.append(c.fetchone()[0])
    c.execute('SELECT MAX(id) FROM labTweets;')
    maxIds.append(c.fetchone()[0])
    c.execute('SELECT MAX(id) FROM libdemTweets;')
    maxIds.append(c.fetchone()[0])
    c.execute('SELECT MAX(id) FROM greenTweets;')
    maxIds.append(c.fetchone()[0])
    conn.close()
    return max(maxIds)

if __name__ == '__main__':
    print()
    #formatPollDate()
    #deleteOldTweets('ukpoliticstweets.db')
    #deleteOldTweets('ukpoliticstweets2.db')
    #formatDate()
#setSentimentTo0()
#sortedTweets()
#clearTweets()
#tweet = (101,"sam","despite all the negative press covfefe","#gymladboris","right here","right now",2000,1999,1998,0)

##insertTweet(tweet)
#print(select(("id","text"),("followers = 2000","retweets = 1999"))
#print(select(("id","text"),("followers",2000,"retweets",1999)))


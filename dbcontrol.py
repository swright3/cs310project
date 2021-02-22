import sqlite3




# c.execute("DROP TABLE IF EXISTS tweets")

# c.execute('''CREATE TABLE tweets (
#     id INTEGER PRIMARY KEY,
#     user TEXT,
#     text TEXT,
#     hashtags TEXT,
#     location TEXT,
#     coordinates TEXT,
#     date TEXT,
#     followers INTEGER,
#     retweets INTEGER,
#     favourites INTEGER,
#     replyToId INTEGER
# )'''
# )

def insertTweet(values):
    conn = sqlite3.connect('ukpoliticstweets.db')
    c = conn.cursor()
    c.execute("INSERT INTO tweets (id,user,text,hashtags,location,coordinates,date,followers,retweets,favourites,replyToId) VALUES (?,?,?,?,?,?,?,?,?,?,?);",values)
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

tweet = (101,"sam","despite all the negative press covfefe","#gymladboris","right here","right now",2000,1999,1998,0)

##insertTweet(tweet)
#print(select(("id","text"),("followers = 2000","retweets = 1999"))
#print(select(("id","text"),("followers",2000,"retweets",1999)))


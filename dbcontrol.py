import sqlite3

conn = sqlite3.connect('ukpoliticstweets.db')

c = conn.cursor()


# c.execute('''CREATE TABLE tweets (
#     id INTEGER PRIMARY KEY,
#     user TEXT,
#     text TEXT,
#     hashtags TEXT,
#     location TEXT,
#     date TEXT,
#     followers INTEGER,
#     retweets INTEGER,
#     favourites INTEGER
# )'''
# )


def insertTweet(values):
    c.execute("INSERT INTO tweets (id,user,text,hashtags,location,date,followers,retweets,favourites) VALUES (?,?,?,?,?,?,?,?,?);",values)
    conn.commit()

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
    c.execute('DELETE FROM ? WHERE ?;',(table,criteria))

tweet = (101,"sam","despite all the negative press covfefe","#gymladboris","right here","right now",2000,1999,1998)

##insertTweet(tweet)
#print(select(("id","text"),("followers = 2000","retweets = 1999"))
#print(select(("id","text"),("followers",2000,"retweets",1999)))

conn.close()
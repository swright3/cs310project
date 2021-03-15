import sqlite3
from pollparser2 import makePollTable

def transferPolls():
    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    c.execute('SELECT pollster,date,con,lab,libdem,green FROM polls')
    polls = c.fetchall()
    conn.close()
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.executemany('INSERT INTO polls (pollster,date,con,lab,libdem,green) VALUES (?,?,?,?,?,?);',polls)
    conn.commit()
    conn.close()

def createRelationalTables():
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE conPollTweets (
        pollId INTEGER NOT NULL,
        partyId INTEGER NOT NULL,
        FOREIGN KEY (pollId) REFERENCES polls(id),
        FOREIGN KEY (partyId) REFERENCES conTweets(conId),
        PRIMARY KEY (pollId,partyId)
    )''')
    c.execute('''CREATE TABLE labPollTweets (
        pollId INTEGER NOT NULL,
        partyId INTEGER NOT NULL,
        FOREIGN KEY (pollId) REFERENCES polls(id),
        FOREIGN KEY (partyId) REFERENCES labTweets(labId),
        PRIMARY KEY (pollId,partyId)
    )''')
    c.execute('''CREATE TABLE libdemPollTweets (
        pollId INTEGER NOT NULL,
        partyId INTEGER NOT NULL,
        FOREIGN KEY (pollId) REFERENCES polls(id),
        FOREIGN KEY (partyId) REFERENCES libdemTweets(id),
        PRIMARY KEY (pollId,partyId)
    )''')
    c.execute('''CREATE TABLE greenPollTweets (
        pollId INTEGER NOT NULL,
        partyId INTEGER NOT NULL,
        FOREIGN KEY (pollId) REFERENCES polls(id),
        FOREIGN KEY (partyId) REFERENCES greenTweets(id),
        PRIMARY KEY (pollId,partyId)
    )''')
    conn.commit()
    conn.close()

#earliest tweet = 2021-03-01
#earliest usable poll = 2021-3-4 id = 2176

def fillRelationalTable(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    date = '2021-3-4'
    c.execute("SELECT id,date FROM polls WHERE id > ?;",(2176,))
    print(c.fetchall())
    conn.close()


if __name__ == '__main__':
    fillRelationalTable('con')
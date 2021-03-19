import sqlite3
from pollparser2 import makePollTable
from datetime import datetime, timedelta

#Creates the relational tables between the polls and each party's tweet table
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
#earliest usable poll = 2021-3-4 id = 2305

#Gets all new polls and relates tweets to them
def fillRelationalTable(party):
    conn = sqlite3.connect('sortedTweets.db')
    c = conn.cursor()
    c.execute('SELECT id,date FROM polls WHERE id > ?;',(2304,))
    allPolls = c.fetchall()
    c.execute('SELECT DISTINCT pollId FROM '+party+'PollTweets;')
    existingPolls = c.fetchall()
    for poll in range(len(existingPolls)):
        existingPolls[poll] = existingPolls[poll][0]
    polls = []
    for poll in allPolls:
        if poll not in existingPolls:
            polls.append(poll)
    for poll in polls:
        tweetIds = getPollRelevantTweets(poll[1],conn,c,party)
        for id in tweetIds:
            c.execute('INSERT INTO '+party+'PollTweets (pollId,partyId) VALUES (?,?)',(poll[0],id))
        conn.commit()
    conn.close()

#Selects only the ids of the tweets from up to 3 days before the specified poll
def getPollRelevantTweets(date,conn,c,party):
    dates = []
    date1 = datetime.strptime(date, '%Y-%m-%d')
    date2 = date1 - timedelta(days=1)
    date3 = date1 - timedelta(days=2)
    date4 = date1 - timedelta(days=3)
    dates.append(date1.strftime('%Y')+'-'+date1.strftime('%m')+'-'+date1.strftime('%d'))
    dates.append(date2.strftime('%Y')+'-'+date2.strftime('%m')+'-'+date2.strftime('%d'))
    dates.append(date3.strftime('%Y')+'-'+date3.strftime('%m')+'-'+date3.strftime('%d'))
    dates.append(date4.strftime('%Y')+'-'+date4.strftime('%m')+'-'+date4.strftime('%d'))
    c.execute('SELECT '+party+'Id FROM '+party+'Tweets WHERE date IN (?,?,?,?);',dates)
    tweets = c.fetchall()
    tweetIds = []
    for tweet in tweets:
        tweetIds.append(tweet[0])
    return tweetIds
    

if __name__ == '__main__':
    fillRelationalTable('con')
    fillRelationalTable('lab')
    fillRelationalTable('libdem')
    fillRelationalTable('green')
import tweepy
from dbcontrol import *
from mpparser import *
import pandas as pd
import time

# Variables that contains the credentials to access Twitter API
ACCESS_TOKEN = '3099117383-ybROCSwGlrqSNgNWYAGU1PlZ5FNFkzdyYDruplo'
ACCESS_SECRET = 'HPGbi7jHo8WSDMSz1EYL4dhFucmnz2roTqVWidfbNoM5E'
CONSUMER_KEY = 'GMTtHcXjvMNpFhs8BVHP0RcSs'
CONSUMER_SECRET = 'sO7DyfPs3cve3vzb1shhEM30vWewJEf3gADi7MAk6qpnktTUmz'


# Setup access to API
def connect_to_twitter_OAuth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    return api


# Create API object
api = connect_to_twitter_OAuth()

# meme_tweets = api.user_timeline('LinusTechTip_')
# for tweet in meme_tweets:
#     print(tweet.text)

class StreamListener(tweepy.StreamListener):
    #Inherit from tweepy streamlistener and override methods because they are stubs
    def on_status(self, status):
        #print(status.entities["text"])
        tweet = self.extractData(status)
        insertTweet(tweet)
        print("tweet inserted")
        
    def on_error(self, status_code):
        if status_code == 420:
            print("420 error")
            time.sleep(60)
            return True # continue listening
        logger.info('Error: status %s', str(status_code))
        return True # continue listening

    def on_timeout(self):
        logger.info('Timeout: pausing 60s')
        time.sleep(60)
        return True  # continue listening


    def extractData(self, status):
        data = []
        data.append(status.id)
        data.append(status.user.id)
        data.append(status.text)

        hashtags = ""
        for tag in status.entities["hashtags"]:
            hashtags = hashtags + tag["text"] + ","
        data.append(hashtags)
        
        data.append(str(status.user.location))
        data.append(str(status.coordinates))
        data.append(str(status.created_at))
        data.append(status.user.followers_count)
        data.append(status.retweet_count)
        data.append(status.favorite_count)
        data.append(status.in_reply_to_user_id)
        # party = ''
        # for phrase in conPhrases:
        #     if phrase in status.text.lower():
        #         party = party + 'con'
        # for phrase in labPhrases:
        #     if phrase in status.text.lower():
        #         party = party + 'lab'
        # for phrase in libdemPhrases:
        #     if phrase in status.text.lower():
        #         party = party + 'lib'
        # for phrase in greenPhrases:
        #     if phrase in status.text.lower():
        #         party = party + 'grn'
        data.append('')

        return data

conPhrases = ["tories","conservative","conservatives","tory","toriesout","conservativeparty","fuckthetories","backboris",
            "toryparty","torygovernment","torymps","votetory","torygovt","theresamay","torybrexit","toryvoters"]
labPhrases = ["labour","labourparty","votelabour","labourgovernment","labourmembers","starmerout","uklabour","starmer","corbyn","jeremycorbyn"]
libdemPhrases = ["libdems","libdem","libdemparty","liberaldemocrat","liberaldemocrats","votelibdem","ldconf"]
greenPhrases = ["green","greenparty","greens","greenpartyuk","greensuk","jonathanbartley","sianberry","siânberry"]

def mpPhrases(conPhrases,labPhrases,libdemPhrases,greenPhrases):
    mpnames = getMParray()
    for mp in mpnames:
        mp[0] = mp[0].replace(' ','').lower()
        if mp[1] == 'Conservative':
            conPhrases.append(mp[0])
        elif mp[1] == 'Labour':
            labPhrases.append(mp[0])
        elif mp[1] == 'Lib Dem':
            libdemPhrases.append(mp[0])
        elif mp[1] == 'Green':
            greenPhrases.append(mp[0])

def mpPhrases2(conPhrases,labPhrases,libdemPhrases,greenPhrases):
    data = pd.read_csv('mptwitter.csv')
    for row in data.index:
        if data['Party'][row] == 'Conservative':
            conPhrases.append(data['Screen name'][row].replace('@',''))
        elif data['Party'][row] == 'Labour':
            labPhrases.append(data['Screen name'][row].replace('@',''))
        elif data['Party'][row] == 'Liberal Democrat':
            libdemPhrases.append(data['Screen name'][row].replace('@',''))
        elif data['Party'][row] == 'Green Party':
            greenPhrases.append(data['Screen name'][row].replace('@',''))

def mpPhrasesToText(phrases1,phrases2):
    with open('phrases1.txt','w') as f:
        for phrase in phrases1:
            f.write(phrase + ',')
    with open('phrases2.txt','w') as f:
        for phrase in phrases2:
            f.write(phrase + ',')

mpPhrases2(conPhrases,labPhrases,libdemPhrases,greenPhrases)
# mpPhrases(conPhrases,labPhrases,libdemPhrases,greenPhrases)
allPhrases = conPhrases + labPhrases + libdemPhrases + greenPhrases
phrases1 = allPhrases[:len(allPhrases)//2]
phrases2 = allPhrases[len(allPhrases)//2:]
#mpPhrasesToText(phrases1,phrases2)

sl = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=sl)
while True:
    try:
        stream.filter(track=phrases1,languages=["en"])
    except:
        print("error occurred")
        time.sleep(60)
        continue
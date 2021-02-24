import tweepy
from dbcontrol import *

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
        
    def on_error(self, status_code):
        if status_code == 420:
            return False

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


        return data

conPhrases = ["tories","borisjohnson","conservative","conservatives","tory","toriesout","conservativeparty","fuckthetories","backboris",
            "toryparty","torygovernment","torymps","votetory","torygovt","theresamay","torybrexit","toryvoters"]
labPhrases = ["labour","labourparty","votelabour","labourgovernment","labourmembers","starmerout","keirstarmer","uklabour",
            "jeremycorbyn","starmer","corbyn"]
libdemPhrases = ["libdems","libdem","libdemparty","liberaldemocrat","liberaldemocrats","votelibdem"]
greenPhrases = ["green","greenparty","greens","greenpartyuk","greensuk"]
sl = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=sl)
stream.filter(track=["libdem,libdemfightback,tory,toryparty,labour,labourparty"],languages=["en"])


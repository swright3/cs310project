import tweepy

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
        hashtags = ""
        for tag in status.entities["hashtags"]:
            hashtags = hashtags + tag["text"] + ","
        print(hashtags)
        #print(status.entities["text"])
        
    def on_error(self, status_code):
        if status_code == 420:
            return False

sl = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=sl)
stream.filter(track=["libdem,libdemfightback,tory,toryparty,labour,labourparty"],languages=["en"])


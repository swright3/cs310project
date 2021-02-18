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

trump_tweets = api.user_timeline('LinusTechTip_')
for tweet in trump_tweets:
    print(tweet.text)
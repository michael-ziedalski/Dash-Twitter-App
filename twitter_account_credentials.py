import tweepy as tw
from tweepy import OAuthHandler

consumer_key = 'RAEuMb5S6e7kmqPrcpRsCsSnG'
consumer_secret = '8asAKTBrJpnby6j1OBFAqtq5gCjWXoOlZaedjJfknFs77RUnNb'
access_token = '799329604418813952-wwdWYqIPLLwaFsED3KB3uBqRKUcZlm3'
access_secret = 'SOTaYTVhRo4ZqrL00izsD2vji0NB66UUzMYjAinmd6uOV'
   
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

 
api = tw.API(auth)
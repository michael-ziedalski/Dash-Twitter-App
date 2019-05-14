import pandas as pd
import numpy as np
import tweepy as tw
from twitter_account_credentials import api

import sys
import csv
import time
import datetime
import collections
import itertools


## Getting id's from twitter screen_names
def id_extractor(screenname):
        
    ids = {}
    
    ## Checking if one string, string of multiple names, or array fed in
    if isinstance(screenname, str):
        
        if ',' in screenname:
            screenname = screenname.replace(" ","").split(',')
            for names in screenname:
                ids[names] = str(api.get_user(screen_name=names).id)
                
        else:
            ids[screenname] = str(api.get_user(screen_name=screenname).id)
        
    elif isinstance(screenname, list) or isinstance(screenname, np.ndarray):
        for names in screenname:
            ids[names] = str(api.get_user(screen_name=names).id)
            
    return ids


## Getting old tweets
def old_tweets(screenname, tweet_count = 10):

    print(type(screenname), screenname)

    ids = id_extractor(screenname)
    
    archive = pd.DataFrame([])
    
    for name in ids:
    
        # Calling the user_timeline function with our parameters
        tweets = api.user_timeline(user_id=ids[name], count=tweet_count)

        ## First row has date format being changed to more readable version
        info = np.array([[tweet.created_at.strftime('%Y-%m-%d %H:%M'), 
                          tweet.author.screen_name,
                          len(tweet.text),
                          tweet.favorite_count,
                          tweet.retweet_count,
                          tweet.text] 
                          for tweet in tweets])

        archive = pd.concat(objs=[archive, 
                                  pd.DataFrame(info, columns=['Date', 'Author', 'Len', 'Favs', 'Retw', 'Text'])])
        
    archive.sort_values(by='Date')
    archive.reset_index(drop=True, inplace=True)    
    
    
    return archive
    

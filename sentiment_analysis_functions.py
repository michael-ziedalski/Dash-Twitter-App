import numpy as np
import re
from textblob import TextBlob


## Organizing tweet by id
def tweet_id_categorizing(tweets, only_keywords_search):

    # if not tweets:
    #     print('\nNo tweets to analyze.')
    #     return

    categorized_tweets = {}

    ## If tweets should be differentiated by user
    if only_keywords_search == 0:

        for tweet in tweets:
            if tweet['Author'] in categorized_tweets:
                categorized_tweets[tweet['Author']].append(tweet['Text'])
            else:
                categorized_tweets[tweet['Author']] = [tweet['Text']]

    ## If tweets should be not differentiated by user, such as searching only by keyword
    elif only_keywords_search == 1:

        categorized_tweets['all tweets'] = [i['Text'] for i in tweets]
    
    # Turning tweet collection for each author into np.array for efficient cleaning in next f.        
    print('\n\ntweet_id_categorizing:\n{}\n'.format(categorized_tweets))
    return categorized_tweets
    


## Next is automatic cleaning of each tweet for textblob's use
def tweet_cleaning(categorized_tweets):

    # if not categorized_tweets:
    #     print('\nNo tweets to analyze.')
    #     return
    
    for authors_tweets in categorized_tweets.keys():
        for tweet in categorized_tweets[authors_tweets]:
            tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", 
                                    tweet).split())

        
    print('\n\ntweet_cleaning:\n{}\n'.format(categorized_tweets))
    
    return categorized_tweets



## Sentiment analysis on previous functions' output using textblob
def tweet_sentiment(tweets, only_keywords_search = 0):
    
    categorized_tweets = tweet_id_categorizing(tweets, only_keywords_search)
    categorized_cleaned_tweets = tweet_cleaning(categorized_tweets)

    if isinstance(categorized_cleaned_tweets, dict):
        for authors_tweets in categorized_cleaned_tweets.keys():
            for i, tweet in enumerate(categorized_cleaned_tweets[authors_tweets]):
                categorized_cleaned_tweets[authors_tweets][i] = TextBlob(tweet).sentiment.polarity
    
    
    print('\n\ntweet_sentiment:\n{}\n'.format(categorized_cleaned_tweets))
    return categorized_cleaned_tweets

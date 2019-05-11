import numpy as np
import re
from textblob import TextBlob


## Organizing tweet by id
def tweet_id_categorizing(tweets):
    categorized_tweets = {}
    
    for tweet in tweets:
        if tweet['Author'] in categorized_tweets:
            categorized_tweets[tweet['Author']].append(tweet['Text'])
        else:
            categorized_tweets[tweet['Author']] = [tweet['Text']]
    
    # Turning tweet collection for each author into np.array for efficient cleaning in next f.
#     for authors_tweets in categorized_tweets:
#         authors_tweets = np.array(authors_tweets)
        
    print('\n\ntweet_id_categorizing:\n{}\n'.format(categorized_tweets))
    return categorized_tweets
    


## Next is automatic cleaning of each tweet for textblob's use
def tweet_cleaning(categorized_tweets): 
#     cleaned_tweets = np.array([])
    
    for authors_tweets in categorized_tweets.keys():
        for tweet in categorized_tweets[authors_tweets]:
            tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", 
                                    tweet).split())

        
    print('\n\ntweet_cleaning:\n{}\n'.format(categorized_tweets))
    
    return categorized_tweets


## Sentiment analysis on previous functions' output using textblob
def tweet_sentiment(tweets):
#     tweet_sentiments = []
    
    categorized_tweets = tweet_id_categorizing(tweets)
    categorized_cleaned_tweets = tweet_cleaning(categorized_tweets)

    if isinstance(categorized_cleaned_tweets, dict):
        for authors_tweets in categorized_cleaned_tweets.keys():
            for i, tweet in enumerate(categorized_cleaned_tweets[authors_tweets]):
                categorized_cleaned_tweets[authors_tweets][i] = TextBlob(tweet).sentiment.polarity
    
    
    print('\n\ntweet_sentiment:\n{}\n'.format(categorized_cleaned_tweets))
    return categorized_cleaned_tweets
            
    
    
    
    
    
#     if isinstance(cleaned_tweets, str):
#         return TextBlob(cleaned_tweets).sentiment.polarity
    
#     if isinstance(cleaned_tweets, list) or isinstance(cleaned_tweets, np.ndarray):
#         tweets_categorized_by_id = []
        
#         for tweet in cleaned_tweets:
# #             print(tweet)
#             tweets.append(TextBlob(tweet).sentiment.polarity)
            
#         return tweets
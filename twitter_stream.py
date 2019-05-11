import tweepy as tw
import os
import sys
import time
import csv
import datetime

from twitter_account_credentials import api
from twitter_functions import id_extractor

## Setting path to active directoy just in case
os.chdir(sys.path[0])

import argparse


## Argparse used, to run script effectively
##################
##################

parser = argparse.ArgumentParser(description="")

parser.add_argument('follow', help='Accounts to follow')
parser.add_argument('time_limit', help='How long to keep stream open', type=int)
parser.add_argument('-file_name', help='Name of resulting csv file', default=None)
parser.add_argument('-sub_name', help='Sub-name of resulting csv file', default='stream')
parser.add_argument('-filter_track', help='Filter track', default=None)
parser.add_argument('-locations', help='Locations', default=None)
parser.add_argument('-languages', help='Languages', default=None)

args = parser.parse_args()

##################
##################


def twitter_stream_listener(file_name=args.file_name,
                            time_limit=int(60*args.time_limit), #Converting to min
                            sub_name=args.sub_name,
                            filter_track=args.filter_track,
                            follow=args.follow,
                            locations=args.locations,
                            languages=args.languages,
                            auth = api.auth):
    
    
    ## Automatic filename generation if file_name missing, based on sub_name prefix and current date
#     if file_name == None:
#         file_name = sub_name+datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")+'.csv'
    if file_name == None:
        file_name = sub_name+'.csv'

    ## Slight optimization for my conditionals below
    if follow:  
        ids = id_extractor(follow)
        follow_num = set([int(i) for i in ids.values()])
        follow_str = set([str(i) for i in ids.values()])


    class CustomStreamListener(tw.StreamListener):
        def __init__(self, time_limit):
            self.start_time = time.time()
            self.limit = time_limit
            # self.saveFile = open('abcd.json', 'a')
            super(CustomStreamListener, self).__init__()

        def on_status(self, status):

            ## Checking if tweet in stream is from chosen user(s), since twitter's 
            ## real-time api doesn't allow such precision yet
            if status.author.id in follow_num:
                    
                if (time.time() - self.start_time) < self.limit:
                    print(".", end="")
                
                    # Writing status data
                    with open(file_name, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            status.created_at, status.author.screen_name,
                            len(status.text), status.favorite_count, 					      status.retweet_count, status.text 
                        ])
                
                
                else:
                        print("\n\n[INFO] Closing file and ending streaming")
                        return False

                
        def on_error(self, status_code):
            if status_code == 420:
                print('Encountered error code 420. Disconnecting the stream')
                ## Returning False in on_data disconnects the stream
                return False
            else:
                print('Encountered error with status code: {}'.format(
                    status_code))
                return True

        def on_timeout(self):
            print('Timeout...')
            return True

    ## Writing csv titles
    print(
        '\n[INFO] Open file: [{}] and starting {} seconds of streaming for [{}]\n'
        .format(file_name, time_limit, follow))
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow([ 'Date', 'Author', 'Length', 'Favorites', 'Retweets',  'Text'])

    streamingAPI = tw.streaming.Stream(
        auth, CustomStreamListener(time_limit=time_limit))
    streamingAPI.filter(
        track=filter_track,
        follow=follow_str,
        locations=locations,
        languages=languages,
    )
    f.close()
    
    
    
## Running stream
twitter_stream_listener()
# By Anthony Layton (Tony Layton)
# 2018-12-10
#
from DB_connect_common import *
import json
from pprint import pprint
import re
import os  # https://docs.python.org/3/library/os.html
import io
import csv  # https://docs.python.org/3.4/library/csv.html
from zipfile import ZipFile  #https://docs.python.org/3.4/library/zipfile.html
import random
from string import punctuation
from pprint import pprint
import sqlite3
from collections import defaultdict, Counter
from collections import namedtuple, defaultdict
from itertools import zip_longest
import sqlite3
import time
from datetime import datetime
import datetime
import calendar
import tweepy
from collections import Counter
import nltk
import random
from string import punctuation
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from pprint import pprint


auth = {"consumer_key": "",
        "consumer_secret": "",
        "access_key": "",
        "access_secret": "",
        }

consumer_key = auth["consumer_key"]
consumer_secret = auth["consumer_secret"]
access_token = auth["access_key"]
access_token_secret = auth["access_secret"]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def cat_griz_tweet_pull():
    # Purpose:
    #   Pull Tweets for the UM vs. MSU game
    # Variables:
    #
    # Uses the following functions to run:
    #   init_tweet_db() = builds the database table 'tweets'
    #   get_populated_db_user_ids() = Pulls the user ids of previously populated users
    #   get_populated_db_tweet_ids() = Pulls the tweet ids of previously populated tweets
    #   grouper() = groups tweets in preparation for pulling and not hitting the rate limit.
    #   populate_tweet_db()
    #   get_unpopulated_db_user_ids()
    # Is used by the following functions to run:
    #   -none-
    rate_limit_status = api.rate_limit_status()
    c_c_search = rate_limit_status['resources']['search']['/search/tweets']['remaining']
    c_c_lookup = rate_limit_status['resources']['users']['/users/lookup']['remaining']

    master_db_name = 'CatGrizTweets.db'
    db = sqlite3.connect(master_db_name)
    cur = db.cursor()

    total_users_processed = 0
    failures = 0
    total_tweets_processed = 0
    populated_users = get_populated_db_user_ids(cur)
    populated_tweets = get_populated_db_tweet_ids(cur)
    recent_tweet_time = str(datetime.date.today() - datetime.timedelta(days=7))
    try:
        init_tweet_db(cur)
    except:
        pass
    search_term = ['griz', 'bobcats', 'gogriz', 'gobobcats', 'University of Montana', 'Montana State University']
    for i in search_term:
        c_c_search -= 1
        if c_c_search <= 1:
            rate_limit_status = api.rate_limit_status()
            r_search = rate_limit_status['resources']['search']['/search/tweets']['reset'] - time.time()
            print("Rate Limit Reached:  'api.search'\t\tSleeping for {} Seconds".format(r_search))
            time.sleep(r_search)
            c_c_search = 180
        else:
            pass
        for page in tweepy.Cursor(api.search,
                                  q=i,
                                  count=100,
                                  since_id=recent_tweet_time,
                                  until='').pages():
            c_c_search -= 1
            if c_c_search <= 1:
                rate_limit_status = api.rate_limit_status()
                r_search = rate_limit_status['resources']['search']['/search/tweets']['reset'] - time.time()
                print("Rate Limit Reached:  'api.search'\t\tSleeping for {} Seconds".format(r_search))
                time.sleep(r_search)
                c_c_search = 180
            else:
                pass
            chunks = grouper(100, page)
            for chunk in chunks:
                tweeter = []
                # Grouper pads with None by default, so drop those.
                chunk = [a for a in chunk if a is not None]
                for tweet in chunk:
                    if tweet.id in populated_tweets:
                        pass
                    else:  # Add to Tweet DB
                        populate_tweet_db(db, [tweet.created_at,tweet.id,
                                               tweet.user.id,tweet.user.name,
                                               tweet.user.screen_name,
                                               tweet.user.description,
                                               tweet.user.location,i,
                                               tweet.text])
                        populated_tweets.update({(tweet.id)})
                        total_tweets_processed += 1
                    if tweet.user.id in tweeter:
                        pass
                    else:
                        tweeter.append(tweet.user.id)
                try:
                    init_users_db(cur)
                except:
                    pass
                try:
                    c_c_lookup -= 1
                    if c_c_lookup <= 1:
                        rate_limit_status = api.rate_limit_status()
                        r_lookup = rate_limit_status['resources']['users']['/users/lookup']['reset'] - time.time()
                        print("Rate Limit Reached:  'api.lookup_users'\t\tSleeping for {} Seconds".format(r_lookup))
                        time.sleep(r_lookup)
                        c_c_lookup = 900
                    else:
                        pass
                    users_data = api.lookup_users(user_ids=tweeter)
                    total_users_processed += len(tweeter)
                    for this_user_data in users_data:
                        if this_user_data.id in populated_users:
                            pass
                        else:
                            save_user(db=db, user=this_user_data,
                                      master_db_name=master_db_name,
                                      parent_user_screen_name=i)
                            populated_users.update({(this_user_data.id)})
                except:
                    # if we end up here, we should step through the
                    # users one at a time.
                    for id in tweeter:
                        good_pull = False
                        c_c_lookup -= 1
                        if c_c_lookup <= 1:
                            rate_limit_status = api.rate_limit_status()
                            r_lookup = rate_limit_status['resources']['users']['/users/lookup']['reset'] - time.time()
                            print("Rate Limit Reached:  'api.lookup_users'\t\tSleeping for {} Seconds".format(r_lookup))
                            time.sleep(r_lookup)
                            c_c_lookup = 900
                        else:
                            pass
                        try:
                            this_user_data = api.lookup_users(user_ids=id)
                            total_users_processed += 1
                            good_pull = True
                        except:
                            failures += 1
                        if good_pull:
                            if this_user_data.id in populated_users:
                                pass
                            else:
                                save_user(db=db, user=this_user_data,
                                          master_db_name=master_db_name,
                                          parent_user_screen_name=i)
                                populated_users.update({(this_user_data.id)})
        needs_pop = get_unpopulated_db_user_ids(cur)
        if needs_pop == set():
            pass
        else:
            c_c_lookup -= 1
            if c_c_lookup <= 1:
                rate_limit_status = api.rate_limit_status()
                r_lookup = rate_limit_status['resources']['users']['/users/lookup']['reset'] - time.time()
                print("Rate Limit Reached:  'api.lookup_users'\t\tSleeping for {} Seconds".format(r_lookup))
                time.sleep(r_lookup)
                c_c_lookup = 900
            else:
                pass
            needs_users_data = api.lookup_users(user_ids=needs_pop)
            total_users_processed += len(needs_users_data)
            for like_this_user_data in needs_users_data:
                if like_this_user_data.id in populated_users:
                    pass
                else:
                    save_user(db=db, user=like_this_user_data,
                              master_db_name=master_db_name,
                              parent_user_screen_name=i)
                    populated_users.update({(like_this_user_data.id)})
    db.close()


cat_griz_tweet_pull()

# By Anthony Layton (Tony Layton)
# 2018-12-10

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
from datetime import *
import calendar
import tweepy
from collections import Counter
import nltk
import random
from string import punctuation
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from pprint import pprint




# These are primarily used in the 'twitter API.py' file
def init_tweet_db(cur):
    # Purpose:
    #   Builds the Database table called 'tweets'
    #   will store the tweets in this table
    # Variables:
    #   cur = the connection to the database
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    cur.execute('''CREATE TABLE tweets (
    tweet_created TIMESTAMP,
    tweet_id INTEGER,
    user_id INTEGER,
    user_name TEXT,
    user_screen_name TEXT,
    user_description TEXT,
    user_location TEXT,
    search_term TEXT,
    tweet_text TEXT)''')


def init_users_db(cur):
    # Purpose:
    #   Builds the Database table called 'users'
    #   will store the users in this table
    # Variables:
    #   cur = the connection to the database
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    # cur.execute('''DROP TABLE IF EXISTS tweets''')
    cur.execute('''CREATE TABLE users (user_id INTEGER,
    user_id_str INTEGER,
    user_name TEXT,
    user_screen_name TEXT,
    user_location TEXT,
    user_followers_count INTEGER,
    user_friends_count INTEGER,
    user_favourites_count INTEGER,
    user_description TEXT,
    user_geo_enabled TEXT,
    user_lang TEXT,
    user_statuses_count INTEGER,
    user_time_zone TEXT,
    user_created_at TIMESTAMP,
    user_verified TEXT,
    user_utc_offset TEXT,
    user_contributors_enabled TEXT,
    user_listed_count INTEGER,
    user_protected TEXT,
    user_url TEXT,
    parent_user_screen_name TEXT)''')


def populate_tweet_db(db, line):
    # Purpose:
    #   populates 'tweet' database table with line
    # Variables:
    #   db = the database
    #   line = what to write to the database.
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    cur = db.cursor()
    cur.execute('''
            INSERT INTO tweets (tweet_created,tweet_id, user_id,
            user_name,user_screen_name,user_description,
            user_location,search_term,tweet_text)
            VALUES (?,?,?,?,?,?,?,?,?)''', line)
    db.commit()


def populate_users_db(db, line):
    # Purpose:
    #   will populate DB with the line
    # Variables:
    #   db = database
    #   line = the line that needs written
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   save_user()
    cur = db.cursor()
    cur.execute('''
            INSERT INTO users (user_id,user_id_str,user_name,user_screen_name,
            user_location,user_followers_count,user_friends_count,user_favourites_count,
            user_description,user_geo_enabled,user_lang,user_statuses_count,
            user_time_zone,user_created_at,user_verified,user_utc_offset,
            user_contributors_enabled,user_listed_count,user_protected,user_url,parent_user_screen_name)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', line)
    db.commit()


def get_populated_db_tweet_ids(cur):
    # Purpose:
    #   Pulls the tweet ids of previously populated tweets
    # Variables:
    #   cur = the database connecton
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    try:
        cur.fetchall()
        output = cur.execute("""SELECT DISTINCT tweet_id
        FROM tweets""")
        tweet_tweet = set()
        for i in output:
            tweet_tweet.update({(i[0])})
    except:
        tweet_tweet = set()
    return(tweet_tweet)


def get_populated_db_user_ids(cur):
    # Purpose:
    #   Pulls the user ids of previously populated users
    # Variables:
    #   cur = the database connection
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    try:
        cur.fetchall()
        output = cur.execute("""SELECT DISTINCT user_id
        FROM users""")
        users_user = set()
        for i in output:
            users_user.update({(i[0])})
    except:
        users_user = set()
    return(users_user)


def get_unpopulated_db_user_ids(cur):
    # Purpose:
    #   gets users that need to be populated in DB
    # Variables:
    #   cur = the database connection
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    try:
        cur.fetchall()
        output = cur.execute("""SELECT DISTINCT user_id
        FROM tweets""")
        tweet_user = set()
        for i in output:
            tweet_user.update({(i[0])})
    except:
        tweet_user = set()
    try:
        cur.fetchall()
        output = cur.execute("""SELECT DISTINCT user_id
        FROM users""")
        users_user = set()
        for i in output:
            users_user.update({(i[0])})
    except:
        users_user = set()
    users_to_find = tweet_user ^ users_user
    print("In tweet, but not in user {}".format(len(tweet_user - users_user)))
    print("In user, but not in tweet {}".format(len(users_user - tweet_user)))
    print("Total users to lookup {}".format(len(users_to_find)))
    return(users_to_find)


def save_user(db, user, master_db_name, parent_user_screen_name=None):
    # Purpose:
    #   saves user information to database
    # Variables:
    #   db = database
    #   user = the user
    #   master_db_name = the database name
    #   parent_user_screen_name = who this user followed
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    populate_users_db(db, [user.id, user.id_str, user.name, user.screen_name, user.location, user.followers_count,
           user.friends_count, user.favourites_count, user.description, user.geo_enabled, user.lang,
           user.statuses_count, user.time_zone, user.created_at, user.verified, user.utc_offset,
           user.contributors_enabled, user.listed_count, user.protected, user.url, parent_user_screen_name])
    print("Parent User:  {}\t\tDB:  {}\t\tSaved Child: {}".format(parent_user_screen_name,
                                                                  master_db_name,user.screen_name))


def grouper(n, iterable, padvalue=None):
    # Purpose:
    #   see purpose below (code by github user '37chandler')
    # Is used by the following functions to run:
    #   cat_griz_tweet_pull()
    ''' Partitions an iterable into groups of size `n`. If there are empty
        spots in the final group they are padded with `padvalue`. It should be
        clear, I just found this in the docs here: https://docs.python.org/3/library/itertools.html
        "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')" '''
    args = [iter(iterable)] * n
    return (zip_longest(*args, fillvalue=padvalue))


# These are primarily used in the 'sentiment.py' file
def classi(dict, subset_group):
    # Purpose:
    #   To classify the tweets as cat, griz, both, or neither.
    # Variables:
    #   Dict = is the dictionary to pass in.
    # Uses the following functions to run:
    #   -none-
    # Is used by the following functions to run:
    #   cat_griz_tweets_from_db()
    tweets = dict
    d = []
    g_count = 0
    c_count = 0
    cats = ['montanastate', 'MSUBobcats', 'MSUBobcatsFB']
    griz = ['umontana', 'UMGRIZZLIES', 'MontanaGrizFB']
    for tweet_created in tweets:
        for tweet_id in tweets[tweet_created]:
            for user_id in tweets[tweet_created][tweet_id]:
                is_cat = False
                is_griz = False
                cat_count = 0
                griz_count = 0
                if len(tweets[tweet_created][tweet_id][user_id]) > 1:
                    for i in tweets[tweet_created][tweet_id][user_id]:
                        if i in cats:
                            is_cat = True
                            cat_count += 1
                        elif i in griz:
                            is_griz = True
                            griz_count += 1
                        else:
                            pass
                else:
                    pass
                if is_cat == True and is_griz == True:
                    if cat_count > griz_count:
                        is_griz = False
                    elif cat_count < griz_count:
                        is_cat = False
                    else:
                        pass
                else:
                    pass
                child = 0
                for parent in tweets[tweet_created][tweet_id][user_id]:
                    if child != 0:
                        pass
                    else:
                        parents = 0
                        child += 1
                        if is_cat == True and is_griz == True:
                            parents = 'both'
                        elif is_cat == False and is_griz == True:
                            parents = 'griz'
                        elif is_cat == True and is_griz == False:
                            parents = 'cats'
                        elif is_cat == False and is_griz == False:
                            parents = 'neither'
                        else:
                            print("ERROR")
                        if subset_group == None:
                            if parents == 'griz':
                                g_count += 1
                                d.append((tweets[tweet_created][tweet_id][user_id][parent]['tweet_text'], parents))
                            elif parents == 'cats':
                                c_count += 1
                                d.append((tweets[tweet_created][tweet_id][user_id][parent]['tweet_text'], parents))
                            else:
                                pass
                        else:
                            pass
    print("GRIZ SAVED:  {}\t\tCATS SAVED:  {}".format(g_count, c_count))
    return(d)


def sentiment(dictonary):
    # Purpose:
    #   To classify the tweets and produce a dict.
    # Variables:
    #   dictonary = the dictonary to pass through
    # Uses the following functions to run:
    #
    # Is used by the following functions to run:
    #   cat_griz_tweets_from_db()
    tweets = dictonary
    the_words = dict()
    cats = ['montanastate', 'MSUBobcats', 'MSUBobcatsFB']
    griz = ['umontana', 'UMGRIZZLIES', 'MontanaGrizFB']
    for tweet_created in tweets:
        for tweet_id in tweets[tweet_created]:
            for user_id in tweets[tweet_created][tweet_id]:
                isCat = False
                isGriz = False
                Cat_count = 0
                Griz_count = 0
                if len(tweets[tweet_created][tweet_id][user_id]) > 1:
                    for i in tweets[tweet_created][tweet_id][user_id]:
                        if i in cats:
                            isCat = True
                            Cat_count += 1
                        elif i in griz:
                            isGriz = True
                            Griz_count += 1
                        else:
                            pass
                else:
                    pass
                if isCat == True and isGriz == True:
                    if Cat_count > Griz_count:
                        isGriz = False
                    elif Cat_count < Griz_count:
                        isCat = False
                    else:
                        pass
                else:
                    pass
                child = 0
                for parent in tweets[tweet_created][tweet_id][user_id]:
                    if child != 0:
                        pass
                    else:
                        parents = 0
                        child += 1
                        if isCat == True and isGriz == True:
                            parents = 'both'
                        elif isCat == False and isGriz == True:
                            parents = 'griz'
                        elif isCat == True and isGriz == False:
                            parents = 'cats'
                        elif isCat == False and isGriz == False:
                            parents = 'neither'
                        else:
                            print("ERROR")
                        the_words.update({tweet_created: {parents: {tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']}}})
    return(the_words)


def write_dict_to_text(dict, subset_group):
    # Purpose:
    #   Write the cat-griz dictionary to a text file. Can choose a specific group.
    # Variables:
    #   dict = what dictionary
    #   subset_group = (None - or -
    #           'griz' -and/or-
    #           'cats' -and/or-
    #           'both' -and/or-
    #           'unknown')
    # Uses the following functions to run:
    #   -none- (but the dictionary is produced with
    #           the ___ function)
    # Is used by the following functions to run:
    #   cat_griz_tweets_from_db()
    tweets = dict
    cats = ['montanastate', 'MSUBobcats', 'MSUBobcatsFB']
    griz = ['umontana', 'UMGRIZZLIES', 'MontanaGrizFB']
    if subset_group == None:
        output_file_name = 'CatGriz_TWEETS_ALL.txt'
    elif subset_group == 'griz':
        output_file_name = 'CatGriz_TWEETS_Follow_Griz.txt'
    elif subset_group == 'cats':
        output_file_name = 'CatGriz_TWEETS_Follow_Cats.txt'
    elif subset_group == 'both':
        output_file_name = 'CatGriz_TWEETS_Follow_BOTH.txt'
    elif subset_group == 'unknown':
        output_file_name = 'CatGriz_TWEETS_Follow_UNKN.txt'
    count_save = 0
    header = ['tweet_created', 'tweet_id', 'user_id', 'parent', 'tweet_text']
    with open(output_file_name, 'a+', encoding='utf-8') as o3file:
        o3file.write("\t".join(header) + "\n")
        for tweet_created in tweets:
            for tweet_id in tweets[tweet_created]:
                for user_id in tweets[tweet_created][tweet_id]:
                    isCat = False
                    isGriz = False
                    Cat_count = 0
                    Griz_count = 0
                    if len(tweets[tweet_created][tweet_id][user_id]) > 1:
                        for i in tweets[tweet_created][tweet_id][user_id]:
                            if i in cats:
                                isCat = True
                                Cat_count += 1
                            elif i in griz:
                                isGriz = True
                                Griz_count += 1
                            else:
                                pass
                    else:
                        pass
                    if isCat == True and isGriz == True:
                        if Cat_count > Griz_count:
                            isGriz = False
                        elif Cat_count < Griz_count:
                            isCat = False
                        else:
                            pass
                    else:
                        pass
                    child = 0
                    for parent in tweets[tweet_created][tweet_id][user_id]:
                        if child != 0:
                            pass
                        else:
                            parents = 0
                            child += 1
                            if isCat == True and isGriz == True:
                                parents = 3
                            elif isCat == False and isGriz == True:
                                parents = 2
                            elif isCat == True and isGriz == False:
                                parents = 1
                            elif isCat == False and isGriz == False:
                                parents = 0
                            else:
                                pass
                            if subset_group == None:
                                count_save += 1
                                row = [tweet_created, tweet_id, user_id, parents,
                                       tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']]
                                o3file.write("\t".join([str(item) for item in row]) + "\n")
                            elif subset_group == 'griz':
                                if parents == 2:
                                    count_save += 1
                                    row = [tweet_created, tweet_id, user_id, parents,
                                           tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']]
                                    o3file.write("\t".join([str(item) for item in row]) + "\n")
                            elif subset_group == 'cats':
                                if parents == 1:
                                    count_save += 1
                                    row = [tweet_created, tweet_id, user_id, parents,
                                           tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']]
                                    o3file.write("\t".join([str(item) for item in row]) + "\n")
                            elif subset_group == 'both':
                                if parents == 3:
                                    count_save += 1
                                    row = [tweet_created, tweet_id, user_id, parents,
                                           tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']]
                                    o3file.write("\t".join([str(item) for item in row]) + "\n")
                            elif subset_group == 'unknown':
                                if parents == 0:
                                    count_save += 1
                                    row = [tweet_created, tweet_id, user_id, parents,
                                           tweets[tweet_created][tweet_id][user_id][parent]['tweet_text']]
                                    o3file.write("\t".join([str(item) for item in row]) + "\n")
    o3file.close()
    print("{}\t{}".format(output_file_name, count_save))


def cat_griz_tweets_from_db(db_file=None, subset_group=None, write_to_file=False, other=None):
    # Purpose:
    #   Pulls the tweets out of the DB when running the Cat Griz Sentiment analysis.
    # Variables:
    #   db_file=None = WHAT DB to connect to (if other than
    #   subset_group=None = Cat
    #   write_to_file=False = Can Choose to write to file or to create dictonary
    #   other=None
    # Uses the following functions to run:
    #   write_dict_to_text()
    #   sentiment()
    #   classi()
    # Is used by the following functions:
    #   -none-
    if db_file == None:
        db = sqlite3.connect('CatGrizTweets.db')
    else:
        db = sqlite3.connect(db_file)
    cur = db.cursor()
    cur.fetchall()
    output_three = cur.execute("""SELECT DATETIME(tweets.tweet_created) as tweet_created,
	tweets.tweet_id AS tweet_id,
	tweets.user_id AS user_id,
	users.parent_user_screen_name AS parent,
	tweets.tweet_text AS tweet
    FROM tweets
    LEFT OUTER JOIN users on users.user_id=tweets.user_id
    WHERE tweet_created >= DATETIME('2018-11-17 19:00:00')
    AND tweet_created <= DATETIME('2018-11-17 23:59:59')
    AND tweet NOT LIKE '%basketball%'
    AND tweet NOT LIKE '%Apprentice%'
    AND tweet NOT LIKE '%tip off%'
    AND tweet NOT LIKE '%NBA%'
    AND tweet NOT LIKE '%@NHLBruins%'
    AND tweet NOT LIKE '%Jazz%'
    AND tweet NOT LIKE '%hoops%'
    AND tweet NOT LIKE '%Volleyballe%'
    AND tweet NOT LIKE '%Casa Roble%'
    AND tweet NOT LIKE '%shooting%'
    AND tweet NOT LIKE '%rebound%'
    AND tweet NOT LIKE '%texas%'
    AND tweet NOT LIKE '%Texas%'
    AND tweet NOT LIKE '%Texas%'
    AND tweet NOT LIKE '%texans%'
    AND tweet NOT LIKE '%lamar%'
    AND tweet NOT LIKE '%Mount Academy%'
    AND tweet NOT LIKE '%WCDO%'
    AND tweet NOT LIKE '%TX%'
    AND tweet NOT LIKE '%Little Rock%'
    AND tweet NOT LIKE '%LittleRocksTeam%'
    AND tweet NOT LIKE '%cougars%'
    AND tweet NOT LIKE '%Cougars%'
    AND tweet NOT LIKE '%hockey%'
    AND tweet NOT LIKE '%women%'
    AND tweet NOT LIKE '%Hayti%'
    AND tweet NOT LIKE '%hayti%'
    AND tweet NOT LIKE '%Ohio%'
    AND tweet NOT LIKE '%ohio%'
    AND tweet NOT LIKE '%shooting%'
    AND tweet NOT LIKE '%Lions%'
    AND tweet NOT LIKE '%lions%'
    AND tweet NOT LIKE '%Eagles%'
    AND tweet NOT LIKE '%eagles%'
    AND tweet NOT LIKE '%last night%'
    AND tweet NOT LIKE '%Friday night%'
    AND tweet NOT LIKE '%Crispus%'
    AND tweet NOT LIKE '%crispus%'
    AND tweet NOT LIKE '%Attucks%'
    AND tweet NOT LIKE '%attucks%'
    AND tweet NOT LIKE '%Plymouth%'
    AND tweet NOT LIKE '%wd%'
    AND tweet NOT LIKE '%WD%'
    AND tweet NOT LIKE '%Vogele%'
    AND tweet NOT LIKE '%New England%'
    AND tweet NOT LIKE '%Ragsdale%'
    AND tweet NOT LIKE '%Orangefield Elementary%'
    AND tweet NOT LIKE '%@Ragsdale_RHS%'
    AND tweet NOT LIKE '%California%'
    AND tweet NOT LIKE '%California%'
    AND tweet NOT LIKE '%@Defenders%'
    AND tweet NOT LIKE '%@CHSKnoxSports%'
    AND tweet NOT LIKE '%#CTNFF%'
    AND tweet NOT LIKE '%#CTNFF%'
    AND tweet NOT LIKE '%Elks%'
    AND tweet NOT LIKE '%Cornell%'
    AND tweet NOT LIKE '%Puentes%'
    AND tweet NOT LIKE '%Dinos%'
    AND tweet NOT LIKE '%Malcolm X%'
    AND tweet NOT LIKE '%Radford%'
    AND tweet NOT LIKE '%Gretna%'
    AND tweet NOT LIKE '%WNE%'
    AND tweet NOT LIKE '%Rio Hondo%'
    AND tweet NOT LIKE '%Mustangs%'
    AND tweet NOT LIKE '%Lady Bobcats%'
    AND tweet NOT LIKE '%Central Bobcats%'
    AND tweet NOT LIKE '%Ingleside%'
    AND tweet NOT LIKE '%@OzarksOzone%'
    AND tweet NOT LIKE '%Panama%'
    AND tweet NOT LIKE '%Livingstone%'
    AND tweet NOT LIKE '%@BFND_Football%'
    AND tweet NOT LIKE '%MHSP%'
    AND tweet NOT LIKE '%Wildlife Refuges%'
    AND tweet NOT LIKE '%Dayton%'
    AND tweet NOT LIKE '%Hounds%'
    AND tweet NOT LIKE '%Kernels%'
    AND tweet NOT LIKE '%UWF%'
    ORDER BY tweets.tweet_created, tweets.tweet_id;""")
    # GAME STARTED at 2018-11-17 @ 12:00 MST (19:00 UTC) ENDED @ est. 22:21:19 UTC
    # NOW MOVE QUERY TO DIC
    tweets = defaultdict(lambda:
                         defaultdict(lambda:
                                     defaultdict(lambda:
                                                 defaultdict(lambda:
                                                             defaultdict()))))
    # tweets[tweet_created][tweet_id][user_id][parent] tweet_text
    # tweets{tweet_created: {tweet_id: {user_id: {parent: tweet_text}}}}
    count_pull = 0
    for row in output_three:
        count_pull += 1
        tweet_created, tweet_id, user_id, parent, tweet_text = row
        tweets[tweet_created][tweet_id][user_id][parent]['tweet_text'] = str(tweet_text)
    db.close()
    if write_to_file is True:
        write_dict_to_text(dict=tweets, subset_group=subset_group)
    else:
        pass
    if other == 'classi':
        d = classi(dict=tweets)
        return(d)
    elif other == 'sentiment':
        the_words = sentiment(dictonary=tweets)
        return(the_words)
    elif other == 'dict':
        return(tweets)
    else:
        pass

# By Anthony Layton
# 2018-12-10


from DB_connect_common import *


def cat_griz_sentiment_analysis():
    # Purpose:
    #   To run the sentiment analysis and save it to file
    # Variables:
    #   -none-
    # Uses the following functions to run:
    #   cat_griz_tweets_from_db()
    # Is used by the following functions:
    #   -none-
    all_game_tweets = cat_griz_tweets_from_db(other='sentiment')
    sentiment_scores = {}
    with open("tidytext_sentiments.txt",'r') as infile:
        next(infile)
        for line in infile.readlines():
            line = line.strip().split("\t")
            if line[1] == "positive":
                sentiment_scores[line[0]] = 1
            else:
                sentiment_scores[line[0]] = -1
    griz_positive = ['ftc', 'go griz', 'fuck the cats', '#gogriz', 'gooooo griz', 'griznation', 'griz nation']
    cats_positive = ['ftg', 'go cats', 'go bobcats', 'fuck the griz', '#gocats', 'gocatsgo']

    date_time2 = list()
    for date_time in all_game_tweets:
        date_time2.append(calendar.timegm((datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').timetuple())))

    pre_write_list = list()
    score_cats = 0
    score_griz = 0
    score_others = 0
    for time_stamp in range(date_time2[0], date_time2[-1]):
        tweet_time_stamp = str(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time_stamp)))
        recorded_time_stamp = str(time.strftime('%H%M%S', time.gmtime(time_stamp - 25200)))
        try:
            for team in all_game_tweets[tweet_time_stamp]:
                if team is 'griz':
                    for whole_tweet_text in all_game_tweets[tweet_time_stamp][team]:
                        line = [x.strip() for x in whole_tweet_text.split()]
                        for idx, word in enumerate(line):
                            if word.lower() in sentiment_scores:
                                score_griz += sentiment_scores[word.lower()]
                        for item in griz_positive:
                            text = re.findall(item, whole_tweet_text.lower())
                            score_griz += (len(text))
                        pre_write_list.extend([[recorded_time_stamp, 'Montana', str(score_griz)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Montana State', str(score_cats)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Others', str(score_others)]])
                elif team is 'cats':
                    for whole_tweet_text in all_game_tweets[tweet_time_stamp][team]:
                        line = [x.strip() for x in whole_tweet_text.split()]
                        for idx, word in enumerate(line):
                            if word.lower() in sentiment_scores:
                                score_cats += sentiment_scores[word.lower()]
                        for item in cats_positive:
                            text = re.findall(item, whole_tweet_text.lower())
                            score_cats += (len(text))
                        pre_write_list.extend([[recorded_time_stamp, 'Montana', str(score_griz)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Montana State', str(score_cats)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Others', str(score_others)]])
                else:
                    for whole_tweet_text in all_game_tweets[tweet_time_stamp][team]:
                        line = [x.strip() for x in whole_tweet_text.split()]
                        for idx, word in enumerate(line):
                            if word.lower() in sentiment_scores:
                                score_others += sentiment_scores[word.lower()]
                        for item in griz_positive:
                            text = re.findall(item, whole_tweet_text.lower())
                            score_griz += (len(text))
                        for item in cats_positive:
                            text = re.findall(item, whole_tweet_text.lower())
                            score_cats += (len(text))
                        pre_write_list.extend([[recorded_time_stamp, 'Montana', str(score_griz)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Montana State', str(score_cats)]])
                        pre_write_list.extend([[recorded_time_stamp, 'Others', str(score_others)]])
        except:
            pre_write_list.extend([[recorded_time_stamp, 'Montana', str(score_griz)]])
            pre_write_list.extend([[recorded_time_stamp, 'Montana State', str(score_cats)]])
            pre_write_list.extend([[recorded_time_stamp, 'Others', str(score_others)]])
    with open("Cat_Griz_Sentiment.txt", "w") as openfile:
        openfile.write("Date_Time\tTeam\tScore\n")
        for line in pre_write_list:
            openfile.write("\t".join(line) + "\n")


cat_griz_sentiment_analysis()

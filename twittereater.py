# -*- coding: utf-8 -*-
import csv
from local_settings import TWITTER_ARCHIVE_NAME, TEST_SOURCE, IGNORE_RETWEETS

f = open(TWITTER_ARCHIVE_NAME, 'r')
tweets = []
reader = csv.reader(f,quotechar='"')
next(reader) #get rid of the twitter header


tweetarchive = open(TEST_SOURCE, 'w')
for row in reader:
    if IGNORE_RETWEETS:
        if not row[8]: #9th column is the timestamp of the retweet
            tweetarchive.write("'%s'," % (row[5]))
    else:
        tweetarchive.write("'%s'," % (row[5]))


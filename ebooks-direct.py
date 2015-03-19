import random
import re
import sys
import twitter
import markov

from htmlentitydefs import name2codepoint as n2c
from local_settings_TEST import *

# Edited for running direct on me Ras Pi
# Instead of giving up on a failed tweet retries until success

def connect():
    api = twitter.Api(consumer_key=MY_CONSUMER_KEY,
                          consumer_secret=MY_CONSUMER_SECRET,
                          access_token_key=MY_ACCESS_TOKEN_KEY,
                          access_token_secret=MY_ACCESS_TOKEN_SECRET)
    return api

def entity(text):
    if text[:2] == "&#":
        try:
            if text[:3] == "&#x":
                return unichr(int(text[3:-1], 16))
            else:
                return unichr(int(text[2:-1]))
        except ValueError:
            pass
    else:
        guess = text[1:-1]
        numero = n2c[guess]
        try:
            text = unichr(numero)
        except KeyError:
            pass    
    return text

def filter_tweet(tweet):
    tweet.text = re.sub(r'\b(RT|MT) .+','',tweet.text) #take out anything after RT or MT
    tweet.text = re.sub(r'(\#|@|(h\/t)|(http))\S+','',tweet.text) #Take out URLs, hashtags, hts, etc.
    tweet.text = re.sub(r'\n','', tweet.text) #take out new lines.
    tweet.text = re.sub(r'\"|\(|\)', '', tweet.text) #take out quotes.
    htmlsents = re.findall(r'&\w+;', tweet.text)
    if len(htmlsents) > 0 :
        for item in htmlsents:
            tweet.text = re.sub(item, entity(item), tweet.text)    
    tweet.text = re.sub(r'\xe9', 'e', tweet.text) #take out accented e
    return tweet.text
                                
                                                    
def grab_tweets(api, max_id=None):
    source_tweets=[]
    user_tweets = api.GetUserTimeline(screen_name=user, count=200, max_id=max_id, include_rts=True, trim_user=True, exclude_replies=True)
    max_id = user_tweets[len(user_tweets)-1].id-1
    for tweet in user_tweets:
        tweet.text = filter_tweet(tweet)
        if len(tweet.text) != 0:
            source_tweets.append(tweet.text)
    return source_tweets, max_id

if __name__=="__main__":
    order = ORDER
    if DEBUG==False:
        guess = random.choice(range(ODDS))
    else:
        guess = 0

    if guess == 0:
        if STATIC_TEST==True:
            file = TEST_SOURCE
            print ">>> Generating from {0}".format(file)
            string_list = open(file).readlines()
            for item in string_list:
                source_tweets = item.split(",")    
        else:
            source_tweets = []
            for handle in SOURCE_ACCOUNTS:
                user=handle
                api=connect()
                max_id=None
                for x in range(17)[1:]:
                    source_tweets_iter, max_id = grab_tweets(api,max_id)
                    source_tweets += source_tweets_iter
                print "{0} tweets found in {1}".format(len(source_tweets), handle)
                if len(source_tweets) == 0:
                    print "Error fetching tweets from Twitter. Aborting."
                    sys.exit()

        
        success = False

        # this section does the actual building of tweet
        # changed it to try again on failure, default was to just give up

        mine = markov.MarkovChainer(order)

        while success == False:
            
            ebook_tweet = ""  # this clears out any previous unsuccessful attempt

            for tweet in source_tweets:
                if re.search('([\.\!\?\"\']$)', tweet):
                    pass
                else:
                    tweet+="."
                mine.add_text(tweet)
            
            #for x in range(0,10):

            ebook_tweet = mine.generate_sentence()
   
            #if a tweet is very short, this will randomly add a second sentence to it.
            if ebook_tweet != None and len(ebook_tweet) < 40:
                rando = random.randint(0,10)
                if rando == 0 or rando == 7: 
                    print "Short tweet. Adding another sentence randomly"
                    newer_tweet = mine.generate_sentence()
                    if newer_tweet != None:
                        ebook_tweet += " " + mine.generate_sentence()
                    else:
                        ebook_tweet = ebook_tweet
                elif rando == 1:
                    #say something crazy/prophetic in all caps
                    print "ALL THE THINGS"
                    ebook_tweet = ebook_tweet.upper()

            #throw out tweets that match anything from the source account.
            if ebook_tweet != None and len(ebook_tweet) < 120:
                success = True
                for tweet in source_tweets:
                    if ebook_tweet[:-1] not in tweet:
                        continue
                    else: 
                        print "TOO SIMILAR: " + ebook_tweet
                        success = False
            elif ebook_tweet == None:
                print "I done goofed, there's nothing in the tweet"
                success = False
            elif len(ebook_tweet) >= 120:
                print "That's too long, whoopsypoops"
                success = False
            else:
                print "I have no idea what I'm doing"
                success = False
            
        # Couldn't find anything wrong with the tweet so here goes
            if success == True:
                if DEBUG == False:
                    status = api.PostUpdate(ebook_tweet)
                    print status.text.encode('utf-8')         
                else:
                    print "SUCCESS: " + ebook_tweet
                
    else:
        print "This time I'm not doing a tweet, so there" #message if the random number fails.

import random
import re
import sys
import twitter
import markov
from htmlentitydefs import name2codepoint as n2c
from local_settings import *

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
        mine = markov.MarkovChainer(order)
        for tweet in source_tweets:
            if re.search('([\.\!\?\"\']$)', tweet):
                pass
            else:
                tweet+="."
            mine.add_text(tweet)
            
        for x in range(0,10):
            ebook_tweet = mine.generate_sentence()

        #randomly drop the last word, as Horse_ebooks appears to do.
        if random.randint(0,4) == 0 and re.search(r'(in|to|from|for|with|by|our|of|your|around|under|beyond)\s\w+$', ebook_tweet) != None: 
           print "Losing last word randomly"
           ebook_tweet = re.sub(r'\s\w+.$','',ebook_tweet) 
           print ebook_tweet
    
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
        if ebook_tweet != None and len(ebook_tweet) < 110:
            for tweet in source_tweets:
                if ebook_tweet[:-1] not in tweet:
                    continue
                else: 
                    print "TOO SIMILAR: " + ebook_tweet
                    sys.exit()
                          
            if DEBUG == False:
                status = api.PostUpdate(ebook_tweet)
                print status.text.encode('utf-8')
            else:
                print ebook_tweet

        elif ebook_tweet == None:
            print "Tweet is empty, sorry."
        else:
            print "TOO LONG: " + ebook_tweet
    else:
        print str(guess) + " No, sorry, not this time." #message if the random number fails.
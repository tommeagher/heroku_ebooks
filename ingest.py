import re
import markov
import cPickle as pickle

from htmlentitydefs import name2codepoint as n2c
from local_settings import *

# Takes text file, builds the Markov object and sticks it on disk for future use

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

#Filters crap out of tweets

def filter_tweet(tweet):
    tweet = re.sub(r'\b(RT|MT) .+','',tweet) #take out anything after RT or MT
    tweet = re.sub(r'(\#|@|(h\/t)|(http))\S+','',tweet) #Take out URLs, hashtags, hts, etc.
    tweet = re.sub(r'\n','', tweet) #take out new lines.
    tweet = re.sub(r'\"|\(|\)', '', tweet) #take out quotes.
    htmlsents = re.findall(r'&\w+;', tweet)
    if len(htmlsents) > 0 :
        for item in htmlsents:
            tweet = re.sub(item, entity(item), tweet)    
    return tweet

if __name__=="__main__":
   
    # Source text file
    file = TEXT_SOURCE

    # Initialise list for tweets
    source_tweets=[]

    # A lovely message for the console
    print ">>> Generating from {0}".format(file)

    # create a list from the source file
    raw_tweets = list(open(file))

    # decode each tweet from UTF-8, and filter it to kick out
    # RT/MT, @, web links and the like
    # This gives an array of plainish text tweets that are just
    # sentences

    for twat in raw_tweets[:]:
        source_tweets.append(filter_tweet(twat.decode('UTF-8')))
        
    # something in Markov is broken so only order 2 works properly
    # Maybe one day I'll know enough to fix the bug
    # One day...

    # this section does the actual building of the bot's brain
    # by cramming in cleaned up tweets one by one

    # create Markov object

    mine = markov.MarkovChainer(2) # change "2" to "order" to use order from config file

    for tweet in source_tweets:
        # if the tweet has punctuation in it, then great
        if re.search('([\.\!\?\"\']$)', tweet):
            pass
        # otherwise add a full stop at the end or it'll get upset
        # when it tries to split the text
        else:
            tweet+="."
        mine.add_text(tweet)

    # Do something to stick objects "mine" and "source_tweets" onto disk for later use

    pickle.dump( mine , open("botbrain.p", "wb" ))
    pickle.dump( source_tweets, open("source_tweets.p","wb"))

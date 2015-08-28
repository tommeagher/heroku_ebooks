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
   
    file = TEXT_SOURCE
    source_tweets=[]
    print ">>> Generating from {0}".format(file)
    raw_tweets = list(open(file))
    for twat in raw_tweets[:]:
        source_tweets.append(filter_tweet(twat.decode('UTF-8')))
        
    # this section does the actual building of bot's brain
    
    # something in Markov is broken so only order 2 works properly
    # Maybe one day I'll know enough to fix the bug
    # One day...
        
    mine = markov.MarkovChainer(2) # change "2" to "order" to use order from config file

    ebook_tweet = ""  # this clears out any previous unsuccessful attempt

    for tweet in source_tweets:
        if re.search('([\.\!\?\"\']$)', tweet):
            pass
        else:
            tweet+="."
        mine.add_text(tweet)

# Do something to stick object "mine" onto disk for later use

    pickle.dump( mine , open("botbrain.p", "wb" ))
    


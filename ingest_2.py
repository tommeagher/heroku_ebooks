import re
import markov_2
import sqlite3

from htmlentitydefs import name2codepoint as n2c
from local_settings import *

# Builds Markov database from text file by cleaning up text
# And adding each line to the DB

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

    db = sqlite3.connect(BRAIN_PATH)
    brain = db.cursor()

    try:
        brain.execute("DROP TABLE tweets")
        brain.execute("CREATE TABLE tweets(tweet)")
    except:
        brain.execute("CREATE TABLE tweets(tweet)")

    # Initialise list for tweets
    source_tweets=[]

    print "Using brain" + BRAIN_PATH
    print ">>> Generating from {0}".format(file)

    # create a list from the source file
    raw_tweets = list(open(file))

    # decode each tweet from UTF-8, and filter it to kick out
    # RT/MT, @, web links and the like
    # This gives an array of plainish text tweets that are just
    # sentences

    for twat in raw_tweets[:]:
        source_tweets.append(filter_tweet(twat.decode('UTF-8')))
        brain.execute("INSERT INTO tweets VALUES (?)", (filter_tweet(twat.decode('UTF-8')),))

    # something in Markov is broken so only order 2 works properly
    # Maybe one day I'll know enough to fix the bug
    # One day...

    # this section does the actual building of the bot's brain
    # by cramming in cleaned up tweets one by one

    # create Markov object

    #mine = markov.MarkovChainer(2) # change "2" to "order" to use order from config file

    db.commit()
    db.close()

    mine = markov_2.MarkovChainer(2,BRAIN_LOCATION) # change "2" to "order" to use order from config file

    mine.init_db()

    for tweet in source_tweets:
        # if the tweet has punctuation in it, then great
        if re.search('([\.\!\?\"\']$)', tweet):
            pass
        # otherwise add a full stop at the end or it'll get upset
        # when it tries to split the text
        else:
            tweet+="."
        mine.add_text(tweet)

<<<<<<< HEAD:ingest_2.py
    mine.commit_db()
    mine.compact_db()
=======
# Do something to stick object "mine" onto disk for later use

    pickle.dump( mine , open(BRAIN_LOCATION + "botbrain.p", "wb" ))
    pickle.dump( source_tweets, open(BRAIN_LOCATION + "source_tweets.p","wb"))
>>>>>>> master:ingest.py

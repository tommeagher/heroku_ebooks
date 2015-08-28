'''
This is based/copied and broken from https://github.com/tommeagher/heroku_ebooks),
'''

#configuration
MY_CONSUMER_KEY = ''
MY_CONSUMER_SECRET = ''
MY_ACCESS_TOKEN_KEY = ''
MY_ACCESS_TOKEN_SECRET = ''

#How often do you want this to run? Runs every 1/ODDS times
ODDS = 8

# how closely do you want this to hew to sensical? 1 is low and 3 is high.
# 1 currently makes it fall over and 3 doesn't seem to work well, 2 works best
ORDER = 2

# False - attempt to tweet outputs, True - just be sick in the console
DEBUG = True 

# The name of a UTF-8 text file, one tweet (or whatever) per line
# This is the file ingest.py noms

TEXT_SOURCE = "" 

#The name of the account you're tweeting to.
TWEET_ACCOUNT = "" 

#When the bot replies does it reply to everyone or just to original
#Tweet that mentioned it
REPLY_TO_ALL = False

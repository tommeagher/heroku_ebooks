'''
This is based/copied and broken from https://github.com/tommeagher/heroku_ebooks),
'''

#configuration
MY_CONSUMER_KEY = ''
MY_CONSUMER_SECRET = ''
MY_ACCESS_TOKEN_KEY = ''
MY_ACCESS_TOKEN_SECRET = ''

#A list of comma-separated, quote-enclosed Twitter handles of account that you'll generate tweets based on. It should look like ["account1", "account2"]. If you want just one account, no comma needed.
SOURCE_ACCOUNTS = [""] 

#How often do you want this to run? Runs every 1/ODDS times
ODDS = 1 

# how closely do you want this to hew to sensical? 1 is low and 3 is high.
# 1 currently makes it fall over and 3 doesn't seem to work well, 2 works best
ORDER = 2

# False - attempt to tweet outputs, True - just be sick in the console
DEBUG = False 

# Use a text file of tweets instead of grabbing them from the API
TEXT_INPUT = True

# The name of a UTF-8 text file, one tweet (or whatever) per line 
TEXT_SOURCE = "" 

#The name of the account you're tweeting to.
TWEET_ACCOUNT = "" 

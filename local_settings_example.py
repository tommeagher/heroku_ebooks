'''
This is based/copied and broken from https://github.com/tommeagher/heroku_ebooks),
'''

#Twitter configuration
MY_CONSUMER_KEY = ''
MY_CONSUMER_SECRET = ''
MY_ACCESS_TOKEN_KEY = ''
MY_ACCESS_TOKEN_SECRET = ''

#Imgur API key
IMGUR_CLIENT_ID = ''
IMGUR_CLIENT_SECRET = ''

#How often do you want this to run? Runs every 1/ODDS times
ODDS = 8

# how closely do you want this to hew to sensical? 1 is low and 3 is high.
# 1 currently makes it fall over and 3 doesn't seem to work well, 2 works best
ORDER = 2

# False - attempt to tweet outputs, True - just be sick in the console
DEBUG = False

# The name of a UTF-8 text file, one tweet (or whatever) per line 
TEXT_SOURCE = "mrpsb.txt" 

#The name of the account you're tweeting to.
TWEET_ACCOUNT = "MrPSB_ebooks" 

#When the bot replies does it reply to everyone or just to original
#Tweet that mentioned it
<<<<<<< HEAD
REPLY_TO_ALL = True
=======
REPLY_TO_ALL = False
>>>>>>> master

# Running from the command line is fine
# But it needs to know where stuff is if you're using cron
# or something

<<<<<<< HEAD
BRAIN_LOCATION = "./"
BRAIN_PATH = "./brain.db"
=======
INSTALL_LOCATION = ""
>>>>>>> master

from os import environ

'''
Local Settings for a heroku_ebooks account. 
'''

# Configuration for Twitter API
# Generate using global variables in heroku
ENABLE_TWITTER_SOURCES = True # Fetch twitter statuses as source
ENABLE_TWITTER_POSTING = True # Tweet resulting status?
MY_CONSUMER_KEY = environ.get('TWITTER_CONSUMER_KEY')#Your Twitter API Consumer Key set in Heroku config
MY_CONSUMER_SECRET = environ.get('TWITTER_CONSUMER_SECRET')#Your Consumer Secret Key set in Heroku config
MY_ACCESS_TOKEN_KEY = environ.get('TWITTER_ACCESS_TOKEN_KEY')#Your Twitter API Access Token Key set in Heroku config
MY_ACCESS_TOKEN_SECRET = environ.get('TWITTER_ACCESS_SECRET')#Your Access Token Secret set in Heroku config

# Configuration for Mastodon API
ENABLE_MASTODON_SOURCES = False # Fetch mastodon statuses as a source?
ENABLE_MASTODON_POSTING = False # Toot resulting status?
MASTODON_API_BASE_URL = "" # an instance url like https://botsin.space
CLIENT_CRED_FILENAME = '' # the MASTODON client secret file you created for this project
USER_ACCESS_FILENAME = '' # The MASTODON user credential file you created at installation.

# Sources (Twitter, Mastodon, local text file or a web page)
#NOTE: Only twitter is controlled via heroku at this time
TWITTER_SOURCE_ACCOUNTS = environ.get('TWEET_SOURCE_ACC').split(",")   # Creates a single entry list for use with a single source account 
MASTODON_SOURCE_ACCOUNTS = [""] # A list, e.g. ["@user@instance.tld"]
SOURCE_EXCLUDE = r'^$'  # Source tweets that match this regexp will not be added to the Markov chain. You might want to filter out inappropriate words for example.
STATIC_TEST = False  # Set this to True if you want to test Markov generation from a static file instead of the API.
TEST_SOURCE = ".txt"  # The name of a text file of a string-ified list for testing. To avoid unnecessarily hitting Twitter API. You can use the included testcorpus.txt, if needed.
SCRAPE_URL = False  # Set this to true to scrape a webpage.
SRC_URL = ['http://www.example.com/one', 'https://www.example.com/two']  # A comma-separated list of URLs to scrape
WEB_CONTEXT = ['span', 'h2']  # A comma-separated list of the tag or object to search for in each page above.
WEB_ATTRIBUTES = [{'class': 'example-text'}, {}] # A list of dictionaries containing the attributes for each page.

ODDS = int(environ.get('TWEET_ODDS')) # How often do you want this to run? 1/8 times? Set in Heroku Config
ORDER = int(environ.get('TWEET_ORDER'))  # How closely do you want this to hew to sensical? 2 is low and 4 is high.Set in Heroku Config

DEBUG = False  # Set this to False to start Tweeting live
TWEET_ACCOUNT = environ.get('TWEET_ACCOUNT') # The name of the account you're tweeting to. Set in Heroku Config

#Configuration for Twitter parser. TEST_SOURCE will be re-used as as the corpus location.
TWITTER_ARCHIVE_NAME = "tweets.csv" #Name of your twitter archive
IGNORE_RETWEETS = True #If you want to remove retweets

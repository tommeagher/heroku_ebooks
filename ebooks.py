import random
import re
import sys
import twitter
from mastodon import Mastodon
import markov
from bs4 import BeautifulSoup
try:
    # Python 3
    from html.entities import name2codepoint as n2c
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from htmlentitydefs import name2codepoint as n2c
    from urllib2 import urlopen
    chr = unichr
from local_settings import *


def connect(type='twitter'):
    if type == 'twitter':
        return twitter.Api(consumer_key=MY_CONSUMER_KEY,
                       consumer_secret=MY_CONSUMER_SECRET,
                       access_token_key=MY_ACCESS_TOKEN_KEY,
                       access_token_secret=MY_ACCESS_TOKEN_SECRET)
    elif type == 'mastodon':
        return Mastodon(client_id=CLIENT_CRED_FILENAME, api_base_url=MASTODON_API_BASE_URL, access_token=USER_ACCESS_FILENAME)
    return None


def entity(text):
    if text[:2] == "&#":
        try:
            if text[:3] == "&#x":
                return chr(int(text[3:-1], 16))
            else:
                return chr(int(text[2:-1]))
        except ValueError:
            pass
    else:
        guess = text[1:-1]
        if guess == "apos":
            guess = "lsquo"
        numero = n2c[guess]
        try:
            text = chr(numero)
        except KeyError:
            pass
    return text


def filter_status(text):
    text = re.sub(r'\b(RT|MT) .+', '', text)  # take out anything after RT or MT
    text = re.sub(r'(\#|@|(h\/t)|(http))\S+', '', text)  # Take out URLs, hashtags, hts, etc.
    text = re.sub('\s+', ' ', text)  # collaspse consecutive whitespace to single spaces.
    text = re.sub(r'\"|\(|\)', '', text)  # take out quotes.
    text = re.sub(r'\s+\(?(via|says)\s@\w+\)?', '', text)  # remove attribution
    text = re.sub(r'<[^>]*>','', text) #strip out html tags from mastodon posts
    htmlsents = re.findall(r'&\w+;', text)
    for item in htmlsents:
        text = text.replace(item, entity(item))
    text = re.sub(r'\xe9', 'e', text)  # take out accented e
    return text


def scrape_page(src_url, web_context, web_attributes):
    tweets = []
    last_url = ""
    for i in range(len(src_url)):
        if src_url[i] != last_url:
            last_url = src_url[i]
            print(">>> Scraping {0}".format(src_url[i]))
            try:
                page = urlopen(src_url[i])
            except Exception:
                last_url = "ERROR"
                import traceback
                print(">>> Error scraping {0}:".format(src_url[i]))
                print(traceback.format_exc())
                continue
            soup = BeautifulSoup(page, 'html.parser')
        hits = soup.find_all(web_context[i], attrs=web_attributes[i])
        if not hits:
            print(">>> No results found!")
            continue
        else:
            errors = 0
            for hit in hits:
                try:
                    tweet = str(hit.text).strip()
                except (UnicodeEncodeError, UnicodeDecodeError):
                    errors += 1
                    continue
                if tweet:
                    tweets.append(tweet)
            if errors > 0:
                print(">>> We had trouble reading {} result{}.".format(errors, "s" if errors > 1 else ""))
    return(tweets)


def grab_tweets(api, max_id=None):
    source_tweets = []
    user_tweets = api.GetUserTimeline(screen_name=user, count=200, max_id=max_id, include_rts=True, trim_user=True, exclude_replies=True)
    if user_tweets:
        max_id = user_tweets[-1].id - 1
        for tweet in user_tweets:
            tweet.text = filter_status(tweet.text)
            if re.search(SOURCE_EXCLUDE, tweet.text):
                continue
            if tweet.text:
                source_tweets.append(tweet.text)
    else:
        pass
    return source_tweets, max_id

def grab_toots(api, account_id=None,max_id=None):
    if account_id:
        source_toots = []
        user_toots = api.account_statuses(account_id)
        max_id = user_toots[len(user_toots)-1]['id']-1
        for toot in user_toots:
            if toot['in_reply_to_id'] or toot['reblog']:
                pass #skip this one
            else:
                toot['content'] = filter_status(toot['content'])
                if len(toot['content']) != 0:
                    source_toots.append(toot['content'])
        return source_toots, max_id

if __name__ == "__main__":
    order = ORDER
    guess = 0
    if ODDS and not DEBUG:
        guess = random.randint(0, ODDS - 1)

    if guess:
        print(str(guess) + " No, sorry, not this time.")  # message if the random number fails.
        sys.exit()
    else:
        api = connect()
        source_statuses = []
        if STATIC_TEST:
            file = TEST_SOURCE
            print(">>> Generating from {0}".format(file))
            string_list = open(file).readlines()
            for item in string_list:
                source_statuses += item.split(",")
        if SCRAPE_URL:
            source_statuses += scrape_page(SRC_URL, WEB_CONTEXT, WEB_ATTRIBUTES)
        if ENABLE_TWITTER_SOURCES and TWITTER_SOURCE_ACCOUNTS and len(TWITTER_SOURCE_ACCOUNTS[0]) > 0:
            twitter_tweets = []
            for handle in TWITTER_SOURCE_ACCOUNTS:
                user = handle
                handle_stats = api.GetUser(screen_name=user)
                status_count = handle_stats.statuses_count
                max_id = None
                my_range = min(17, int((status_count/200) + 1))
                for x in range(1, my_range):
                    twitter_tweets_iter, max_id = grab_tweets(api, max_id)
                    twitter_tweets += twitter_tweets_iter
                print("{0} tweets found in {1}".format(len(twitter_tweets), handle))
                if not twitter_tweets:
                    print("Error fetching tweets from Twitter. Aborting.")
                    sys.exit()
                else:
                    source_statuses += twitter_tweets
        if ENABLE_MASTODON_SOURCES and len(MASTODON_SOURCE_ACCOUNTS) > 0:
            source_toots = []
            mastoapi = connect(type='mastodon')
            max_id=None
            for handle in MASTODON_SOURCE_ACCOUNTS:
                accounts = mastoapi.account_search(handle)
                if len(accounts) != 1:
                    pass # Ambiguous search
                else:
                    account_id = accounts[0]['id']
                    num_toots = accounts[0]['statuses_count']
                    if num_toots < 3200:
                        my_range = int((num_toots/200)+1)
                    else:
                        my_range = 17
                    for x in range(my_range)[1:]:
                        source_toots_iter, max_id = grab_toots(mastoapi,account_id, max_id=max_id)
                        source_toots += source_toots_iter
                    print("{0} toots found from {1}".format(len(source_toots), handle))
                    if len(source_toots) == 0:
                        print("Error fetching toots for %s. Aborting." % handle)
                        sys.exit()
            source_statuses += source_toots
        if len(source_statuses) == 0:
            print("No statuses found!")
            sys.exit()
        mine = markov.MarkovChainer(order)
        for status in source_statuses:
            if not re.search('([\.\!\?\"\']$)', status):
                status += "."
            mine.add_text(status)
        for x in range(0, 10):
            ebook_status = mine.generate_sentence()

        # randomly drop the last word, as Horse_ebooks appears to do.
        if random.randint(0, 4) == 0 and re.search(r'(in|to|from|for|with|by|our|of|your|around|under|beyond)\s\w+$', ebook_status) is not None:
            print("Losing last word randomly")
            ebook_status = re.sub(r'\s\w+.$', '', ebook_status)
            print(ebook_status)

        # if a tweet is very short, this will randomly add a second sentence to it.
        if ebook_status is not None and len(ebook_status) < 40:
            rando = random.randint(0, 10)
            if rando == 0 or rando == 7:
                print("Short tweet. Adding another sentence randomly")
                newer_status = mine.generate_sentence()
                if newer_status is not None:
                    ebook_status += " " + mine.generate_sentence()
                else:
                    ebook_status = ebook_status
            elif rando == 1:
                # say something crazy/prophetic in all caps
                print("ALL THE THINGS")
                ebook_status = ebook_status.upper()

        # throw out tweets that match anything from the source account.
        if ebook_status is not None and len(ebook_status) < 210:
            for status in source_statuses:
                if ebook_status[:-1] not in status:
                    continue
                else:
                    print("TOO SIMILAR: " + ebook_status)
                    sys.exit()

            if not DEBUG:
                if ENABLE_TWITTER_POSTING:
                    status = api.PostUpdate(ebook_status)
                if ENABLE_MASTODON_POSTING:
                    status = mastoapi.toot(ebook_status)
            print(ebook_status)

        elif not ebook_status:
            print("Status is empty, sorry.")
        else:
            print("TOO LONG: " + ebook_status)

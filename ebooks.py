import random
import re
import sys
import twitter
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


def connect():
    return twitter.Api(consumer_key=MY_CONSUMER_KEY,
                       consumer_secret=MY_CONSUMER_SECRET,
                       access_token_key=MY_ACCESS_TOKEN_KEY,
                       access_token_secret=MY_ACCESS_TOKEN_SECRET)


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
        numero = n2c[guess]
        try:
            text = chr(numero)
        except KeyError:
            pass
    return text


def filter_tweet(tweet):
    tweet.text = re.sub(r'\b(RT|MT) .+', '', tweet.text)  # take out anything after RT or MT
    tweet.text = re.sub(r'(\#|@|(h\/t)|(http))\S+', '', tweet.text)  # Take out URLs, hashtags, hts, etc.
    tweet.text = re.sub('\s+', ' ', tweet.text)  # collaspse consecutive whitespace to single spaces.
    tweet.text = re.sub(r'\"|\(|\)', '', tweet.text)  # take out quotes.
    tweet.text = re.sub(r'\s+\(?(via|says)\s@\w+\)?', '', tweet.text)  # remove attribution
    htmlsents = re.findall(r'&\w+;', tweet.text)
    for item in htmlsents:
        tweet.text = tweet.text.replace(item, entity(item))
    tweet.text = re.sub(r'\xe9', 'e', tweet.text)  # take out accented e
    return tweet.text


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
            tweet.text = filter_tweet(tweet)
            if re.search(SOURCE_EXCLUDE, tweet.text):
                continue
            if tweet.text:
                source_tweets.append(tweet.text)
    else:
        pass
    return source_tweets, max_id

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
        source_tweets = []
        if STATIC_TEST:
            file = TEST_SOURCE
            print(">>> Generating from {0}".format(file))
            string_list = open(file).readlines()
            for item in string_list:
                source_tweets += item.split(",")
        if SCRAPE_URL:
            source_tweets += scrape_page(SRC_URL, WEB_CONTEXT, WEB_ATTRIBUTES)
        if SOURCE_ACCOUNTS and len(SOURCE_ACCOUNTS[0]) > 0:
            twitter_tweets = []
            for handle in SOURCE_ACCOUNTS:
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
                    source_tweets += twitter_tweets
        mine = markov.MarkovChainer(order)
        for tweet in source_tweets:
            if not re.search('([\.\!\?\"\']$)', tweet):
                tweet += "."
            mine.add_text(tweet)

        for x in range(0, 10):
            ebook_tweet = mine.generate_sentence()

        # randomly drop the last word, as Horse_ebooks appears to do.
        if random.randint(0, 4) == 0 and re.search(r'(in|to|from|for|with|by|our|of|your|around|under|beyond)\s\w+$', ebook_tweet) is not None:
            print("Losing last word randomly")
            ebook_tweet = re.sub(r'\s\w+.$', '', ebook_tweet)
            print(ebook_tweet)

        # if a tweet is very short, this will randomly add a second sentence to it.
        if ebook_tweet is not None and len(ebook_tweet) < 40:
            rando = random.randint(0, 10)
            if rando == 0 or rando == 7:
                print("Short tweet. Adding another sentence randomly")
                newer_tweet = mine.generate_sentence()
                if newer_tweet is not None:
                    ebook_tweet += " " + mine.generate_sentence()
                else:
                    ebook_tweet = ebook_tweet
            elif rando == 1:
                # say something crazy/prophetic in all caps
                print("ALL THE THINGS")
                ebook_tweet = ebook_tweet.upper()

        # throw out tweets that match anything from the source account.
        if ebook_tweet is not None and len(ebook_tweet) < 110:
            for tweet in source_tweets:
                if ebook_tweet[:-1] not in tweet:
                    continue
                else:
                    print("TOO SIMILAR: " + ebook_tweet)
                    sys.exit()

            if not DEBUG:
                status = api.PostUpdate(ebook_tweet)
                print(status.text.encode('utf-8'))
            else:
                print(ebook_tweet)

        elif not ebook_tweet:
            print("Tweet is empty, sorry.")
        else:
            print("TOO LONG: " + ebook_tweet)

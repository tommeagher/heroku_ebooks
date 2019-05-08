# Heroku_ebooks

This is a basic Python port of [@harrisj's](https://twitter.com/harrisj) [iron_ebooks](https://github.com/harrisj/iron_ebooks/) Ruby script. Using Heroku's scheduler, you can post to an _ebooks Twitter account based on the corpus of an existing Twitter at pseudorandom intervals. Currently, it is the magic behind [@adriennelaf_ebx](http://www.twitter.com/adriennelaf_ebx) and [@stevebuttry_ebx](http://www.twitter.com/stevebuttry_ebx), among many, many others in the wild.

This project should work in the latest releases of Python 2.7 and Python 3. By default, in Heroku, this will be deployed to Python 3.

## Setup

1. Clone this repo
2. If posting to Twitter, create a Twitter account that you will post to.
3. Sign into https://dev.twitter.com/apps with the same login and create an application. Make sure that your application has read and write permissions to make POST requests.
4. Set `ENABLE_TWITTER_SOURCES` and `ENABLE_TWITTER_POSTING` to `True`.  
5. In `local_settings.py`, be sure to add the handle of the Twitter user you want your _ebooks account to be based on. To make your tweets go live, change the `DEBUG` variable to `False`.
6. If you also want to include Mastodon as a source set `ENABLE_MASTODON_SOURCES` to `True` and you'll need to create a Mastodon account to send to on an instance like [botsin.space](https://botsin.space). If you would also like to have the bot post to this account, set `ENABLE_MASTODON_POSTING` to `True`. 
7. After creating the Mastodon account, open a python prompt in your project directory and follow the [directions below](#mastodon-setup). Update your `local_settings.py` file with the filenames of the generated client secret and user credential secret files.
8. Create an account at Heroku, if you don't already have one. [Install the Heroku toolbelt](https://devcenter.heroku.com/articles/quickstart#step-2-install-the-heroku-toolbelt) and set your Heroku login on the command line.
9. Type the command `heroku create` to generate the _ebooks Python app on the platform that you can schedule.
10. The only Python requirements for this script are [python-twitter](https://github.com/bear/python-twitter), Mastodon.py, and BeautfulSoup; the `pip install` of which is handled by Heroku automatically.
11. `git commit -am 'updated the local_settings.py'`
12. `git push heroku master`
13. Before Heroku will properly run your scripts, it will need to have the application keys you created in step 4. We'll configure these as environment variables in Heroku, which will not appear anywhere else in your code (or on Github). Have the consumer key (and secret) and access token (and secret) from your Twiter application ready. At the command line where you just pushed your code to Heroku, type: 
```
heroku config:set TWITTER_CONSUMER_KEY=enter_your_consumer_key_here
heroku config:set TWITTER_CONSUMER_SECRET=enter_your_consumer_secret_here
heroku config:set TWITTER_ACCESS_TOKEN_KEY=enter_your_access_token_here
heroku config:set TWITTER_ACCESS_SECRET=enter_your_access_secret_here
```
Substitute your actual keys after the = sign. Don't include any spaces, and you don't need to wrap them in quotes. To ensure they all got entered correctly, type `heroku config` to see all the environment variables stored for your app. If you see all four keys in there, you're good to go.

14. Now, test your upload by typing `heroku run worker`. You should either get a response that says "3, no, sorry, not this time" or a message with the body of your post. If you get the latter, check your _ebooks Twitter account to see if it worked.
15. Now it's time to configure the scheduler. `heroku addons:create scheduler:standard`
16. Once that runs, type `heroku addons:open scheduler`. This will open up a browser window where you can adjust the time interval for the script to run. The scheduled command should be `python ebooks.py`. I recommend setting it at one hour.
17. Sit back and enjoy the fruits of your labor.

## Configuring

There are several parameters that control the behavior of the bot. You can adjust them by setting them in your `local_settings.py` file.

```
ODDS = 8
```

The bot does not run on every invocation. It runs in a pseudorandom fashion. At the beginning of each time the script fires, `guess = random.choice(range(ODDS))`. If `guess == 0`, then it proceeds. If your `ODDS = 8`, it should run one out of every 8 times, more or less. You can override it to make it more or less frequent. To make it run every time, you can set it to 0.


By default, the bot ignores any tweets with URLs in them because those might just be headlines for articles and not text you've written.

```
ORDER = 2
```

The ORDER variable represents the Markov index, which is a measure of associativity in the generated Markov chains. 2 is generally more incoherent and 3 or 4 is more lucid. I tend to stick with 2.

### Additional sources

This bot was originally designed to pull tweets from a Twitter account, however, it can also process comma-separated text in a text file, or scrape content from the web.

#### Static Text
To use a local text file, set `STATIC_TEST = True` and specify the name of a text file containing comma-separated "tweets" as `TEST_SOURCE`.

#### Web Content
To scrape content from the web, set `SCRAPE_URL` to `True`. This bot makes use of the [`find_all()` method](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all) of Python's BeautfulSoup library. The implementation of this method requires the definition of three inputs in `local_settings.py`.

1. A list of URLs to scrape as `SRC_URL`.
2. A list, `WEB_CONTEXT`, of the [names](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#id11) of the elements to extract from the corresponding URL. This can be "div", "h1" for level-one headings, "a" for links, etc. If you wish to search for more than one name for a single page, repeat the URL in the `SRC_URL` list for as many names as you wish to extract.
3. A list, `WEB_ATTRIBUTES` of dictionaries containing [attributes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#attrs) to filter by. For instance, to limit the search to divs of class "title", one would pass the directory: `{"class": "title"}`. Use an empty dictionary, `{}`, for any page and name for which you don't wish to specify attributes.

__Note:__ Web scraping is experimental and may give you unexpected results. Make sure to test the bot in debugging mode before publishing.

#### Twitter archive
To use tweets from a Twitter account you have access to, you can download your Twitter Archive by following the steps from [Twitter's Help Center](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive).

1. Request your Twitter archive
2. Extract the CSV file and ensure it is named the same as the `TWITTER_ARCHIVE_NAME` in `local_settings.py`
3. In `local_settings.py`, retweets are ignored by default. If you want to include retweets in your corpus, change `IGNORE_RETWEETS` to `False`.
4. Update `TEST_SOURCE` and specify the name of the parsed Twitter archive
5. Once that is all set, run `twittereater.py` and it will automatically create a corpus file based on the `TEST_SOURCE` variable in `local_settings.py`

If you want to use the Twitter corpus to generate tweets, set `STATIC_TEST = True`


## Debugging

If you want to test the script or to debug the tweet generation, you can skip the random number generation and not publish the resulting tweets to Twitter.

First, adjust the `DEBUG` variable in `local_settings.py`.

```
DEBUG = True
```

After that, commit the change and `git push heroku master`. Then run the command `heroku run worker` on the command line and watch what happens.

If you want to avoid hitting the Twitter API and instead want to use a static text file, you can do that. First, create a text file containing a Python list of quote-wrapped tweets. Then set the `STATIC_TEST` variable to `True`. Finally, specify the name of text file using the `TEST_SOURCE` variable in `local_settings.py`

## Mastodon Setup

You only need to do this once!

```python
>>> from mastodon import Mastodon
>>> Mastodon.create_app('pytooterapp', api_base_url='YOUR INSTANCE URL', to_file='YOUR_FILENAME_HERE')
```

Then, create a user credential file. NOTE: Your bot has to follow your source account.

```python
>>> mastodon = Mastodon(client_id='YOUR_FILENAME_HERE', api_base_url='YOUR INSTANCE URL')
>>> mastodon.log_in('yourawesomeemail@whatever.com','incrediblygoodpassword',to_file='YOUR USER FILENAME HERE')
```

Commit those two files to your repository and you can toot away.

## Credit
This is based almost entirely on [@harrisj's](https://twitter.com/harrisj) [iron_ebooks](https://github.com/harrisj/iron_ebooks/). He created it in Ruby, and I wanted to port it to Python. All the credit goes to him. As a result, all of the blame for clunky implementation in Python fall on me.

Many thanks to the [many folks who have contributed](CONTRIBUTORS.md) to the development of this project since it was open sourced in 2013. If you see ways to improve the code, please fork it and send a [pull request](https://github.com/tommeagher/heroku_ebooks/pulls), or [file an issue](https://github.com/tommeagher/heroku_ebooks/issues) for me, and I'll address it.

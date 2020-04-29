import os
import time
import logging
import pandas as pd
from src.data.structure import Downloader, CSSE, Twitter
from datetime import datetime
import tweepy
import GetOldTweets3 as got
import urllib
from bs4 import BeautifulSoup # package for parsing HTML
import pickle
import csv


class CSSEDownloader(CSSE, Downloader):
    def __init__(self, dirname):
        CSSE.__init__(self, dirname)
        Downloader.__init__(self)

        self.dirname = dirname
        self.web_dir = os.path.join(
            "https://raw.githubusercontent.com",
            "CSSEGISandData",
            "COVID-19",
            "master",
            "csse_covid_19_data",
            "csse_covid_19_time_series")

    def fetch_data(self):
        """
        Fetch US time series data.

        Returns
        -------
        data : pd.DataFrame
            CSSE time series data
        """
        data = {}

        self.path_confirmed = os.path.join(self.web_dir, self.fname_confirmed_raw)
        self.path_deaths = os.path.join(self.web_dir, self.fname_deaths_raw)

        data['confirmed'] = pd.read_csv(self.path_confirmed)
        data['deaths'] = pd.read_csv(self.path_deaths)
        return data

    def save_data(self):
        """
        Save CSSE data to ../raw
        """
        logger = logging.getLogger(__name__)
        logger.info('Downloading latest CSSE raw data.')

        # fetch latest data from github repository
        data = self.fetch_data()

        # iterate over dictionary of data frames and save to csv
        for category in data.keys():
            fname = "time_series_covid19_{type}_US.csv".format(type=category)
            data[category].to_csv(os.path.join(self.raw_dir, self.dirname,
                                               'US', fname))
        return None


class TwitterNewsDownloader(Twitter, Downloader):
    def __init__(self, dirname):
        Twitter.__init__(self, dirname)
        Downloader.__init__(self)

        self.dirname = dirname

    def fetch_data(self, usernames):
        """
        Fetch news articles from all users in usernames

        Returns
        -------
        articles : pd.DataFrame
            Time series data of all articles of a specific user - time resolution: one day
        """
        # got through all users
        for user in usernames:
            file = os.path.join(self.raw_dir, self.dirname, user + '.p')

            # If file of user exists start searching for tweets at date where
            # last search ended until today
            if os.path.isfile(file):
                articles = pickle.load(open(file, "rb"))
                last_data = str(max(articles.keys()))

                #Delete data in data to avoid sampling same articles twice
                try:
                    del(articles[max(articles.keys())])
                except:
                    print("Keys not found")

                tweets = self.scrape_twitter(user=user, since=last_data)
                print(tweets[1].id)
                print(tweets[-1].id)

            #If file does not exists yet, search from 1st January 2020 unitl today
            else:
                tweets = self.scrape_twitter(user=user, since="2020-01-01")
                articles = {}

            for tweet_scrape in tweets:

                tweet = self.api.get_status(tweet_scrape.id, tweet_mode='extended')

                a = tweet._json['entities']
                b = a['urls']
                print(b)
                try:
                    c = b[0]
                    url = c['expanded_url']
                    page = urllib.request.urlopen(url)  # open the web page
                    html = page.read()  # read web page contents as a string
                    soup = BeautifulSoup(html, 'html.parser')  # parse html of web page
                    p_class = soup.find_all('p')
                    article = ""
                    for i in p_class:
                        article = article + i.get_text()

                    date_time_str = tweet._json['created_at']
                    date_time_obj = datetime.strptime(date_time_str, '%a %b %d %H:%M:%S %z %Y')
                    date = date_time_obj.date()
                    print(date)
                    articles.setdefault(date, []).append(article)
                except:
                    print("No URL in this Tweet")
                # print(articles)

            # TODO: ideally, fetch_data should return a dict or data frame
            #  of the fetched data. it should then be saved within the save_data
            #  method.
            pickle.dump(articles, open(file, "wb"))

    def scrape_twitter(self, user, since):
        tweets = []
        tweetCriteria = got.manager.TweetCriteria().setUsername(user) \
            .setSince(since) \
            .setUntil(datetime.today().strftime('%Y-%m-%d')) \
            .setEmoji("unicode")

        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        return tweets

    def save_data(self, usernames):
        # TODO: ideally, fetch_data should return a dict or data frame
        #  of the fetched data. it should then be saved within the save_data
        #  method.
        self.fetch_data(usernames)
        print(self.project_dir)


class TwitterUserDownloader(Twitter, Downloader):
    def __init__(self, dirname):
        Twitter.__init__(self, dirname)
        Downloader.__init__(self)

        self.dirname = dirname  # data dir name
        self.fetched_tweets = None  # to store the tweets fetched

    def set_tweet_criteria(self, user, since):
        # GetOldTweets module
        tweet_criteria = got.manager.TweetCriteria().setUsername(user) \
            .setSince(since) \
            .setUntil(datetime.today().strftime('%Y-%m-%d')) \
            .setEmoji("unicode")
        return tweet_criteria

    def fetch_data(self, user_names, start_date="2020-01-01"):
        """Fetch tweets for users"""

        # dict to store tweet df's for all users
        dict_out = {}

        # TODO: here, make sure to write to the disk so that we circumvent
        #  timeouts of the internet connection or any other issues
        for user in user_names:
            # TODO: this could be neatly parallelised to fetch the tweets  of
            #  as many users as cores are available on the machine
            #  simultaneously
            print("User: {}".format(user))
            #fpath = os.path.join(self.raw_dir, self.dirname, 'tweets_users.pkl')

            # If file of user exists start searching for tweets at date where
            # last search ended until today
            # -----------------------------------------------------------------
            # TODO: fix checking if data already exists and if yes, until when
            """
            if os.path.isfile(fpath):
                articles = pickle.load(open(fpath, "rb"))
                last_date = str(max(articles.keys()))

                # Delete data in data to avoid sampling same articles twice
                try:
                    del(articles[max(articles.keys())])
                # TODO: specify concrete error that would be thrown
                except:
                    print("Keys not found")

                # set tweet criteria for scraping
                tweet_criteria = self.set_tweet_criteria(user=user,
                                                         since=last_date)
                tweets = got.manager.TweetManager.getTweets(tweet_criteria)

            # If file does not exists yet, search from start_date until today
            # -----------------------------------------------------------------
            else:
                # set tweet criteria for scraping
                tweet_criteria = self.set_tweet_criteria(user=user,
                                                         since=start_date)
                tweets = got.manager.TweetManager.getTweets(tweet_criteria)
            """

            # set tweet criteria for scraping
            tweet_criteria = self.set_tweet_criteria(user=user,
                                                     since=start_date)
            tweets = got.manager.TweetManager.getTweets(tweet_criteria)
            n_tweets = len(tweets)

            # collect all tweets for one user in a df
            df_user = pd.DataFrame()

            # iterate over tweets
            # tweet_mode='extended' -> contains the entire untruncated text
            # -----------------------------------------------------------------
            print("  retrieving tweets")
            try:
                for n, tweet_scrape in enumerate(tweets):
                    print("    fetching tweet {n} of {nsum} tweets".format(
                        n=n, nsum=n_tweets))
                    # get json via tweepy api
                    tweet = self.api.get_status(tweet_scrape.id,
                                                tweet_mode='extended',
                                                wait_on_rate_limit=True,
                                                timeout=60)  # 60 seconds

                    # 1. Transform the json into a df
                    df_tweet = pd.DataFrame.from_dict(tweet._json,
                                                      orient='index',
                                                      columns=[n])

                    # 2. Concatenate df_tweet to df_out
                    df_user = pd.concat([df_tweet, df_user], axis=1)

            # except if RateLimitError arises
            except tweepy.RateLimitError:
                print("resource usage limit: {} skipped".format(user))
                time.sleep(5 * 60)  # wait a few mins

            # the error arises when the user has protected tweets
            except tweepy.TweepError:
                print("Failed to run the command on user {}".format(user))

            if df_user.empty:
                df_user = None
            else:
                print("  tidying tweet data")
                # transpose
                df_user = df_user.transpose()

                # set index column
                df_user['created_at'] = pd.to_datetime(df_user['created_at'])
                df_user = df_user.set_index('created_at')

                # set optimal dtypes (~ 21% less storage needed)
                for col in df_user.columns:
                    df_user[col] = df_user[col].astype(self.tweet_df_types[col])

            # store data for each user in dict
            dict_out[user] = df_user
        self.fetched_tweets = dict_out
        return self

    def save_data(self, fname='user_tweets.pkl'):
        # fetch tweets
        if self.fetched_tweets is not None:
            fpath = os.path.join(self.raw_dir, self.dirname, fname)
            pickle.dump(self.fetched_tweets, open(fpath, "wb"))
            print("Done! Tweet data was saved to {}".format(fpath))
        else:
            raise IOError("The data that you tried to save"
                          "has not been fetched yet. Run 'fetch_tweets' first.")
        return None


if __name__ == "__main__":
    # CSSE data
    #downloader = CSSEDownloader(dirname="csse")
    #downloader.save_data()

    # twitter news data
    #twitter_downloader = TwitterNewsDownloader(dirname='twitter_news')
    #twitter_downloader.save_data(usernames=['nytime'])
    """
    # twitter user data
    start_time = time.time()
    twitter_user = TwitterUserDownloader(dirname='twitter_news')
    twitter_user.fetch_data(user_names=['realDonaldTrump', 'JoeBiden'],
                            start_date="2020-01-01")

    # save
    twitter_user.save_data(fname='trump_biden_tweets.pkl')
    execution_time = time.time() - start_time
    print('executed in {:.2f} seconds.'.format(execution_time)) 
    # ['realDonaldTrump', 'JoeBiden'] from "2020-01-01" onwards
    # took ~ 27 minutes as of 29.04.2020
    """
    # read the fetched tweets again
    f = "/Users/felix/ETH/code/bdproject/data/" \
        "raw/twitter_news/trump_biden_tweets.pkl"
    tweet_data = pd.read_pickle(f)
    print(type(tweet_data))

    # memory usage in MB
    print("nbytes Trump: {} MB".format(
        tweet_data['realDonaldTrump'].memory_usage().sum() / 1000000))
    print("nbytes Biden: {} MB".format(
        tweet_data['JoeBiden'].memory_usage().sum() / 1000000))

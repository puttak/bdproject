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

        self.dirname = dirname

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

        for user in user_names:
            fpath = os.path.join(self.raw_dir, self.dirname, 'tweets_users.pkl')

            # If file of user exists start searching for tweets at date where
            # last search ended until today
            # -----------------------------------------------------------------
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

            # collect all tweets for one user in a df
            df_user = pd.DataFrame()

            # iterate over tweets
            # tweet_mode='extended' -> contains the entire untruncated text
            # -----------------------------------------------------------------
            print("retrieving tweets")
            try:
                for n, tweet_scrape in enumerate(tweets):
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

            # the error arises when the user has protected tweets
            except tweepy.TweepError:
                print("Failed to run the command on user {}".format(user))

            # except if RateLimitError arises
            except tweepy.RateLimitError:
                print("resource usage limit: {} skipped".format(user))
                time.sleep(5 * 60)  # wait a few mins

            print("cleaning")
            # transpose
            df_user = df_user.transpose()

            # try auto-inferring dtypes to cast columns from dtype
            # "object" to more appropriate and memory-efficient dtypes
            # TODO: not sure if this is really efficient. we might as well
            #  hardcode this step if the structure always stays the same
            df_user = df_user.infer_objects()

            # manually deal with the remaining column dtypes
            df_user['created_at'] = pd.to_datetime(df_user['created_at'])

            # set datetime index
            df_user = df_user.set_index('created_at')
        dict_out[user] = df_user
        self.fetched_tweets = dict_out
        return self

    def save_data(self, fname='user_tweets.pkl'):
        # fetch tweets
        try:
            fpath = os.path.join(self.raw_dir, self.dirname, fname)
            pickle.dump(self.fetched_tweets, open(fpath, "wb"))
            print("Data saved to {}".format(fpath))
        except:
            "The data that you tried to save was not fetched yet."
        return None


if __name__ == "__main__":
    # CSSE data
    #downloader = CSSEDownloader(dirname="csse")
    #downloader.save_data()

    # twitter news data
    #twitter_downloader = TwitterNewsDownloader(dirname='twitter_news')
    #twitter_downloader.save_data(usernames=['nytime'])

    # twitter user data
    twitter_user = TwitterUserDownloader(dirname='twitter_news')
    twitter_user.fetch_data(user_names=['realDonaldTrump'],
                            start_date="2020-04-25")

    # save
    twitter_user.save_data()

    # read again
    data = pd.read_pickle("/Users/felix/ETH/code/bdproject/data"
                          "/raw/twitter_news/user_tweets.pkl")
    print(data)

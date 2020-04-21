import os
import logging
import pandas as pd
from src.data.structure import Downloader, CSSE, TwitterNews
from datetime import datetime
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


class TwitterNewsDownloader(TwitterNews, Downloader):
    def __init__(self, dirname):
        TwitterNews.__init__(self, dirname)
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
        #got through all users
        for user in usernames:
            file=os.path.join(self.raw_dir, self.dirname, user + '.p')

            #If file of user exists start searching for tweets at date where last search ended until today
            if os.path.isfile(file):
                articles=pickle.load( open( file, "rb" ))
                last_data=str(max(articles.keys()))

                #Delete data in data to avoid sampling same articles twice
                try:
                    del(articles[max(articles.keys())])
                except:
                    print("Keys not found")

                tweets=self.scrape_twitter(user=user, since=last_data)
                print(tweets[1].id)
                print(tweets[-1].id)

            #If file does not exists yet, search from 1st January 2020 unitl today
            else:
                tweets=self.scrape_twitter(user=user, since="2020-01-01")
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
        self.fetch_data(usernames)
        print(self.project_dir)


if __name__ == "__main__":
    downloader = CSSEDownloader(dirname="csse")
    downloader.save_data()

    twitter_downloader = TwitterNewsDownloader(dirname='twitter_news')
    twitter_downloader.save_data(usernames=['realDonaldTrump'])

from tweepy import OAuthHandler
import datetime
import sys
import tweepy
import GetOldTweets3 as got
import urllib
from bs4 import BeautifulSoup # package for parsing HTML
import pandas as pd
from configparser import ConfigParser


def log_in():
    # this you get when you make create an application on twitter as a dev
    config = ConfigParser()
    config.read('config.ini')
    # this you get when you make create an application on twitter as a dev
    consumer_key =config.get('AUTH', 'consumer_key')
    consumer_secret =config.get('AUTH', 'consumer_secret')
    access_token =config.get('AUTH', 'access_token')
    access_token_secret =config.get('AUTH', 'access_token_secret')


    auth = OAuthHandler(consumer_key, consumer_secret)  # creating an OAuthHandler instance
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    # test authentication
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
    return api
def scrape_twitter():

    tweets = []
    tweetCriteria = got.manager.TweetCriteria().setUsername("nytimes") \
        .setSince("2020-01-1") \
        .setUntil("2020-01-02") \
        .setEmoji("unicode")
    tweets = got.manager.TweetManager.getTweets(tweetCriteria)
    return tweets

def get_articles(tweets,api):

    articles = {}
    e=0
    for tweet_scrape in tweets:
        e=e+1
        if e<3:
            tweet = api.get_status(tweet_scrape.id,tweet_mode='extended')
            a = tweet._json['entities']
            b = a['urls']
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
            date_time_obj = datetime.datetime.strptime(date_time_str, '%a %b %d %H:%M:%S %z %Y')
            date = date_time_obj.date()

        print(date)
       # articles['Articles'].append(article)
        articles.setdefault(date, []).append(article)
        #print(articles)



    df = pd.DataFrame.from_dict({'Articles': articles})
    df=df
    df.to_csv("./file.csv", sep=',')



def main(args):
    api=log_in()
    tweets=scrape_twitter()
    articles=get_articles(tweets,api)




if __name__ == '__main__':
    main(sys.argv[1:])
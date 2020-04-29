"""
The following basic structures are implemented so far:

    - Data : knows about project and data directories
    - Download : inherits from Data class. knows about web-url of raw data.
                 Must implement fetch and save methods.
    - Reader : inherits from Data class. must implement readers for raw and
               processed data.
    - Transform : inherits from Reader. must implement transformation method
                  to go from raw to processed data.
"""

import os
from src.utils.paths import get_parent_dir
from configparser import ConfigParser
from tweepy import OAuthHandler
import tweepy


class Data(object):
    """
    Implements basic data structure.
    """
    def __init__(self):
        """
        Initialise 3 directories: project, processed and raw.
        Methods that raise a NotImplementedError must be implemented in each
        child class.
        """
        # define names directories
        self.project_dir = get_parent_dir(up=2)
        assert isinstance(self.project_dir, str)

        self.processed_dir = os.path.join(self.project_dir, "data/processed")
        self.raw_dir = os.path.join(self.project_dir, "data/raw")

        # create dirs if they don't exist already
        for data_dir in [self.processed_dir, self.raw_dir]:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)


class Downloader(Data):
    """
    Basic download class. Inherits from Data class. Needs to implement methods
    for fetching and saving data.
    """
    def __init__(self, webdir=""):
        super(Downloader, self).__init__()
        self.web_dir = webdir
        assert isinstance(self.web_dir, str)

    def fetch_data(self, *args):
        raise NotImplementedError

    def save_data(self, *args):
        raise NotImplementedError


class Reader(Data):
    """
    Basic reader class.
    """
    def __init__(self):
        Data.__init__(self)

    def read_raw(self, *args):
        raise NotImplementedError

    def read_processed(self, *args):
        raise NotImplementedError


class Transformer(Reader):
    """
    Basic class for data transformation.
    """
    def __init__(self):
        Reader.__init__(self)

    def raw2processed(self, *args):
        raise NotImplementedError


class CSSE(Data):
    """
    Defines structure of CSSE data for raw and processed stage.
    """
    def __init__(self, dirname):
        """
        Parameters
        ----------
        dirname : str
            Name of the shortcut used for the data sub directories. For example
            "csse" to map to "data/raw/csse" and "data/processed/csse".
        """
        # initialise mother class: now this class inherited the Data class
        super(CSSE, self).__init__()  # alternative: Data.__init__(self)
        self.dirname = dirname

        # define file name structure
        self.fname_confirmed_raw = "time_series_covid19_confirmed_US.csv"
        self.fname_deaths_raw = "time_series_covid19_deaths_US.csv"

        # processed timeseries data
        self.fname_confirmed_processed = \
            "time_series_covid19_confirmed_US_timeseries.csv"
        self.fname_deaths_processed = \
            "time_series_covid19_deaths_US_timeseries.csv"

        # processed ancillary data
        self.fname_confirmed_processed_ancillary = \
            "time_series_covid19_confirmed_US_ancillary.csv"
        self.fname_deaths_processed_ancillary = \
            "time_series_covid19_deaths_US_ancillary.csv"


class Twitter(Data):
    def __init__(self, dirname):
        """
        Initialize class with Tweepy credentials

        Parameters
        ----------
         : str

        """
        # initialise mother class: now this class inherited the Data class
        super(Twitter, self).__init__()
        self.dirname = dirname

        config = ConfigParser()
        config.read(os.path.join(self.project_dir, 'config.ini'))

        #read tokens from config file
        self.__consumer_key = config.get('AUTH', 'consumer_key')
        self.__consumer_secret = config.get('AUTH', 'consumer_secret')
        self.__access_token = config.get('AUTH', 'access_token')
        self.__access_token_secret = config.get('AUTH', 'access_token_secret')

        # creating an OAuthHandler instance
        self.auth = OAuthHandler(self.__consumer_key,
                                 self.__consumer_secret)
        self.auth.set_access_token(self.__access_token,
                                   self.__access_token_secret)
        self.api = tweepy.API(self.auth,
                              wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)

        # ---
        # define data types of the columns in the common df_tweet structure
        # see https://numpy.org/devdocs/user/basics.types.html
        # ---
        # uInt64 vs uint64:
        # uInt64: NaNs are possible (pandas dtype)
        # uint64: Nan are not possible (numpy dtype)
        # ---
        # Note: Use a Categorical for efficient storage of an
        # object-dtype column with many repeated values.
        self.tweet_df_types = {'id': 'uint64',
                               'id_str': 'uint64',
                               'full_text': 'string',
                               'truncated': 'bool',
                               'display_text_range': 'object',
                               'entities': 'object',  # dictionary
                               'source': 'string',
                               'in_reply_to_status_id': 'float32',
                               'in_reply_to_status_id_str': 'string',
                               'in_reply_to_user_id': 'float32',
                               'in_reply_to_user_id_str': 'string',
                               'in_reply_to_screen_name': 'string',
                               'user': 'object',  # dictionary
                               'geo': 'object',  # ?
                               'coordinates': 'object',  # ?
                               'place': 'object',  # ?
                               'contributors': 'object',  # ?
                               'is_quote_status': 'bool',
                               'quoted_status_id': 'float32',
                               'quoted_status_id_str': 'string',
                               'quoted_status_permalink': 'object',
                               'quoted_status': 'object',  # dictionary
                               'retweet_count': 'uint64',
                               'favorite_count': 'uint64',
                               'favorited': 'bool',
                               'retweeted': 'bool',
                               'possibly_sensitive': 'bool',
                               'possibly_sensitive_appealable': 'bool',
                               'lang': 'string',
                               'extended_entities': 'object'}  # dictionary

        # test authentication
        try:
            self.api.verify_credentials()
            print("Twitter Authentication OK")
        except:
            print("Error during authentication")

if __name__ == "__main__":
    c = Twitter(dirname="twitter_news")
    print(c.tweet_df_types)


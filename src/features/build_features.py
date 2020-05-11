import os
import logging
import pickle
import pandas as pd
from src.utils.paths import check_create_dir
from src.features.text import compute_sentiments
from src.data.reader import TwitterReader


class TwitterFeatures(TwitterReader):
    def __init__(self, dirname):
        TwitterReader.__init__(self, dirname)
        self.dirname = dirname

    def calculate_sentiments(self):
        logger = logging.getLogger(__name__)
        reader = TwitterReader(dirname=self.dirname)
        processed_data = reader.read_processed()

        sentiment_data = {}
        col_names = ['neg', 'neu', 'pos', 'compound']
        sentiment_colname = 'sentiments'
        for user_name, user_data in processed_data.items():
            idx = user_data.index

            # yields tuples of ('neg', 'neu', 'pos', 'compound')
            sentiment_scores = user_data['full_text'].apply(compute_sentiments)

            # create df
            df_sentiments = pd.DataFrame(data=sentiment_scores.values,
                                         columns=[sentiment_colname],
                                         index=idx)
            # tuple to multiple columns
            for n, col in enumerate(col_names):
                df_sentiments[col] = df_sentiments[sentiment_colname].apply(
                    lambda sentiments: sentiments[n])

            sentiment_data[user_name] = df_sentiments.drop(sentiment_colname,
                                                           axis=1)
            # TODO - Idea: resample to daily frequency. store 0%, 2.5%, 25%,
            #  50%, 75%, 97.5% and 100% quantiles and the mean
            #  for each of the 4 sentiment scores.

        # save to pkl
        out_dir = os.path.join(self.project_dir, self.processed_dir,
                               "sentiments")
        check_create_dir(out_dir)
        fpath = os.path.join(out_dir, "user_tweets_sentiments.pkl")

        # TODO: check if it is really in append mode
        pickle.dump(sentiment_data, open(fpath, "wb"))
        print("Sentiment data was saved to {}".format(fpath))
        logger.info('Calculating sentiment scores for twitter user data.')
        return None


if __name__ == "__main__":
    features = TwitterFeatures('twitter_user')
    features.calculate_sentiments()

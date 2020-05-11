import os
import time
import logging
from src.utils.paths import get_parent_dir
from src.data.download import CSSEDownloader, TwitterUserDownloader
from src.data.transform import CSSETransformer, TwitterTransformer
from src.features.build_features import TwitterFeatures


def run_pipeline():
    """
    Run all steps. This includes download, processing, transformation,
    feature extraction, model training, prediction and visualization.
    """
    # -------------------------------------------------------------------------
    start_time = time.time()
    logger = logging.getLogger(__name__)
    logger.info('Starting programme pipeline.')
    # -------------------------------------------------------------------------

    # 1) Download latest data
    # -------------------------------------------------------------------------
    # CSSE COVID-19 data
    csse = CSSEDownloader(dirname='csse')
    csse.save_data()

    # Twitter user data
    twitter_user = TwitterUserDownloader(dirname='twitter_user')
    twitter_user.fetch_data(user_names=['realDonaldTrump', 'JoeBiden'],
                            start_date="2020-01-01")
    twitter_user.save_data()

    # 2) transform data
    # -------------------------------------------------------------------------

    # CSSE COVID-19 data
    csse_transformer = CSSETransformer(dirname='csse')
    csse_transformer.raw2processed()
    csse_transformer.processed2ds()

    # Twitter user data
    TwitterTransformer(dirname='twitter_user').raw2processed()

    # 3) extract features
    # -------------------------------------------------------------------------

    # Twitter user data
    features = TwitterFeatures('twitter_user')
    features.calculate_sentiments()


    # -------------------------------------------------------------------------
    execution_time = time.time() - start_time
    execution_stmt = 'Programme pipeline successfully executed in {}.'.format(
        time.strftime('%H:%M:%S', time.gmtime(execution_time)))
    print(execution_stmt)
    logger.info(execution_stmt)
    # -------------------------------------------------------------------------
    return None


if __name__ == "__main__":
    # set logging parameters
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logfile = os.path.join(get_parent_dir(up=2), 'logs', 'pipeline.log')
    logging.basicConfig(level=logging.INFO,
                        format=log_fmt,
                        filename=logfile,
                        filemode='a')

    # execute pipeline
    run_pipeline()

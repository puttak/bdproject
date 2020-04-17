import os
import logging
from src.utils.paths import get_parent_dir
from src.data.download import CSSEDownloader
from src.data.transform import CSSETransformer


def run_pipeline():
    """
    Run all steps. This includes download, processing, transformation,
    feature extraction, model training, prediction and visualization.
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting programme pipeline.')

    # run steps
    # -------------------------------------------------------------------------
    # 1) Download latest data
    CSSEDownloader(dirname='csse').save_data()

    # 2) transform data
    CSSETransformer(dirname='csse').raw2processed()

    # 3) ...

    logger.info('Programme pipeline successfully executed.')
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

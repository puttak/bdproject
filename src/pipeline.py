import os
import logging
from src.utils.paths import get_parent_dir
from src.data import download, transform


def run_pipeline():
    """
    Run all programme steps. This includes download, processing, transformation,
    prediction and visualization.
    """
    logger = logging.getLogger(__name__)
    logger.info('Starting programme pipeline.')

    # run steps
    download.csse_main()
    transform.csse_main()

    logger.info('Programme pipeline executed.')
    return None


if __name__ == "__main__":
    # set logging parameters
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logfile = os.path.join(get_parent_dir(up=2), 'logs', 'pipeline.log')
    logging.basicConfig(level=logging.INFO,
                        format=log_fmt,
                        filename=logfile,
                        filemode='a')

    # run
    run_pipeline()

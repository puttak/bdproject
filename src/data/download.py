import os
import logging
import pandas as pd
from pathlib import Path
from dotenv import find_dotenv, load_dotenv


class CSSEDownloader(object):
    """
    Implements a downloader for the COVID-19 data from John Hopkins University
    CSSE. It can be found here: https://github.com/CSSEGISandData/COVID-19.
    """
    def __init__(self, granularity='US'):
        """
        Initialize class with data granularity.

        Parameters
        ----------
        granularity : str
            Data granularity parameter. One of ["US", "global"].
        """
        # check for valid granularity level
        if granularity not in ['US', 'global']:
            raise FileNotFoundError("Granularity level does not exist. "
                                    "Choose 'US' or 'global'.)")
        self.granularity = granularity
        # define data directory
        self.csse_dir = os.path.join("https://raw.githubusercontent.com",
                                     "CSSEGISandData",
                                     "COVID-19",
                                     "master",
                                     "csse_covid_19_data",
                                     "csse_covid_19_time_series")
        # define time series (ts) file structure
        self.ts_confirmed = \
            os.path.join(self.csse_dir,
                         "time_series_covid19_confirmed_{}.csv".format(
                             granularity))
        self.ts_deaths = \
            os.path.join(self.csse_dir,
                         "time_series_covid19_deaths_{}.csv".format(
                             granularity))
        if granularity == 'global':
            self.ts_recovered = \
                os.path.join(self.csse_dir,
                             "time_series_covid19_recovered_{}.csv".format(
                                 granularity))

    def fetch_ts(self):
        """
        Fetch time series data based on the given granularity level.

        Returns
        -------
        ts_data : pd.DataFrame
            Time series data
        """
        #
        ts_data = {}
        if self.granularity == 'US':
            ts_data['confirmed'] = pd.read_csv(self.ts_confirmed)
            ts_data['deaths'] = pd.read_csv(self.ts_deaths)
        elif self.granularity == 'global':
            ts_data['confirmed'] = pd.read_csv(self.ts_confirmed)
            ts_data['deaths'] = pd.read_csv(self.ts_deaths)
            ts_data['recovered'] = pd.read_csv(self.ts_recovered)
        else:
            raise ImportError("Granularity level does not exist. CSSE time "
                              "series data could not be loaded.")
        return ts_data


def main(project_dir,
         output_dir="data/raw"):
    """
    Downloads latest CSSE time series data into output_dir.

    Parameters
    ----------
    project_dir : str
        Path to project directory of 'bdproject'.
    output_dir : str
        Output directory, ../raw per default.

    Returns
    -------

    """
    # logging
    logger = logging.getLogger(__name__)
    logger.info('Downloading latest CSSE raw data.')

    # TODO: resolve whether to specify project_dir within the main function
    #  or outside.
    # path to project directory "bdproject" (should work for niklas and felix)
    #project_dir = os.path.abspath(os.path.join(
    #    os.path.dirname(os.getcwd()), '..'))

    # download and save files to ../raw
    for granularity_level in ['US', 'global']:
        downloader = CSSEDownloader(granularity=granularity_level)
        data = downloader.fetch_ts()
        # iterate over dictionary of data frames and save to csv
        for key in data.keys():
            fname = \
                "time_series_covid19_" \
                "{type}_{granularity}.csv".format(type=key,
                                                  granularity=granularity_level)
            data[key].to_csv(os.path.join(project_dir,
                                          output_dir,
                                          granularity_level,
                                          fname))

if __name__=="__main__":
    # turn on logging
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find dir of 'bdproject'
    project_dir = Path(__file__).resolve().parents[2]

    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    # run download
    main(project_dir)
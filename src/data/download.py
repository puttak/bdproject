import os
import logging
import pandas as pd
from src.data.structure import Download, CSSE


class CSSEDownloader(CSSE, Download):
    def __init__(self, dirname):
        CSSE.__init__(self, dirname)
        Download.__init__(self)

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

        self.path_confirmed = os.path.join(self.web_dir, self.fname_confirmed)
        self.path_deaths = os.path.join(self.web_dir, self.fname_deaths)

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
            data[category].to_csv(os.path.join(self.raw_dir_csse, 'US', fname))


if __name__ == "__main__":
    downloader = CSSEDownloader(dirname="csse")
    downloader.save_data()

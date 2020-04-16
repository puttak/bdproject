import os
import pandas as pd
import xarray as xr
from src.utils.paths import get_parent_dir
from src.data.structure import Data


class CSSE(Data):
    """
    ...
    """
    def __init__(self, dirname, data_stage, granularity):
        """
        Parameters
        ----------
        dirname : str
            Name of the shortcut used for the data sub directories. For example
            "csse" to map to "data/raw/csse" and "data/processed/csse".
        data_stage
        granularity
        """
        # initialise mother class: now this class inherited the Data class
        super(CSSE, self).__init__()  # same as Data.__init__(self)

        # name must now be implemented
        self.dirname = dirname

        # data can be in either of two stages: raw or processed
        self.data_stage = data_stage
        if self.data_stage not in ['raw', 'processed']:
            raise IOError("Data stage does not exist. Choose one of 'raw',"
                          "'processed'.")

        # there are two granularity levels: US and global
        self.granularity = granularity
        if self.granularity not in ['US', 'global']:
            raise IOError("Granularity level does not exist."
                          "Choose 'US' or 'global'.)")

        # at this stage, re-define dirs based on dirname variable
        self.processed_dir = os.path.join(self.processed_dir, self.dirname)
        self.raw_dir = os.path.join(self.raw_dir, self.dirname)

        # define file name structures based on granularity
        self.fname_confirmed = \
            "time_series_covid19_confirmed_{}.csv".format(self.granularity)
        self.fname_deaths = \
            "time_series_covid19_deaths_{}.csv".format(self.granularity)
        if granularity == 'global':
            self.ts_recovered = \
                "time_series_covid19_recovered_{}.csv".format(self.granularity)


def read_csse2df(path):
    """
    Preliminary reader for CSSE time series data.

    Parameters
    ----------
    path : str
        path to .csv file

    Returns
    -------
    df : pd.DataFrame
        CSSE timeseries data.
            Cols: county FIPS codes
            Rows: time
    """
    df = pd.read_csv(path, index_col=[0])
    df.index = pd.to_datetime(df.index)
    return df


def read_csse2ds(path):
    """
    Read CSSE data to xr.Dataset.

    Parameters
    ----------
    path

    Returns
    -------

    """

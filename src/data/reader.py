import os
import pandas as pd
import xarray as xr
from src.utils.paths import get_parent_dir
from src.data.structure import Reader


class CSSE(Reader):
    def __init__(self, data_stage):
        """
        Parameters
        ----------
        data_stage : str
            one of raw, processed
        """
        Reader.__init__(self)

        # data can be in either of two stages: raw or processed
        self.data_stage = data_stage
        if self.data_stage not in ['raw', 'processed']:
            raise IOError("Data stage does not exist. Choose one of 'raw',"
                          "'processed'.")

    def read_raw(self):
        pass

    def read_processed(self):
        pass

    def read_csse2ds(self):
        pass

    def read_csse2df(self):
        pass


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
        CSSE timeseries data with county FIPS codes as cols.
    """
    df = pd.read_csv(path, index_col=[0])
    df.index = pd.to_datetime(df.index)
    return df

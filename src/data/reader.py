import os
import numpy as np
import pandas as pd
import xarray as xr
from src.data.structure import Reader, CSSE, Twitter


class CSSEReader(CSSE, Reader):
    """"""
    def __init__(self, dirname):
        """"""
        CSSE.__init__(self, dirname)
        Reader.__init__(self)

        self.dirname = dirname

    def read_raw(self, variable="confirmed"):
        """
        Read raw CSSE data.

        Parameters
        ----------
        variable : str
            One of 'confirmed', 'deaths'

        Returns
        -------
        df : pd.DataFrame
            Raw CSSE data.
        """
        # create file path
        if variable == 'confirmed':
            fpath = os.path.join(self.raw_dir, self.dirname, "US",
                                 self.fname_confirmed_raw)
        elif variable == 'deaths':
            fpath = os.path.join(self.raw_dir, self.dirname, "US",
                                 self.fname_deaths_raw)
        else:
            raise IOError("Variable does not exist. Choose one of 'confirmed',"
                          "'deaths'.")
        # read data
        df = pd.read_csv(fpath, index_col=[0])
        return df

    def read_processed(self, variable="confirmed"):
        """
        Read CSSE time series data only.

        Parameters
        ----------
        variable : str
            One of 'confirmed', 'deaths'

        Returns
        -------
        df : pd.DataFrame
            CSSE time series data.
        """
        # create file path
        if variable == 'confirmed':
            fpath = os.path.join(self.processed_dir, self.dirname, "US",
                                 self.fname_confirmed_processed)
        elif variable == 'deaths':
            fpath = os.path.join(self.processed_dir, self.dirname, "US",
                                 self.fname_deaths_processed)
        else:
            raise IOError("Variable does not exist. Choose one of 'confirmed',"
                          "'deaths'.")
        # read data
        df = pd.read_csv(fpath, index_col=[0])
        df.index = pd.to_datetime(df.index)
        df.index.name = 'time'
        return df

    def read_ancillary(self, variable="confirmed"):
        """
        Read CSSE ancillary data only.

        Parameters
        ----------
        variable : str
            One of 'confirmed', 'deaths'

        Returns
        -------
        df : pd.DataFrame
            CSSE ancillary data.
        """
        if variable == 'confirmed':
            fpath = os.path.join(self.processed_dir, self.dirname, "US",
                                 self.fname_confirmed_processed_ancillary)
        elif variable == 'deaths':
            fpath = os.path.join(self.processed_dir, self.dirname, "US",
                                 self.fname_deaths_processed_ancillary)
        else:
            raise IOError("Variable does not exist. Choose one of 'confirmed',"
                          "'deaths'.")
        # read data
        df = pd.read_csv(fpath, index_col=[0])
        return df

    def read_processed_nc(self):
        """
        Read CSSE data to xr.Dataset object.

        Returns
        -------
        CSSE data as xr.Dataset
        """
        fpath = os.path.join(self.processed_dir, self.dirname,
                             "US", "csse_data_merged.nc")
        return xr.open_dataset(fpath, engine='netcdf4')


class TwitterReader(Twitter, Reader):
    def __init__(self, dirname):
        """"""
        Twitter.__init__(self, dirname)
        Reader.__init__(self)

        self.dirname = dirname

    def read_raw(self):
        fpath = os.path.join(self.raw_dir, self.dirname, 'user_tweets.pkl')
        return pd.read_pickle(fpath)

    def read_processed(self):
        fpath = os.path.join(
            self.processed_dir, self.dirname, 'user_tweets.pkl')
        return pd.read_pickle(fpath)

    def read_sentiments(self):
        fpath = os.path.join(
            self.processed_dir, "sentiments", 'user_tweets_sentiments.pkl')
        return pd.read_pickle(fpath)


if __name__ == "__main__":
    reader = TwitterReader(dirname='twitter_user')
    ds = reader.read_sentiments()
    print(ds['JoeBiden'])

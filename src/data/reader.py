import os
import pandas as pd


def read_csse(path):
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
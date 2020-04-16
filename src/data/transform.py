# -*- coding: utf-8 -*-
import os
import logging
import pandas as pd
from src.utils.paths import get_parent_dir
from src.data.structure import Transform


class CSSETransform(Transform):
    def __init__(self):
        super(CSSETransform, self).__init__()
        pass


def csse_main(fpath_in="data/raw/csse", fpath_out="data/processed/csse"):
    """
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('Splitting raw data into time series and ancillary part.')

    # get paths
    project_dir = get_parent_dir(up=2)
    raw_dir = os.path.join(project_dir, fpath_in)

    # iterate over csv files, split into time series and ancillary part and save
    # TODO: extend to global data. could be made nicer by creating a CSSE data
    #  class which stores the default structure.
    for granularity_level in ['US']:
        file_dir = os.path.join(raw_dir, granularity_level)
        # process
        for file in os.listdir(file_dir):
            # read csv
            file_path = os.path.join(file_dir, file)
            ts_raw = pd.read_csv(file_path, infer_datetime_format=True)
            ts_raw = ts_raw.convert_dtypes()

            # drop all cols apart from Province_States and the time series data
            ancillary_cols = ['Unnamed: 0', 'UID', 'iso2', 'iso3', 'code3',
                              'Admin2', 'Country_Region', 'Lat',
                              'Long_', 'Province_State', 'Combined_Key']
            if 'Population' in ts_raw.columns:
                ancillary_cols.append('Population')

            # split into time series and ancillary data per state
            ts_clean = (ts_raw.drop(columns=ancillary_cols)
                        .set_index('FIPS')
                        .transpose())
            # to datetime index
            ts_clean.index = pd.to_datetime(ts_clean.index, format='%m/%d/%y')

            # ancillary data
            ancillary_cols.append('FIPS')
            ancillary_clean = (ts_raw[ancillary_cols]
                               .drop(columns=['Unnamed: 0']))

            # save to csv
            ts_clean.to_csv(
                os.path.join(project_dir, fpath_out, granularity_level,
                             file.split('.')[0] + '_timeseries.csv'))
            ancillary_clean.to_csv(
                os.path.join(project_dir, fpath_out, granularity_level,
                             file.split('.')[0] + '_ancillary.csv'))

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # run main
    csse_main()

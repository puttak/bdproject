# -*- coding: utf-8 -*-
import os
import logging
import pandas as pd
from src.utils.paths import get_parent_dir


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

            # drop all cols apart from Province_States and the time series data
            ancillary_cols = ['Unnamed: 0', 'UID', 'iso2', 'iso3', 'code3',
                              'FIPS', 'Admin2', 'Country_Region', 'Lat',
                              'Long_', 'Province_State']
            if 'Population' in ts_raw.columns:
                ancillary_cols.append('Population')

            # split into time series and ancillary data per state
            ts_clean = (ts_raw.drop(columns=ancillary_cols)
                        .set_index('Combined_Key')
                        .transpose()
                        )
            # to datetime index
            ts_clean.index = pd.to_datetime(ts_clean.index, format='%m/%d/%y')

            # ancillary data
            ancillary_cols.append('Combined_Key')
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

# -*- coding: utf-8 -*-
import os
import logging
import pickle
import numpy as np
import pandas as pd
import xarray as xr
from src.utils.paths import check_create_dir
from src.data.structure import Transformer, CSSE
from src.data.reader import CSSEReader, TwitterReader
from src.features.text import normalize_text, connect_tokens


class CSSETransformer(CSSEReader, Transformer):
    def __init__(self, dirname):
        CSSE.__init__(self, dirname)
        Transformer.__init__(self)
        self.dirname = dirname

    def raw2processed(self):
        """
        Basic transformation of raw data into processed data.

        Returns
        -------
        Two pd.DataFrames for each variable (confirmed cases, deaths). The first
        one stores the timeseries data as indicated by the file name extension
        _timeseries. The second one stores all ancillary information contained
        in the raw data as indicated by the file name extension _ancillary.
        """
        # start logger
        logger = logging.getLogger(__name__)
        logger.info('Splitting raw data into time series and ancillary part.')

        file_dir = os.path.join(self.raw_dir, self.dirname, "US")
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
                os.path.join(self.project_dir, self.processed_dir, self.dirname,
                             "US", file.split('.')[0] + '_timeseries.csv'))
            ancillary_clean.to_csv(
                os.path.join(self.project_dir, self.processed_dir, self.dirname,
                             "US", file.split('.')[0] + '_ancillary.csv'))
        return None

    def processed2nc(self):
        """
        Creates xr.Dataset based on pre-processed time series data. For each
        variable, it stores the time series data as 2D arrays with dimension
        n_times x n_entities. Metadata from the ancillary files is included.

        Requires the package netcdf4 to be installed in order to use the
        netcdf4 engine for saving the file.

        Returns
        -------
        xr.Dataset
            variables: confirmed, deaths
            coords : ['time', 'county']
            dims : ['time', 'county']
        """
        # TODO: add ancillary data (if easily feasible). For once, it would
        #  be great to have the lon/lat data available. Nice for plotting on
        #  a map.
        # start logger
        logger = logging.getLogger(__name__)
        logger.info('Converting transformed data into xr.Dataset object.')

        # read processed time series data
        ts_confirmed = self.read_processed(variable='confirmed')
        ts_deaths = self.read_processed(variable='deaths')

        # clean up suspect "Unnamed" columns so we can convert to numeric types
        # fips codes 3252 und 3148 don't exist
        dfs_clean = {}
        for var, df in zip(['confirmed', 'deaths'], [ts_confirmed, ts_deaths]):
            search = np.array(["Unnamed" in x for x in df.columns.values])

            # drop cols with non-existing county FIPS codes
            df = df.drop(labels=df.columns[search].values, axis=1)

            df.columns = pd.to_numeric(df.columns, downcast='integer')
            df = df[df.columns.sort_values()]
            dfs_clean[var] = df

        # recast cleaned dfs
        ts_confirmed = dfs_clean['confirmed']
        ts_deaths = dfs_clean['deaths']

        # tests
        assert np.alltrue(
            ts_confirmed.columns.values == ts_deaths.columns.values)
        assert np.alltrue(
            ts_confirmed.index == ts_deaths.index)

        # construct xr.Dataset
        times = ts_confirmed.index.values
        locs = ts_confirmed.columns.values
        dims = ['time', 'county']
        data_vars = {'confirmed': (dims, ts_confirmed.values),
                     'deaths': (dims, ts_deaths.values)}
        coords = {'time': times, 'county': locs}
        ds = xr.Dataset(data_vars=data_vars, coords=coords)

        # save to netcdf
        fpath = os.path.join(self.project_dir, self.processed_dir, self.dirname,
                     "US", "csse_data_merged.nc")
        compression = dict(zlib=True, complevel=5)
        encoding = {var: compression for var in ds.data_vars}

        # appending did not work. let's simply delete the file every time
        if os.path.exists(fpath):
            os.remove(fpath)
        ds.to_netcdf(fpath, mode='w', encoding=encoding, engine='netcdf4')


class TwitterTransformer(TwitterReader, Transformer):
    def __init__(self, dirname):
        TwitterReader.__init__(self, dirname)
        Transformer.__init__(self)
        self.dirname = dirname

    def raw2processed(self):
        logger = logging.getLogger(__name__)
        reader = TwitterReader(dirname=self.dirname)
        raw_data = reader.read_raw()

        processed_data = {}
        for user_name, user_data in raw_data.items():
            # copy raw data
            user_data_clean = user_data.copy()

            # overwrite and connect tokens to yield a string separated by
            # whitespace because sentiment analysis requires the whole
            # text strings.
            user_data_clean['full_text'] = (user_data['full_text']
                                            .apply(normalize_text)
                                            .apply(connect_tokens))

            processed_data[user_name] = user_data_clean  # store

        # save to pkl
        out_dir = os.path.join(self.project_dir, self.processed_dir, self.dirname)
        check_create_dir(out_dir)
        fpath = os.path.join(out_dir, "user_tweets.pkl")

        # TODO: check if it is really in append mode
        pickle.dump(processed_data, open(fpath, "wb"))
        print("Transformed data was saved to {}".format(fpath))
        logger.info('Updating twitter user data.')
        return None


if __name__ == '__main__':
    from pprint import pprint
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # run
    CSSETransformer(dirname='csse').processed2nc()

"""
The following basic structures are implemented here:

    - Data : knows about project and data directories
    - Download : inherits from Data class. knows about web-url of raw data.
                 Must implement fetch and save methods.
    - Reader : inherits from Data class. must implement readers for raw and
               processed data.
    - Transform : inherits from Reader. must implement transformation method
                  to go from raw to processed data.
"""

import os
from src.utils.paths import get_parent_dir


class Data(object):
    """
    Implements basic data structure.
    """
    def __init__(self):
        """
        Initialise data name and 3 directories: project, processed and raw.
        Methods that raise a NotImplementedError must be implemented in each
        child class.
        """
        # define names directories
        self.project_dir = get_parent_dir(up=2)
        assert isinstance(self.project_dir, str)
        self.processed_dir = os.path.join(self.project_dir, "data/processed")
        self.raw_dir = os.path.join(self.project_dir, "data/raw")

        # create dirs if they don't exist already
        for data_dir in [self.processed_dir, self.raw_dir]:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)


class Download(Data):
    """
    Basic download class. Inherits from Data class. Needs to implement methods
    for fetching and saving data.
    """
    def __init__(self, webdir):
        super(Download, self).__init__()
        self.webdir = webdir
        assert isinstance(self.webdir, str)

    def fetch_data(self):
        raise NotImplementedError

    def save_data(self):
        raise NotImplementedError


class Reader(Data):
    """
    Basic reader class.
    """
    def __init__(self):
        super(Reader, self).__init__()

    def read_raw(self):
        raise NotImplementedError

    def read_processed(self):
        raise NotImplementedError


class Transform(Reader):
    """
    Basic class for data transformation.
    """
    def __init__(self):
        super(Transform, self).__init__()

    def raw2processed(self):
        raise NotImplementedError


# TODO: delete this class once the code is adapted to the new structure classes
#  the new class is defined in reader.py
class CSSE(object):
    def __init__(self, data_stage, granularity):
        self.data_stage = data_stage
        self.granularity = granularity
        # data can be in either of two stages: raw or processed
        if self.data_stage not in ['raw', 'processed']:
            raise IOError("Data stage does not exist. Choose one of 'raw',"
                          "'processed'.")

        # there are two granularity levels: US and global
        if self.granularity not in ['US', 'global']:
            raise IOError("Granularity level does not exist."
                          "Choose 'US' or 'global'.)")
        # project dir
        self.pdir = get_parent_dir(up=2)

        # directories of raw online data and raw/processed offline data
        self.online_repo = os.path.join("https://raw.githubusercontent.com",
                                        "CSSEGISandData",
                                        "COVID-19",
                                        "master",
                                        "csse_covid_19_data",
                                        "csse_covid_19_time_series")
        self.dir_processed = os.path.join(self.pdir, "data/processed/csse")
        self.dir_raw = os.path.join(self.pdir, "data/raw/csse")

        # define separate file structures based on data_stage
        if self.data_stage == 'raw':
            # define time series (ts) file structure
            self.ts_confirmed = \
                os.path.join(self.online_repo,
                             "time_series_covid19_confirmed_{}.csv".format(
                                 self.granularity))
            self.ts_deaths = \
                os.path.join(self.online_repo,
                             "time_series_covid19_deaths_{}.csv".format(
                                 self.granularity))
            if granularity == 'global':
                self.ts_recovered = \
                    os.path.join(self.online_repo,
                                 "time_series_covid19_recovered_{}.csv".format(
                                     self.granularity))
        # data_stage == 'processed'
        else:
            self.ts_confirmed = \
                os.path.join(self.online_repo,
                             "time_series_covid19_confirmed_{}.csv".format(
                                 self.granularity))

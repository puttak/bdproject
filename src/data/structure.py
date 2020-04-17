"""
The following basic structures are implemented so far:

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
        Initialise 3 directories: project, processed and raw.
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


class Downloader(Data):
    """
    Basic download class. Inherits from Data class. Needs to implement methods
    for fetching and saving data.
    """
    def __init__(self, webdir=""):
        super(Downloader, self).__init__()
        self.web_dir = webdir
        assert isinstance(self.web_dir, str)

    def fetch_data(self):
        raise NotImplementedError

    def save_data(self):
        raise NotImplementedError


class Reader(Data):
    """
    Basic reader class.
    """
    def __init__(self):
        Data.__init__(self)

    def read_raw(self):
        raise NotImplementedError

    def read_processed(self):
        raise NotImplementedError


class Transformer(Reader):
    """
    Basic class for data transformation.
    """
    def __init__(self):
        Reader.__init__(self)

    def raw2processed(self):
        raise NotImplementedError


class CSSE(Data):
    """
    Defines structure of CSSE data for raw and processed stage.
    """
    def __init__(self, dirname):
        """
        Parameters
        ----------
        dirname : str
            Name of the shortcut used for the data sub directories. For example
            "csse" to map to "data/raw/csse" and "data/processed/csse".
        """
        # initialise mother class: now this class inherited the Data class
        super(CSSE, self).__init__()  # alternative: Data.__init__(self)
        self.dirname = dirname

        # at this stage, re-define dirs based on dirname variable
        self.processed_dir_csse = os.path.join(self.processed_dir, self.dirname)
        self.raw_dir_csse = os.path.join(self.raw_dir, self.dirname)

        # define file name structure
        self.fname_confirmed = "time_series_covid19_confirmed_US.csv"
        self.fname_deaths = "time_series_covid19_deaths_US.csv"

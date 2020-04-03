from pathlib import Path


def get_parent_dir(up=1):
    """
    Get the directory path x steps upwards in the hierarchy.

    Parameters
    ----------
    up : int
        How many directories to go up.

    Returns
    -------
    path : str
        Path to directory.
    """
    return Path(__file__).resolve().parents[up]

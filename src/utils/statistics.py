import numpy as np
import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr


def kendall_pval(x, y):
    return kendalltau(x, y)[1]


def pearsonr_pval(x, y):
    return pearsonr(x, y)[1]


def spearmanr_pval(x, y):
    return spearmanr(x, y)[1]


def correlation_matrix(df):
    """
    Given a pd.DataFrame, calculate Pearson's R
    and the p-values of the correlation.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing numeric values.
    Returns
    -------
    (correlations, p_values) : tuple
        Tuple of dataframes.
    """
    df = df.dropna()._get_numeric_data()
    cols = pd.DataFrame(columns=df.columns)

    correlations = cols.transpose().join(cols, how='outer')
    p_values = cols.transpose().join(cols, how='outer')

    for r in df.columns:
        for c in df.columns:
            # pearsonr returns a tuple like (corr, pval)
            correlations[r][c] = round(pearsonr(df[r], df[c])[0], 4)
            p_values[r][c] = round(pearsonr(df[r], df[c])[1], 4)

    return (correlations.apply(pd.to_numeric),
            p_values.apply(pd.to_numeric))


def lag_features(df, n_lags=1):
    df_lagged = df.copy()

    for lag in range(1, n_lags + 1):
        shifted = df.shift(lag)
        shifted.columns = [x + "_lag" + str(lag) for x in df.columns]

        df_lagged = pd.concat((df_lagged, shifted), axis=1)
    return df_lagged


def calc_lagmeans(s, lags):
    """
    Calculates for each observation the mean of the previous x months, for each
    x in lags Assumes that the input series has evenly spaced temporal intervals

    :param s: pandas.Series
        Time series of which to calculate lag avarages of.
    :param lags: list
        list of lags for which to calculate the average for.
    :return: pandas.Dataframe
        data frame with a column for each lag
        The columns are padded at the beginning such that they
        all have the length of the input series
    """
    csum = s.cumsum().values
    csum = np.insert(csum, 0, 0)
    out_df = pd.DataFrame(index=s.index)
    for lag in lags:
        lagsum = csum[lag:] - csum[:-lag]
        lagsum = np.insert(lagsum, 0, np.nan * np.ones(lag-1))
        out_df['lagmean_' + str(lag)] = lagsum/lag
    return out_df
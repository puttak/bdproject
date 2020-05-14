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
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.utils.statistics import correlation_matrix
sns.set(style="white")


def correlation_matrix_plot(df, significance_level=0.05, cbar_levels=8,
                            figsize=(6,6)):
    """Plot corrmat considering p-vals."""
    corr, pvals = correlation_matrix(df)

    # create triangular mask for heatmap
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True

    # mask corrs based on p-values
    pvals_plot = np.where(pvals > significance_level, np.nan, corr)

    # plot
    # -------------------------------------------------------------------------
    # define correct cbar height and pass to sns.heatmap function
    fig, ax = plt.subplots(figsize=figsize)
    cbar_kws = {"fraction": 0.046, "pad": 0.04}
    sns.heatmap(corr,
                mask=mask,
                cmap=sns.diverging_palette(20, 220, n=cbar_levels),
                square=True,
                vmin=-1,
                center=0,
                vmax=1,
                annot=pvals_plot,
                cbar_kws=cbar_kws)
    plt.title("p < {:.2f}".format(significance_level))
    plt.tight_layout()
    return fig, ax

if __name__ == "__main__":
    # read data
    data = pd.read_csv('https://raw.githubusercontent.com/'
                       'drazenz/heatmap/master/autos.clean.csv')

    # subset
    columns = ['bore', 'stroke', 'compression-ratio', 'horsepower', 'city-mpg',
               'price']

    # plot heatmap
    correlation_matrix_plot(data[columns], significance_level=0.05)

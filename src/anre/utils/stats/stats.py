# mypy: disable-error-code="assignment"
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as spStats
from sklearn import metrics
from sklearn.neighbors import KNeighborsRegressor
from statsmodels.tsa.stattools import acf


def get_gaussianKdeSr(x: np.ndarray | pd.Series, n: int = 1000, bwAdjust: float = 1.0) -> pd.Series:
    if isinstance(x, np.ndarray):
        pass
    elif isinstance(x, pd.Series):
        x = x.values
    else:
        raise NotImplementedError

    kernel = spStats.gaussian_kde(x)
    kernel.set_bandwidth(kernel.factor * bwAdjust)

    positions = np.linspace(np.min(x), np.max(x), n)
    kdeSr = pd.Series(kernel(positions), index=positions)
    return kdeSr


def plot_ROC_curve(yTrue, yScore, positiveLabel, ax=None):
    fpr, tpr, tr = metrics.roc_curve(y_true=yTrue, y_score=yScore, pos_label=positiveLabel)
    score = metrics.auc(fpr, tpr)

    if ax is None:
        fig, ax = plt.subplots()

    ax.plot(fpr, tpr, color='darkorange', label='ROC')
    ax.plot([0, 1], [0, 1], color='navy', linestyle='--')
    ax.set_xlim([-0.01, 1.01])
    ax.set_ylim([-0.01, 1.01])
    ax.set_title('ROC curve (area = %0.3f)' % score)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    return ax


def get_meanAndStdDf_viaKnn(X, y, newX, nNeighbors) -> pd.DataFrame:
    """Get mean and std of y around newX

    returns pd.DataFrame with columns ['mean', 'std']

    """

    assert isinstance(X, np.ndarray)

    neigh = KNeighborsRegressor(n_neighbors=nNeighbors)
    neigh.fit(X, y)
    kneighborsIdxArr = neigh.kneighbors(newX, return_distance=False)

    def get_predWithStd(values):
        return {'mean': np.mean(values), 'std': np.std(values)}

    meanAndStdDf = pd.DataFrame.from_records([get_predWithStd(y[idx]) for idx in kneighborsIdxArr])
    return meanAndStdDf


def _get_effective_sample_size_ar1(count: int, autocorrelation: float) -> float:
    # https://ljmartin.github.io/technical-notes/stats/estimators-autocorrelated/
    assert -1 <= autocorrelation <= 1, (
        f'Autocorrelation must be in [-1, 1], but got {autocorrelation}'
    )
    assert count >= 2
    if abs(autocorrelation) == 1:
        return 0
    delta = (
        (count - 1) * autocorrelation - count * autocorrelation**2 + autocorrelation ** (count + 1)
    ) / (1 - autocorrelation) ** 2
    correction_div = (1 + 2 * delta / count) / (1 - 2 * delta / (count * (count - 1)))
    effective_sample_size = count / correction_div
    return effective_sample_size


def _get_effective_sample_size_from_multi(
    count: int, autocorrelations: np.ndarray | pd.Series
) -> float:
    # See: https://journals.pan.pl/Content/107037/PDF/Journal10178-VolumeXVII%20Issue1_01%20paper.pdf
    assert count > 0
    assert isinstance(autocorrelations, (np.ndarray, pd.Series))
    k = len(autocorrelations)
    assert k > 0
    assert count > k
    if autocorrelations[0] == 1:
        warnings.warn('autocorr[0] == 1, is It OK?')
    correction_div = (
        1 + 2 * np.sum(np.arange(count - 1, count - 1 - k, -1) * autocorrelations) / count
    )
    # correction_div = (1 + 2 * np.sum(autocorrelations))
    effective_sample_size = count / correction_div
    return effective_sample_size


def get_effective_sample_size(x: pd.Series | np.ndarray, method: str = 'ar1', nlags: int = 1):
    if isinstance(x, np.ndarray):
        x = pd.Series(x)
    count = len(x)
    assert count > nlags > 0
    if method == 'ar1':
        assert nlags == 1, 'nlags must be 1 for AR(1)'
        if x.nunique() > 1:
            autocorrelation = x.corr(x.shift(1))
            if np.isfinite(autocorrelation):
                effective_sample_size = _get_effective_sample_size_ar1(
                    count=count, autocorrelation=autocorrelation
                )
            else:
                effective_sample_size = count
        else:
            effective_sample_size = count

    elif method == 'multi':
        autocorrelations = acf(x, fft=True, nlags=nlags)[1:]
        effective_sample_size = _get_effective_sample_size_from_multi(
            count=count, autocorrelations=autocorrelations
        )
    else:
        raise ValueError(f'Unknown method: {method}')
    return effective_sample_size


def get_mean_estimates_adjusted_by_autocorrelation(x: pd.Series) -> pd.Series:
    assert isinstance(x, pd.Series)
    count = x.shape[0]
    if count >= 2:
        effective_sample_size = get_effective_sample_size(x=x, method='ar1')
        mean = x.mean()
        obs_std = x.std()
        if obs_std > 0:
            mean_se = obs_std / effective_sample_size**0.5
            tstat = mean / mean_se
        else:
            mean_se = 0
            tstat = 0

    else:
        mean = np.nan
        obs_std = np.nan
        mean_se = np.nan
        tstat = np.nan
        effective_sample_size = np.nan

    return pd.Series({
        'mean': mean,
        'obs_std': obs_std,
        'mean_se': mean_se,
        'count': count,
        'effective_sample_size': effective_sample_size,
        'tstat': tstat,
    })

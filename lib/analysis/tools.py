def block_array(arr, block_length):
    import numpy as np

    if not isinstance(arr, np.ndarray):
        raise ValueError('block_array: np.ndarray needed as input.')

    q, r = divmod(arr.shape[0], block_length)

    if q == 0:
        raise ValueError("'block' too big")

    if r == 0:
        return arr.reshape(q, -1, *arr.shape[1:])
    else:
        return arr[:-r].reshape(q, -1, *arr.shape[1:])

def bootstrap(sample, n_trials=1e6):
    """
    Parameters
    ----------
    sample : 1-D array-like or int
        original sample
    n_trials : int or float, optional
        number of extractions

    Returns
    -------
    mean : float
        resampled mean
    std : float
        resampled standard deviation
    """
    import numpy as np

    n_trials = int(n_trials)

    if n_trials < len(sample):
        print('Warning, few ')

    re_sample = np.random.choice(sample, n_trials)

    mean = np.mean(re_sample)
    std = np.std(re_sample)

    return np.array([mean, std])

def decay(t, t_corr, A):
    from numpy import cosh

    # return (cosh(t / t_corr) - b) / (cosh(1. / t_corr) - b)
    return A*(cosh(t / t_corr) - cosh(1. / t_corr)) + 1.

def divergence(l, l_c, alpha, A):
    return A * (l - l_c)**(-alpha)

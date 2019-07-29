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

def blocked_bootstrap(sample, n_new_samples=1e3, len_new_sample=None):
    """
    Parameters
    ----------
    sample : 2-D array-like
        original sample, (also n-D with n > 2 is supported, only the first two
        dimensions are used, the other are preserved).
    n_trials : int or float, optional
        number of extractions

    Returns
    -------
    re_sample : 2-D array-like
        resampled array with bootstrap
    """
    import numpy as np

    len_samp = len_new_sample if len_new_sample else len(sample)
    n_samp = int(n_new_samples)

    if n_samp < len(sample):
        print('Warning, few sample requested for resampling.')

    # first extract randomly blocks' ids
    blocks_extr = np.random.randint(len(sample), size=(n_samp, len_samp))

    # than use blocks' ids to get actual blocks
    re_sample_blocked = sample[blocks_extr]

    # eventually flattened along block axis
    s = sample.shape
    re_sample = re_sample_blocked.reshape(n_samp, len_samp * s[1], *s[2:])

    return re_sample

def blocked_bootstrap_gen(sample, n_new_samples=1e3, len_new_sample=None):
    """
    Parameters
    ----------
    sample : 2-D array-like
        original sample, (also n-D with n > 2 is supported, only the first two
        dimensions are used, the other are preserved).
    n_trials : int or float, optional
        number of extractions

    Returns
    -------
    re_sample : 2-D array-like
        resampled array with bootstrap
    """
    import numpy as np

    len_samp = len_new_sample if len_new_sample else len(sample)
    n_samp = int(n_new_samples)

    if n_samp < len(sample):
        print('Warning, few sample requested for resampling.')

    # first extract randomly blocks' ids
    blocks_extr = np.random.randint(len(sample), size=(n_samp, len_samp))

    for sample_blocks in blocks_extr:
        # than use blocks' ids to get actual blocks
        re_sample_blocked = sample[sample_blocks]

        # eventually flattened along block axis
        s = sample.shape
        re_sample = re_sample_blocked.reshape(len_samp * s[1], *s[2:])

        yield re_sample

    return

def decay(t, t_corr, A):
    from numpy import cosh

    # return (cosh(t / t_corr) - b) / (cosh(1. / t_corr) - b)
    return A*(cosh(t / t_corr) - cosh(1. / t_corr)) + 1.

def divergence(l, l_c, alpha, A):
    return A * (l - l_c)**(-alpha)

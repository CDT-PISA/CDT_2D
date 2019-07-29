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

def blocked_bootstrap(raw_sample, block_size,
                      n_new_samples=1e3, len_new_sample=None):
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

    sample = block_array(raw_sample, block_size)

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

def blocked_bootstrap_gen(raw_sample, block_size,
                          n_new_samples=1e3, len_new_sample=None):
    """
    Parameters
    ----------
    sample : 1-D array-like
        original sample, (also n-D with n > q is supported, only the first
        dimensions is used, the other are preserved).
    n_trials : int or float, optional
        number of extractions

    Returns
    -------
    re_sample : 2-D array-like
        resampled array with bootstrap
    """
    import numpy as np

    sample = block_array(raw_sample, block_size)

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

def get_time_corr(profiles):
    """
    Parameters
    ----------
    profiles : 2-D array-like
        sample of profiles

    Returns
    -------
    profiles_corr : 1-D array-like
        profiles time correlation
    """
    import numpy as np

    # 's' is the index over samples
    # 'i' is the index over the ensemble
    # 't' is the index over physical times
    # 'k' is the index over time-shifts, Δt

    # too hard for memory, extimated 128GB of memory needed (use case)
    #
    # # print(profiles_blocked.shape)
    # # <<V_t V_(t+Δt)>>_t
    # profiles_shift = np.array([np.roll(profiles_resampled, Δt, axis=2)
    #                          for Δt in range(0, profiles.shape[1] + 1)])
    # profiles_cov = np.einsum('ksit,sit->sk', profiles_shift,
    #                          profiles_resampled) / profiles_resampled[0].size
    # # last division realizes the averages <> and <>_t, because 'np.einsum' is
    # # doing only the sum
    #
    # # <<V_t>**2>_t : before the mean over the ensemble 'sit->st', at the end
    # # the mean over times 'st->s'
    # profiles_mean_sq = (profiles_resampled.mean(axis=1)**2).mean(axis=1)
    #
    # # '(sk->ks),s->ks'
    # profiles_corr_pre = profiles_cov.transpose() - profiles_mean_sq
    # # '(sit->s),s->s'
    # profiles_var = (profiles_resampled**2).mean(axis=(1,2)) - profiles_mean_sq
    # # 'ks,s->ks'
    # profiles_corr = profiles_corr_pre / profiles_var
    #
    # # 'ks->k'
    # profiles_corr_mean = profiles_corr.mean(axis=1)
    # profiles_corr_std = profiles_corr.std(axis=1)

    # redo all without s index, so for a single sample

    # print(profiles.shape, flush=True)
    Δts = np.arange(profiles.shape[1] + 1)
    profiles_corr = []
    for Δt in Δts:
        profiles_shift = np.roll(profiles, Δt, axis=1)
        profiles_cov = np.abs( np.einsum('it,it->', profiles_shift,
                          np.conj(profiles)) ) / profiles.size
        # last division realizes the averages <> and <>_t, because 'np.einsum'
        # is doing only the sum

        # <<V_t>**2>_t : before the mean over the ensemble 'it->t', at the
        # end the mean over times 't->'
        profiles_mean_sq = (np.abs(profiles.mean(axis=0)**2)).mean()

        # 'k,->k'
        profiles_corr_pre = profiles_cov - profiles_mean_sq
        # '(it->),->'
        profiles_var = (np.abs(profiles**2)).mean() - profiles_mean_sq
        # 'k,->k'
        profiles_corr += [profiles_corr_pre / profiles_var]

    profiles_corr = np.array(profiles_corr)

    return profiles_corr

def decay(t, t_corr, A):
    from numpy import cosh

    # return (cosh(t / t_corr) - b) / (cosh(1. / t_corr) - b)
    return A*(cosh(t / t_corr) - cosh(1. / t_corr)) + 1.

def divergence(l, l_c, alpha, A):
    return A * (l - l_c)**(-alpha)

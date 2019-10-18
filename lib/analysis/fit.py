def select_from_plot(Point, indices, values, i=0, dot=None, proj_axis='x',
                     block=False):
    from matplotlib.pyplot import figure, show, figtext, close
    from lib.utils import point_str

    imin = min(indices)
    imax = max(indices)
    vmin = min(values)
    vmax = max(values)

    color_cycle = ['xkcd:carmine', 'xkcd:teal', 'xkcd:peach', 'xkcd:mustard',
                   'xkcd:cerulean']

    n_col = len(color_cycle)

    fig = figure()
    ax = fig.add_subplot(111)
    canvas = fig.canvas

    fig.set_size_inches(7, 5)
    ax.plot(indices, values, color=color_cycle[i % n_col])
    ax.set_title('λ = ' + point_str(Point))
    figtext(.5,.03,' '*10 +
            'press enter to convalid current selection', ha='center')
    if block:
        ax.set_ylim(0, vmax*1.1)
    if not dot == None:
        ax.plot(*dot, 'o', mec='w')

    fig.canvas.draw()

    def on_press(event):
        on_press.p = True
    on_press.p = False

    def on_click(event):
        on_press.p = False
        if event.inaxes is not None:
            x = event.xdata
            y = event.ydata

            vmax_ = vmax*1.1 if block else vmax
            inarea = x > imin and x < imax and y > vmin and y < vmax_
            if inarea and not on_motion.drag:
                on_click.x = x
                on_click.y = y
                if on_click.i > 0:
                    on_click.m[0].remove()
                on_click.m = ax.plot(x, y, 'o', mec='w')
                event.canvas.draw()
                on_click.i += 1
        on_motion.drag = False
    on_click.i = 0
    on_click.m = None
    on_click.x = None
    on_click.y = None

    def on_motion(event):
        if on_press.p == True:
            on_motion.drag = True
            hide_drag = not event.canvas.manager.toolbar._active == None
        else:
            hide_drag = False
        if event.inaxes is not None and not hide_drag:
            x = event.xdata
            y = event.ydata

            vmax_ = vmax*1.1 if block else vmax
            inarea = x > imin and x < imax and y > vmin and y < vmax_
            if inarea:
                m = ax.plot(x, y, 'wo', mec='k')
                if 'x' in proj_axis:
                    n = ax.plot(x, vmin, 'k|', ms=20)
                if 'y' in proj_axis:
                    o = ax.plot(imin, y, 'k_', ms=20)
                event.canvas.draw()
                m[0].remove()
                if 'x' in proj_axis:
                    n[0].remove()
                if 'y' in proj_axis:
                    o[0].remove()
        else:
            event.canvas.draw()
    on_motion.drag = False

    def on_key(event):
        if event.key == 'enter':
            close()
            if on_click.x == None:
                on_click.x = -1
        if event.key == 'q':
            on_click.x = None
            on_click.y = None
            close()


    canvas.mpl_connect('button_press_event', on_press)
    canvas.mpl_connect('button_release_event', on_click)
    canvas.mpl_connect('motion_notify_event', on_motion)
    canvas.mpl_connect('key_press_event', on_key)
    show()

    return on_click.x, on_click.y

def set_cut(p_dir, i=0, force=False):
    from os import chdir
    from os.path import basename
    from math import ceil
    from numpy import loadtxt
    from pandas import read_csv
    from lib.utils import dir_point

    chdir(p_dir)
    Point = dir_point(basename(p_dir))

    vol_file = 'history/volumes.txt'
    indices, volumes = read_csv(vol_file, sep=' ').values[:,:2].transpose()

    if force:
        index = indices[-1] * 0.2
    else:
        index, _ = select_from_plot(Point, indices, volumes, i)

    if index:
        return ceil(index)
    else:
        return index

def blocked_mean_std(indices, volumes, block_size):
    from numpy import mean, std
    from math import sqrt

    bs = block_size
    buffer_start = indices[0]
    buffer = []
    block_means = []
    for i in range(0,len(indices)):
        if (indices[i] - buffer_start) > bs:
            block_means += [mean(buffer)]
            buffer = []
            buffer_start = indices[i]
        buffer += [volumes[i]]

    vol = mean(block_means)
    err = std(block_means) / sqrt(len(block_means) - 1)

    return vol, err

def set_block(p_dir, i=0, force=False):
    from os import chdir
    from os.path import basename
    from math import log
    import json
    import numpy as np
    from pandas import read_csv
    from lib.utils import dir_point

    chdir(p_dir)
    Point = dir_point(basename(p_dir))

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    if not cut:
        print("No 'cut' found, so it's not possible to go on with the 'block'.")
        return None

    vol_file = 'history/volumes.txt'
    indices, volumes = read_csv(vol_file, sep=' ').values[:,:2].transpose()
    imax = indices[-1]

    volumes_cut = volumes[indices > cut]
    indices_cut = indices[indices > cut]

    # if volumes_cut.std() < 1e-5:
    #     # use gauge-action as a pseudo-volume if volume is fixed
    #     vol_file = 'history/gauge.txt'
    #     indices, volumes = read_csv(vol_file, sep=' ').values[:,:2].transpose()
    #     imax = indices[-1]
    #
    #     volumes_cut = volumes[indices > cut]
    #     indices_cut = indices[indices > cut]

    ratio = 1.3
    block_sizes = [ratio**k for k in
                   range(15, int(log(imax - cut, ratio)) - 12)]
    stdevs = []
    for bs in block_sizes:
        _, stdev = blocked_mean_std(indices_cut, volumes_cut, bs)
        stdevs += [stdev]

    if force:
        block = block_sizes[np.array(stdevs).argmax()]
    else:
        block, _ = select_from_plot(Point, block_sizes, stdevs, i,
                                    proj_axis='xy', block=True)
    if block == None or block == -1:
        print('Nothing done.')
        return None
    block = int(block)

    return block

def eval_volume(p_dir):
    from os import chdir, getcwd
    import json
    from numpy import loadtxt

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    vol_file = 'history/volumes.txt'
    indices, volumes = loadtxt(vol_file, unpack=True)

    volumes_cut = volumes[indices > cut]
    indices_cut = indices[indices > cut]

    vol, err = blocked_mean_std(indices_cut, volumes_cut, block)

    chdir(cwd)

    print('\033[93mvolume:\033[0m {:.4} ± {:.3}'.format(vol, err))

    return vol, err

def eval_action(p_dir):
    from os import chdir, getcwd
    import json
    import numpy as np

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    vol_file = 'history/volumes.txt'
    v_indices, volumes = np.loadtxt(vol_file, unpack=True)
    gauge_file = 'history/gauge.txt'
    g_indices, g_action, _, _ = np.loadtxt(gauge_file, unpack=True)

    indices_cut = g_indices[g_indices > cut]
    volumes_cut = volumes[np.searchsorted(v_indices, indices_cut)]
    g_action_cut = g_action[g_indices > cut]

    g_action_cut = g_action_cut
    g_action, err = blocked_mean_std(indices_cut, g_action_cut, block)

    chdir(cwd)

    print('\033[93mgauge action:\033[0m '
          '{:.4} ± {:.3}'.format(g_action, err))

    return g_action, err

def eval_action_density(p_dir):
    from os import chdir, getcwd
    import json
    import numpy as np

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    vol_file = 'history/volumes.txt'
    v_indices, volumes = np.loadtxt(vol_file, unpack=True)
    gauge_file = 'history/gauge.txt'
    g_indices, g_action, _, _ = np.loadtxt(gauge_file, unpack=True)

    indices_cut = g_indices[g_indices > cut]
    volumes_cut = volumes[np.searchsorted(v_indices, indices_cut)]
    g_action_cut = g_action[g_indices > cut]

    g_density_cut = g_action_cut / volumes_cut
    g_density, err = blocked_mean_std(indices_cut, g_density_cut, block)

    chdir(cwd)

    print('\033[93mgauge action density:\033[0m '
          '{:.4} ± {:.3}'.format(g_density, err))

    return g_density, err

def eval_top_susc(p_dir, type=1, force=False):
    from os import chdir, getcwd
    import json
    import numpy as np

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    vol_file = 'history/volumes.txt'
    v_indices, volumes = np.loadtxt(vol_file, unpack=True)
    gauge_file = 'history/gauge.txt'
    g_indices, _, top_ch, _ = np.loadtxt(gauge_file, unpack=True)

    indices_cut = g_indices[g_indices > cut]
    volumes_cut = volumes[np.searchsorted(v_indices, indices_cut)]
    top_ch_cut = top_ch[g_indices > cut]

    if type == 1:
        top_susc_cut = top_ch_cut**2 / volumes_cut

        top_susc, err = blocked_mean_std(indices_cut, top_susc_cut, block)
    if type == 2:
        from lib.analysis.tools import blocked_bootstrap_gen
        try:
            import progressbar
            pbar = True
        except ModuleNotFoundError:
            pbar = False

        top_2 = np.array([top_ch_cut**2 / volumes_cut**2, volumes_cut]).T
        index_block = len(indices_cut[indices_cut < indices_cut[0] + block])

        top_2_resampled = blocked_bootstrap_gen(top_2, index_block)
        top_susc_l = []

        if pbar:
            with progressbar.ProgressBar(max_value=1000) as bar:
                i = 0
                for sample in top_2_resampled:
                    sample = sample.T
                    sample_top_susc = sample[0] * sample[1]
                    top_susc_l += [sample_top_susc]
                    if not force:
                        bar.update(i)
                    i += 1
        else:
            for sample in top_2_resampled:
                sample = sample.T
                sample_top_susc = sample[0] * sample[1]
                top_susc_l += [sample_top_susc]

        top_susc_a = np.array(top_susc_l)
        top_susc, err = top_susc_a.mean(), top_susc_a.std()

    chdir(cwd)

    print('\033[93mtopological susceptibility:\033[0m '
          '{:.4} ± {:.3}'.format(top_susc, err))

    return top_susc, err

def compute_torelons(p_dir, plot, fit, force=False):
    from os import chdir, getcwd
    import json
    import numpy as np
    from matplotlib import pyplot as plt
    from lib.analysis.tools import blocked_bootstrap_gen, get_time_corr

    try:
        import progressbar
        pbar = True
    except ModuleNotFoundError:
        pbar = False

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    def load_toblerone(file,**genfromtext_args):
         """
         Load torelons' complex data in the C++ format in numpy.
         """

         array_as_strings = np.genfromtxt(file,dtype=str,**genfromtext_args)
         float_parser = np.vectorize(lambda x: float(x))
         complex_parser = np.vectorize(lambda x: complex(*eval(x)))

         indices = float_parser(array_as_strings[:,0])
         torelons = complex_parser(array_as_strings[:,1:])
         return indices, torelons

    try:
        toblerone = 'history/toblerone.txt'
        indices, torelons = load_toblerone(toblerone)
    except Exception:
        print('Old format torelon.')
        return None

    torelons_cut = torelons[indices > cut]
    indices_cut = indices[indices > cut]

    index_block = len(indices_cut[indices_cut < indices_cut[0] + block])
    n_samp = 200
    torelons_resampled = blocked_bootstrap_gen(torelons_cut, index_block,
                                               n_new_samples=n_samp)

    print('\033[38;5;80mbootstrapping torelons:\033[0m')
    torelons_decay = []
    if pbar:
        with progressbar.ProgressBar(max_value=n_samp) as bar:
            i = 0
            for torelons in torelons_resampled:
                torelons_decay += [get_time_corr(torelons)]
                if not force:
                    bar.update(i)
                i += 1
            torelons_decay = np.array(torelons_decay)
    else:
        for torelons in torelons_resampled:
            torelons_decay += [get_time_corr(torelons)]
        torelons_decay = np.array(torelons_decay)

    torelons_decay_mean = torelons_decay.mean(axis=0)
    torelons_decay_std = torelons_decay.std(axis=0)

    if fit:
        from lib.analysis.tools import decay
        par, cov, χ2 = fit_decay(torelons_decay_mean, torelons_decay_std)
        if plot and (par is not None):
            x = np.linspace(0, len(torelons_decay_mean) - 1, 1001)
            y = np.vectorize(decay)(x - x.mean(), *par, rescale=x.mean())
            plt.plot(x, y, 'tab:green', label='fit')
    else:
        par, cov, χ2 = None, None, [None, None]

    if plot:
        plt.title(f'TORELON:\n Number of points: {len(indices_cut)}')
        plt.plot(torelons_decay_mean, 'tab:blue', label='bootstrap mean')
        plt.plot(torelons_decay_mean + torelons_decay_std, 'tab:red')
        plt.plot(torelons_decay_mean - torelons_decay_std, 'tab:red',
                 label='bootstrap std')
        plt.legend()
        plt.savefig('torelon.pdf')
        if not force:
            plt.show()

    # the sum over 'i' is the sum over the ensemble
    # the sum over 'j' is the sum over times
    # torelons_shift = np.array([np.roll(torelons_cut, Δt, axis=1)
    #                            for Δt in range(0, torelons_cut.shape[1] + 1)])
    # torelons_decay_pre = np.abs(np.einsum('kij,ij->k', torelons_shift,
    #                                       torelons_cut.conjugate()))
    # tolerons_mean_sq = abs((torelons_cut.mean(axis=0)**2).mean())
    #
    # torelons_decay = (torelons_decay_pre / torelons_cut.size -
    #                   tolerons_mean_sq)
           # np.einsum('ij,ij', torelons_cut, torelons_cut) / torelons_cut.size)
    # tolerons_var = abs((torelons_cut**2).mean()) - tolerons_mean_sq
    # torelons_decay /= tolerons_var

    # Run the following to be sure that the previous is the right formula
    # -------------------------------------------------------------------
    #
    # torelons_decay = np.einsum('kij,ij->ik', torelons_shift, torelons_cut)
    #
    # print(torelons_decay.shape)
    # torelons_decay1 = []
    # for torelon in torelons_cut:
    #     l = []
    #     for t in range(1, torelons_cut.shape[1]):
    #         l += [torelon @ np.roll(torelon, t)]
    #     torelons_decay1 += [np.array(l)]
    # torelons_decay1 = np.array(torelons_decay1)
    # print(torelons_decay1.shape)
    # print(((torelons_decay1 - torelons_decay) > 1e-7).any())

    # print(profiles_corr_mean)

    chdir(cwd)

    return list([torelons_decay_mean.tolist(),
                 torelons_decay_std.tolist(),
                 {'par': None if par is None else par.tolist(),
                  'cov': None if cov is None else cov.tolist(),
                  'chi2': χ2[0], 'dof': χ2[1]}])

def compute_profiles_corr(p_dir, plot, fit, force=False):
    import sys
    from os import chdir, getcwd
    import json
    import numpy as np
    from matplotlib import pyplot as plt
    from lib.analysis.tools import blocked_bootstrap_gen, get_time_corr

    try:
        import progressbar
        pbar = True
    except ModuleNotFoundError:
        pbar = False

    cwd = getcwd()
    chdir(p_dir)

    with open('measures.json', 'r') as file:
        measures = json.load(file)

    cut = measures['cut']
    block = measures['block']

    profiles_file = 'history/profiles.txt'
    A = np.loadtxt(profiles_file, unpack=True)
    indices = A[0]
    profiles = A[1:].transpose()

    profiles_cut = profiles[indices > cut]
    indices_cut = indices[indices > cut]

    index_block = len(indices_cut[indices_cut < indices_cut[0] + block])
    n_samp = 200
    profiles_resampled = blocked_bootstrap_gen(profiles_cut, index_block,
                                               n_new_samples=n_samp)

    print('\033[38;5;80mbootstrapping profiles:\033[0m')
    profiles_corr = []
    if pbar:
        with progressbar.ProgressBar(max_value=n_samp) as bar:
            i = 0
            for profiles in profiles_resampled:
                profiles_corr += [get_time_corr(profiles)]
                if not force:
                    bar.update(i)
                i += 1
            profiles_corr = np.array(profiles_corr)
    else:
        for profiles in profiles_resampled:
            profiles_corr += [get_time_corr(profiles)]
        profiles_corr = np.array(profiles_corr)

    profiles_corr_mean = profiles_corr.mean(axis=0)
    profiles_corr_std = profiles_corr.std(axis=0)

    # print(profiles_corr_mean)
    if fit:
        from lib.analysis.tools import decay
        par, cov, χ2 = fit_decay(profiles_corr_mean, profiles_corr_std)
        if plot and (par is not None):
            x = np.linspace(0, len(profiles_corr_mean) - 1, 1001)
            y = np.vectorize(decay)(x - x.mean(), *par, rescale=x.mean())
            plt.plot(x, y, 'tab:green', label='fit')
    else:
        par, cov, χ2 = None, None, [None, None]

    if plot:
        # ax.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)
        plt.plot(profiles_corr_mean, 'tab:blue', label='bootstrap mean')
        plt.plot(profiles_corr_mean + profiles_corr_std, 'tab:red')
        plt.plot(profiles_corr_mean - profiles_corr_std, 'tab:red',
                 label='bootstrap std')
        plt.title(f'PROFILE CORR.:\n Number of points: {len(indices_cut)}')
        plt.legend()
        plt.savefig('profile.pdf')
        if not force:
            plt.show()

    # the sum over 'i' is the sum over the ensemble
    # the sum over 'j' is the sum over times, and it's done after all the other
    # operations
    # profiles_shift = np.array([np.roll(profiles_cut, Δt, axis=1)
    #                            for Δt in range(0, profiles_cut.shape[1] + 1)])
    # profiles_corr_pre = np.einsum('kij,ij->k', profiles_shift, profiles_cut)
    # profiles_mean_sq = (profiles_cut.mean(axis=0)**2).mean()
    #
    # profiles_corr = profiles_corr_pre / profiles_cut.size - profiles_mean_sq
    # profiles_var = (profiles_cut**2).mean() - profiles_mean_sq
    # profiles_corr /= profiles_var

    # print(profiles_corr)

    # if plot:
    #     # plt.figure(2)
    #     plt.plot(profiles_corr, 'tab:green', label='mean')

    chdir(cwd)

    return list([profiles_corr_mean.tolist(),
                 profiles_corr_std.tolist(),
                 {'par': None if par is None else par.tolist(),
                  'cov': None if cov is None else cov.tolist(),
                  'chi2': χ2[0] if χ2 else None,
                  'dof': χ2[1] if χ2 else None}])

def fit_decay(profile, errors):
    import numpy as np
    from scipy.optimize import curve_fit
    from scipy.stats import chi2
    from lib.analysis.tools import decay

    times = np.arange(len(profile)) - ((len(profile) - 1) / 2)
    h = max(times)
    times /= max(times)
    profile = np.array(profile)
    errors = np.array(errors)

    try:
        par, cov = curve_fit(decay, times[1:-1], profile[1:-1],
                             sigma=errors[1:-1],
                             absolute_sigma=True, p0=(1., 0.))
        # err = np.sqrt(np.diag(cov))

        residuals_sq = ((profile[1:-1] - np.vectorize(decay)(times[1:-1], *par))
                        /errors[1:-1])**2
        χ2 = residuals_sq.sum()
        dof = len(times[1:-1]) - len(par)
        p_value = chi2.sf(χ2, dof)
        p_alert = 31 if 0.99 < p_value or p_value < 0.01 else 0

        rescale = np.array([h, 1])
        par = par * rescale
        cov = ((cov * rescale).T * rescale).T
        print(f'\033[93mcorr_length\033[0m = {par[0]} ± {np.sqrt(cov[0][0])}')

        print('\033[94mFit evaluation:\033[0m')
        print('\t\033[93mχ²\033[0m =', χ2)
        print('\t\033[93mdof\033[0m =', dof)
        print(f'\t\033[93mp-value\033[0m = \033[{p_alert}m', p_value,
                      '\033[0m')
    except RuntimeError:
        print('Fit failed.')
        par, cov = None, None
        χ2, dof = None, None

    return par, cov, [χ2, dof]

def fit_decay2(profile, errors):
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    from scipy.stats import chi2

    times = np.arange(len(profile))
    profile = np.array(profile)
    errors = np.array(errors)

    cut = len(profile) * 10 // 100
    p = profile[1:cut]
    e = errors[1:cut]
    t = times[1:cut]
    print(f'cut: {cut}')

    try:
        par, cov = curve_fit(exp_decay, t, p, sigma=e, absolute_sigma=True,
                             p0=(3.))
        # err = np.sqrt(np.diag(cov))

        exp_decay = np.vectorize(exp_decay)

        residuals_sq = ((p - exp_decay(t, *par)) / e)**2
        χ2 = residuals_sq.sum()
        dof = len(times[1:-1]) - len(par)
        p_value = chi2.sf(χ2, dof)
        p_alert = 31 if 0.99 < p_value or p_value < 0.01 else 0

        rescale = np.array([h, 1])
        par = par * rescale
        cov = ((cov * rescale).T * rescale).T
        print(f'\033[93mcorr_length\033[0m = {par[0]} ± {np.sqrt(cov[0][0])}')

        print('\033[94mFit evaluation:\033[0m')
        print('\t\033[93mχ²\033[0m =', χ2)
        print('\t\033[93mdof\033[0m =', dof)
        print(f'\t\033[93mp-value\033[0m = \033[{p_alert}m', p_value,
                      '\033[0m')

        if False:# p_alert:
            p_fit = None
        else:
            p_fit = np.zeros(1001)
            p_fit[:501] = exp_decay(np.linspace(0,len(times)/2, 501), *par)
            p_fit[-501:] = p_fit[500::-1]
    except RuntimeError:
        print('Fit failed.')
        par, cov = None, None
        χ2, dof = None, None

    return par, cov, [χ2, dof]

def fit_divergence(lambdas, volumes, errors, betas, kind='volumes'):
    import sys
    from os import getcwd
    from os.path import isfile, basename
    from platform import node
    import json
    from pprint import pprint
    import numpy as np
    from scipy.optimize import curve_fit
    from scipy.stats import chi2
    from matplotlib import pyplot as plt, colors as clr
    import seaborn as sns
    from lib.analysis.tools import divergence, constant

    if len(set(betas)) > 1:
        print('Volume fit is possible only for fixed β.')
        print('Instead following β were given:\n{set(betas)}')
        return

    class MyPrint:
        def __init__(self, filename):
            self.file = open(filename, 'w')

        def __del__(self):
            self.file.close()

        def write(self, *args, sep=' ', end='\n'):
            from re import sub
            print(*args, sep=sep, end=end)
            new_args = []
            for x in args:
                new_args += [sub('\033.*?m', '', str(x))]
            self.file.write(sep.join(new_args) + end)

    my_out = MyPrint(f'{kind[:3]}_output.txt')
    my_fit_msg = MyPrint(f'{kind[:3]}_fit_messages.txt')

    lambdas = np.array(lambdas)
    volumes = np.array(volumes)
    errors = np.array(errors)

    kw = {'height_ratios':[3,1]}
    with sns.axes_style("whitegrid"):
        sns.set_context("talk")
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, gridspec_kw=kw)
    # ax1 = fig.add_subplot(211)
    # ax2 = fig.add_subplot(212)

    ax1.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)

    my_fit_msg.write('\033[36m')
    my_fit_msg.write('Messages from fit (if any):')
    my_fit_msg.write('--------------------------')
    my_fit_msg.write('\033[0m')
    stderr_save = sys.stderr
    sys.stderr = my_fit_msg

    if kind in ['volumes', 'profiles', 'torelons']:
        lc_0 = min(lambdas)*0.7 if min(lambdas) > 0 else min(lambdas)*1.3
        alpha_0 = 2.4 if kind != 'profiles' else 2.
        A_0 = 61 if kind == 'volumes' else 0.
        p0=(lc_0, alpha_0, A_0)

        par, cov = curve_fit(divergence, lambdas, volumes, sigma=errors,
                             absolute_sigma=True, p0=p0)
        # bounds=((min(lambdas), -np.inf, -np.inf), (np.inf, np.inf, np.inf)))
    elif kind in ['gauge-action', 'topological-susceptibility']:
        par, cov = curve_fit(constant, lambdas, volumes, sigma=errors,
                             absolute_sigma=True)
    else:
        raise ValueError('kind not recognized')

    err = np.sqrt(np.diag(cov))

    sys.stderr = stderr_save
    my_fit_msg.write('\033[36m', end='')
    my_fit_msg.write('--------------------------')
    my_fit_msg.write('End fit')
    my_fit_msg.write('\033[0m')

    if kind in ['volumes', 'profiles', 'torelons']:
        residuals = ((volumes - np.vectorize(divergence)(lambdas, *par))
                        /errors)
    elif kind in ['gauge-action', 'topological-susceptibility']:
        residuals = ((volumes - np.vectorize(constant)(lambdas, *par))
                        /errors)

    residuals_sq = residuals**2
    χ2 = residuals_sq.sum()
    dof = len(lambdas) - len(par)
    p_value = chi2.sf(χ2, dof)
    p_alert = 31 if 0.99 < p_value or p_value < 0.01 else 0

    β = str(betas[0])
    my_out.write('\033[38;5;87m┌──', '─' * len(β), '──┐', sep='')
    my_out.write(f'│β = {β}│')
    my_out.write('└──', '─' * len(β), '──┘\033[0m\n', sep='')

    my_out.write('\033[94mFunction:\033[0m')
    if kind in ['volumes', 'profiles', 'torelons']:
        my_out.write('\tf(λ) = A*(λ - λ_c)**(-α)')
    elif kind in ['gauge-action', 'topological-susceptibility']:
        my_out.write('\tf(λ) = a')

    my_out.write('\033[94mFit evaluation:\033[0m')
    my_out.write('\t\033[93mχ²\033[0m =', χ2)
    my_out.write('\t\033[93mdof\033[0m =', dof)
    my_out.write(f'\t\033[93mp-value\033[0m = \033[{p_alert}m', p_value,
                  '\033[0m')

    if kind in ['volumes', 'profiles', 'torelons']:
        names = ['λ_c', 'α', 'A']
    elif kind in ['gauge-action', 'topological-susceptibility']:
        names = ['a']

    my_out.write('\033[94mOutput parameters:\033[0m')
    for x in zip(names, zip(par, err)):
        my_out.write(f'\t\033[93m{x[0]}\033[0m = {x[1][0]} ± {x[1][1]}')

    n = len(par)
    corr = np.zeros((n, n))
    for i in range(0, n):
        for j in range(0, n):
            corr[i,j] = cov[i,j]/np.sqrt(cov[i,i]*cov[j,j])

    my_out.write('\033[94mCorrelation coefficients:\033[0m')
    my_out.write("\t" + str(corr).replace('\n','\n\t'))

    if not isfile(f'../par_{kind[:3]}.csv'):
        with open(f'../par_{kind[:3]}.csv', 'a') as f_par:
            f_par.write('# fit_name[0] ')
            i = 1
            for name in names:
                f_par.write(f'{name}[{i}] err_{name}[{i+1}] ')
                i += 2
            f_par.write('\n\n')

    fit_name = str(basename(getcwd()))
    with open(f'../par_{kind[:3]}.csv', 'r') as f_par:
        f_cont = f_par.read()
        pos_ = f_cont.find(fit_name + ' ')
        expr_ = f'{fit_name} '
        expr_ += ''.join([f'{x[0]} {x[1]} ' for x in zip(par, err)])
        if pos_ != -1:
            end_pos = f_cont[pos_:].find('\n')
            f_cont = f_cont[:pos_] + expr_ + f_cont[(pos_ + end_pos):]
        else:
            expr_ += '\n'
            f_cont += expr_

    with open(f'../par_{kind[:3]}.csv', 'w') as f_par:
        f_par.write(f_cont)

    # PLOT

    # sns.set_style('white')
    # sns.set_style("whitegrid")
    # plt.style.use('seaborn-paper')

    l_inter = np.linspace(min(lambdas), max(lambdas), 1000)
    if kind in ['volumes', 'profiles', 'torelons']:
        ax1.plot(l_inter, divergence(l_inter, *par))
        ax1.set_ylabel('volume')
    elif kind in ['gauge-action', 'topological-susceptibility']:
        ax1.plot(l_inter, np.vectorize(constant)(l_inter, *par))
        ax1.errorbar(l_inter.mean(), par[0], np.sqrt(cov[0][0]),
                     ecolor='tab:green', capsize=5)
        print('typ err: ', errors.mean())
        print('max - min: ', max(volumes) - min(volumes))
        fig2 = plt.figure()
        plt.hist(errors)
        if kind == 'topological-susceptibility':
            ax1.set_ylabel('$\\chi$')

    fc_ = residuals.astype(str)
    fc_[residuals > 0.] = 'tab:green'
    fc_[fc_ != 'tab:green'] = 'w'
    ax2.scatter(lambdas, residuals, c=clr.to_rgba_array(fc_), #s=5,
             edgecolors='k', linewidths=.5)
    ax2.set_xlabel('λ')
    ax2.set_ylabel('residuals')

    ax1.set_title(f'β = {betas[0]}:\n$χ^2$ = {χ2:0.1f},  dof = {dof},  '
                  f'p-value = {p_value:4.2%}')
    plt.tight_layout(pad=0.5)
    plt.savefig(f'fit_{kind[:3]}.pdf')
    if node() == 'Paperopoli':
        plt.show()
        # pass

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

def set_cut(p_dir, i=0):
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

def set_block(p_dir, i=0):
    from os import chdir
    from os.path import basename
    from math import log
    import json
    from numpy import loadtxt
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

    ratio = 1.3
    block_sizes = [ratio**k for k in
                   range(15, int(log(imax - cut, ratio)) - 10)]
    stdevs = []
    for bs in block_sizes:
        _, stdev = blocked_mean_std(indices_cut, volumes_cut, bs)
        stdevs += [stdev]

    block, _ = select_from_plot(Point, block_sizes, stdevs, i, proj_axis='y',
                                block=True)
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

    print('volume: {:.4} ± {:.3}'.format(vol, err))

    return vol, err

def compute_torelons(p_dir, plot, fit):
    from os import chdir, getcwd
    import json
    import numpy as np
    from matplotlib import pyplot as plt
    from lib.analysis.tools import block_array, bootstrap

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
    torelons_blocked = block_array(torelons_cut, index_block)

    # 'b' is the index over blocks
    # 'i' is the index over the ensemble
    # 't' is the index over physical times
    # 'k' is the index over time-shifts, Δt

    # print(torelons_blocked.shape)
    # <<V_t V_(t+Δt)>>_t
    torelons_shift = np.array([np.roll(torelons_blocked, Δt, axis=2)
                             for Δt in range(0, torelons_blocked.shape[2] + 1)])
    torelons_decay_pre = np.abs(np.einsum('kbit,bit->bk', torelons_shift,
                                          torelons_blocked.conjugate()))
    # <<V_t>**2>_t : before the mean over the ensemble, at the end the mean
    # over times
    torelons_mean_sq = (abs(torelons_blocked.mean(axis=1)**2)).mean(axis=1)

    torelons_decay = (torelons_decay_pre.transpose() / torelons_blocked[0].size
                     - torelons_mean_sq)

    torelons_decay_mean, torelons_decay_std = \
        np.vectorize(bootstrap, signature='(m)->(k)')(torelons_decay).T

    # print(torelons_decay_mean)

    if fit:
        from lib.analysis.tools import decay
        par, cov = fit_decay(torelons_decay_mean, torelons_decay_std)
        if plot and par:
            x = np.linspace(0, len(torelons_decay_mean) - 1, 1001)
            x_t = np.linspace(-1., 1., 1001)
            y = np.vectorize(decay)(x_t, *par)
            plt.plot(x, y, 'tab:purple', label='fit')
    else:
        par, cov = None, None

    if plot:
        # plt.title(f'TIME CORR.:\n Number of points: {len(indices_cut)}')
        plt.plot(torelons_decay_mean, 'tab:blue')
        plt.plot(torelons_decay_mean + torelons_decay_std, 'tab:red')
        plt.plot(torelons_decay_mean - torelons_decay_std, 'tab:red')
        # plt.show()

    # the sum over 'i' is the sum over the ensemble
    # the sum over 'j' is the sum over times
    torelons_shift = np.array([np.roll(torelons_cut, Δt, axis=1)
                               for Δt in range(0, torelons_cut.shape[1] + 1)])
    torelons_decay_pre = np.abs(np.einsum('kij,ij->k', torelons_shift,
                                          torelons_cut.conjugate()))
    tolerons_mean_sq = abs((torelons_cut.mean(axis=0)**2).mean())

    torelons_decay = (torelons_decay_pre / torelons_cut.size -
                      tolerons_mean_sq)
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

    if plot:
        plt.title(f'TORELON:\n Number of points: {len(indices_cut)}')
        plt.plot(torelons_decay, 'tab:green')
        plt.show()

    chdir(cwd)

    return list([torelons_decay_mean.tolist(),
                 torelons_decay_std.tolist(),
                 None if par is None else par.tolist(),
                 None if cov is None else cov.tolist()])

def compute_profiles_corr(p_dir, plot, fit):
    import sys
    from os import chdir, getcwd
    import json
    import numpy as np
    from matplotlib import pyplot as plt
    # from lib.analysis.tools import block_array, blocked_bootstrap_gen, get_time_corr
    from tools import block_array, blocked_bootstrap_gen, get_time_corr

    try:
        import progressbar
        pbar = True
    except ModuleNotFoundError:
        pbar = False

    cwd = getcwd()
    chdir(p_dir)

    # with open('measures.json', 'r') as file:
    #     measures = json.load(file)

    # cut = measures['cut']
    # block = measures['block']
    cut = 165540000
    block = 156272640

    # profiles_file = 'history/profiles.txt'
    profiles_file = 'profiles.txt'
    A = np.loadtxt(profiles_file, unpack=True)
    indices = A[0]
    profiles = A[1:].transpose()

    profiles_cut = profiles[indices > cut]
    indices_cut = indices[indices > cut]

    index_block = len(indices_cut[indices_cut < indices_cut[0] + block])
    profiles_blocked = block_array(profiles_cut, index_block)
    profiles_resampled = blocked_bootstrap_gen(profiles_blocked, len_new_sample=96)

    profiles_corr = []
    if pbar:
        with progressbar.ProgressBar(max_value=1e3) as bar:
            i = 0
            for profiles in profiles_resampled:
                profiles_corr += [get_time_corr(profiles)]
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
        par, cov = fit_decay(profiles_corr_mean, profiles_corr_std)
        if plot:
            x = np.linspace(0, len(profiles_corr_mean) - 1, 1001)
            x_t = np.linspace(-1., 1., 1001)
            y = np.vectorize(decay)(x_t, *par)
            plt.plot(x, y, 'tab:purple', label='fit')
    else:
        par, cov = None, None

    if plot:
        # ax.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)
        plt.plot(profiles_corr_mean, 'tab:blue', label='bootstrap mean')
        plt.plot(profiles_corr_mean + profiles_corr_std, 'tab:red')
        plt.plot(profiles_corr_mean - profiles_corr_std, 'tab:red',
                 label='bootstrap std')

    # the sum over 'i' is the sum over the ensemble
    # the sum over 'j' is the sum over times, and it's done after all the other
    # operations
    profiles_shift = np.array([np.roll(profiles_cut, Δt, axis=1)
                               for Δt in range(0, profiles_cut.shape[1] + 1)])
    profiles_corr_pre = np.einsum('kij,ij->k', profiles_shift, profiles_cut)
    profiles_mean_sq = (profiles_cut.mean(axis=0)**2).mean()

    profiles_corr = profiles_corr_pre / profiles_cut.size - profiles_mean_sq
    profiles_var = (profiles_cut**2).mean() - profiles_mean_sq
    profiles_corr /= profiles_var

    # print(profiles_corr)

    if plot:
        # plt.figure(2)
        plt.title(f'TIME CORR.:\n Number of points: {len(indices_cut)}')
        plt.plot(profiles_corr, 'tab:green', label='mean')
        plt.legend()
        plt.show()

    chdir(cwd)

    return list([profiles_corr_mean.tolist(),
                 profiles_corr_std.tolist(),
                 None if par is None else par.tolist(),
                 None if cov is None else cov.tolist()])

def fit_decay(profile, errors):
    import numpy as np
    from scipy.optimize import curve_fit
    from lib.analysis.tools import decay

    times = np.arange(len(profile)) - ((len(profile) - 1) / 2)
    h = max(times)
    times /= max(times)
    profile = np.array(profile)
    errors = np.array(errors)

    try:
        par, cov = curve_fit(decay, times[1:-1], profile[1:-1], sigma=errors[1:-1],
                             absolute_sigma=True, p0=(1., 0.))
        # err = np.sqrt(np.diag(cov))
    except RuntimeError:
        par, cov = None, None

    return par, cov

def fit_divergence(lambdas, volumes, errors, betas, kind='volumes'):
    import sys
    from platform import node
    import json
    from pprint import pprint
    import numpy as np
    from scipy.optimize import curve_fiterrerr
    from scipy.stats import chi2
    from matplotlib.pyplot import figure, show, savefig
    from lib.analysis.tools import divergence

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

    my_out = MyPrint('vol_output.txt')
    my_fit_msg = MyPrint('vol_fit_messages.txt')

    lambdas = np.array(lambdas)
    volumes = np.array(volumes)
    errors = np.array(errors)

    fig = figure()
    ax = fig.add_subplot(111)

    ax.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)

    my_fit_msg.write('\033[36m')
    my_fit_msg.write('Messages from fit (if any):')
    my_fit_msg.write('--------------------------')
    my_fit_msg.write('\033[0m')
    stderr_save = sys.stderr
    sys.stderr = my_fit_msg

    par, cov = curve_fit(divergence, lambdas, volumes, sigma=errors,
                         absolute_sigma=True, p0=(min(lambdas)*0.7, 2.4, 61))
        # bounds=((min(lambdas), -np.inf, -np.inf), (np.inf, np.inf, np.inf)))
    err = np.sqrt(np.diag(cov))

    sys.stderr = stderr_save
    my_fit_msg.write('\033[36m', end='')
    my_fit_msg.write('--------------------------')
    my_fit_msg.write('End fit')
    my_fit_msg.write('\033[0m')

    residuals_sq = ((volumes - np.vectorize(divergence)(lambdas, *par))
                    /errors)**2
    χ2 = residuals_sq.sum()
    dof = len(lambdas) - len(par)
    p_value = chi2.sf(χ2, dof)
    p_al = 31 if 0.99 < p_value or p_value < 0.01 else 0

    β = str(betas[0])
    my_out.write('\033[38;5;87m┌──', '─' * len(β), '──┐', sep='')
    my_out.write(f'│β = {β}│')
    my_out.write('└──', '─' * len(β), '──┘\033[0m\n', sep='')

    my_out.write('\033[94mFunction:\033[0m')
    my_out.write('\tf(λ) = A*(λ - λ_c)**(-α)')

    my_out.write('\033[94mFit evaluation:\033[0m')
    my_out.write('\t\033[93mχ²\033[0m =', χ2)
    my_out.write('\t\033[93mdof\033[0m =', dof)
    my_out.write(f'\t\033[93mp-value\033[0m = \033[{p_al}m', p_value,
                  '\033[0m')

    names = ['λ_c', 'α', 'A']

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

    l_inter = np.linspace(min(lambdas), max(lambdas), 1000)
    ax.plot(l_inter, divergence(l_inter, *par))

    savefig('fit.pdf')
    if node() == 'Paperopoli':
        show()

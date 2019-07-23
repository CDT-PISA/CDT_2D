def select_from_plot(Point, indices, values, i=0, dot=None, proj_axis='x'):
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
            inarea = x > imin and x < imax and y > vmin and y < vmax
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
            inarea = x > imin and x < imax and y > vmin and y < vmax
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
    from lib.utils import dir_point

    chdir(p_dir)
    Point = dir_point(basename(p_dir))

    vol_file = 'history/volumes.txt'
    indices, volumes = loadtxt(vol_file, unpack=True)

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
    indices, volumes = loadtxt(vol_file, unpack=True)
    imax = indices[-1]

    volumes_cut = volumes[indices > cut]
    indices_cut = indices[indices > cut]

    ratio = 1.5
    block_sizes = [ratio**k for k in
                   range(0, int(log(imax - cut, ratio)) - 3)]
    stdevs = []
    for bs in block_sizes:
        _, stdev = blocked_mean_std(indices_cut, volumes_cut, bs)
        stdevs += [stdev]

    block, _ = select_from_plot(Point, block_sizes, stdevs, i, proj_axis='y')
    if block == None or block == -1:
        print('Nothing done.')
        return None
    block = int(block)

    return block

def eval_volume(p_dir):
    from os import chdir
    import json
    from numpy import loadtxt

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

    return vol, err

def fit_volume(lambdas, volumes, errors):
    import json
    from numpy import array, sqrt, log, zeros, diag, vectorize, linspace
    from scipy.optimize import curve_fit
    from matplotlib.pyplot import figure, show

    lambdas = array(lambdas)
    volumes = array(volumes)
    errors = array(errors)

    fig = figure()
    ax = fig.add_subplot(111)

    ax.errorbar(lambdas, volumes, yerr=errors, fmt='none', capsize=5)

    def volume(l, l_c, alpha, A):
        return A*(l - l_c)**(-alpha)

    par, cov = curve_fit(volume, lambdas, volumes, sigma=errors,
                         absolute_sigma=True, p0=(0.69315, 2.4, 61))

    residuals_sq = ((volumes - vectorize(volume)(lambdas, *par))/errors)**2
    chi2 = residuals_sq.sum()
    dof = len(lambdas) - len(par)

    print("χ² = ", chi2, dof)

    names = ['λ_c', 'alpha', 'factor']#, 'shift']
    print(dict(zip(names, par)))
    print(dict(zip(names,sqrt(diag(cov)))))

    n = len(par)
    corr = zeros((n, n))
    for i in range(0, n):
        for j in range(0, n):
            corr[i,j] = cov[i,j]/sqrt(cov[i,i]*cov[j,j])

    print(corr)

    l_inter = linspace(min(lambdas), max(lambdas), 1000)
    ax.plot(l_inter, volume(l_inter, *par))

    show()

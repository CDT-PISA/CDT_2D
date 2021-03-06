"""Preliminary analyses
"""

from numpy import loadtxt
from lib.analysis import sim_paths

def mean_volumes(configs=None, print_flag=True, path=None):
    from pprint import pprint

    mvs = {}
    for c, sims in sim_paths().items():
        if configs and c not in configs:
            continue

        for path in sims:
            from os import chdir
            from os.path import basename, isfile
            import json
            from numpy import loadtxt
            from lib.utils import dir_point

            chdir(path)

            Point = dir_point(basename(path))
            if isfile('history/volumes.txt'):
                _, volumes = loadtxt('history/volumes.txt', unpack=True)

                with open('state.json', 'r') as state_file:
                    state = json.load(state_file)

                try:
                    cut = state['cut']
                except KeyError:
                    cut = 0

                try:
                    mvs[c] = {**mvs[c], Point: volumes[cut:].mean()}
                except KeyError:
                    mvs[c] = {Point: volumes[cut:].mean()}

    if print_flag:
        pprint(mvs)

    return mvs

def divergent_points(configs=None, conf_plot=False, save_path=None,
                     load_path=None):
    from os.path import isdir
    from numpy import array
    from matplotlib.pyplot import plot, show, figure

    if load_path and isdir(load_path):
        from os import chdir
        from numpy import loadtxt

        chdir(load_path)
        try:
            convergent = loadtxt('convergent.csv')
            divergent = loadtxt('divergent.csv')
            if len(convergent.shape) == 1:
                convergent = convergent.reshape(1, convergent.shape[0])
            if len(divergent.shape) == 1:
                divergent = divergent.reshape(1, divergent.shape[0])
        except OSError:
            print(f"Invalid path given: '{load_path}'.")
            return
        try:
            fit_line = loadtxt('fit_line.csv')
        except OSError:
            fit_line = []
    else:
        convergent = []
        divergent = []
        fit_line = []
        if conf_plot:
            from matplotlib.text import Text
            ylabel = []
            i = 0

        for c, sims in sim_paths().items():
            if configs and c not in configs:
                continue

            if conf_plot:
                i += 1
                print(i, c)
                # ylabel += [Text(x=(i-1), y=i, text=c)]
                ylabel += [c]

            for path in sims:
                from os import chdir
                from os.path import basename, isfile
                from lib.utils import dir_point

                chdir(path)

                if conf_plot:
                    Point = [dir_point(basename(path))[0], i]
                else:
                    Point = dir_point(basename(path))

                if isfile('max_volume_reached'):
                    divergent += [Point]
                elif isfile('history/volumes.txt'):
                    convergent += [Point]


    fig = figure()
    ax = fig.add_subplot(111)
    if len(convergent) > 0:
        convergent = array(convergent)
        # *zip(*convergent)
        ax.plot(convergent[:,0], convergent[:,1], 'b+')
    if len(divergent) > 0:
        divergent = array(divergent)
        # *zip(*divergent)
        ax.plot(divergent[:,0], divergent[:,1], 'r+')
    if len(fit_line) > 0:
        ax.plot(fit_line[:,0], fit_line[:,1], 'k')

    if save_path and isdir(save_path):
        from os import makedirs, chdir, getcwd
        from numpy import savetxt, array

        chdir(save_path)
        makedirs('DivergentPlot', exist_ok=True)
        chdir('DivergentPlot')
        savetxt('convergent.csv', array(convergent))
        savetxt('divergent.csv', array(divergent))
        savetxt('fit_line.csv', array(fit_line))
    elif save_path:
        print(f"Invalid path given: '{path}'.")


    if conf_plot:
        from numpy import linspace
        yticks_location = linspace(1, len(ylabel), len(ylabel))
        ax.set_yticks(yticks_location)
        ax.set_yticklabels(ylabel)
        ax.set_ylim(0, len(ylabel) + 1)

    if save_path and isdir(save_path):
        from matplotlib.pyplot import savefig

        savefig(save_path + '/DivergentPlot/DivergentPlot.pdf')
    elif load_path and isdir(load_path):
        from matplotlib.pyplot import savefig

        savefig(load_path + '/DivergentPlot.pdf')

    show()

def volumes_plot(configs=None, path=None):
    from os.path import isfile
    import matplotlib.pyplot as plt
    from lib.utils import point_dir, config_dir

    mvs = mean_volumes(configs, print_flag=False)

    curves = {}
    for c, sims in mvs.items():
        for Point, mv in sims.items():
            if isfile(config_dir(c) + '/' + point_dir(Point) +
                      '/max_volume_reached'):
                continue
            curve = c + ' β=' + str(Point[1])
            coords = (Point[0], mv)
            try:
                curves[curve] += [coords]
            except KeyError:
                curves[curve] = [coords]

    for lab, points in curves.items():
        points = sorted(points, key=lambda x: x[0])
        plt.plot(*zip(*points), marker='o', label=lab)

    plt.xlabel('λ')
    plt.ylabel('Volume')
    plt.legend()
    plt.show()


def preplot(fit_name, kind):
    from os import chdir
    import numpy as np
    import matplotlib.pyplot as plt
    from lib.utils import fit_dir
    import seaborn as sns

    sns.set_style('whitegrid')
    sns.set_context('talk')

    chdir(fit_dir(fit_name))

    if kind in ['v', 'volumes']:
        try:
            data = np.genfromtxt('volumes.csv', unpack=True)
        except (FileNotFoundError, OSError):
            print(f"No file 'volumes.csv' for fit {fit_name}")
            return
        Lambda = data[0]
        vol, err = data[2], data[3]

        plt.title('Volumes:\n' + fit_name)
        plt.errorbar(Lambda, vol, err, fmt='none', capsize=5)
        plt.savefig('pre_volumes.pdf')
        plt.show()

    elif kind in ['p', 'profiles']:
        try:
            data = np.genfromtxt('profiles_length.csv', unpack=True)
        except (FileNotFoundError, OSError):
            print(f"No file 'profiles_length.csv' for fit {fit_name}")
            return
        Lambda = data[0]
        pro_xi, err = data[2], data[3]

        plt.title('Profiles Correlation Lengths:\n' + fit_name)
        plt.errorbar(Lambda, pro_xi, err, fmt='none', capsize=5)
        plt.savefig('pre_profiles.pdf')
        plt.show()

    elif kind in ['g', 'action', 'gauge', 'gauge-action']:
        try:
            data = np.genfromtxt('gauge_action.csv', unpack=True)
        except (FileNotFoundError, OSError):
            print(f"No file 'gauge_action.csv' for fit {fit_name}")
            return
        Lambda, Beta = data[0], data[1]
        g_action, err = data[2], data[3]
        g_action_density, density_err = data[4], data[5]

        # the average coord num in 2d is fixed and it is 6
        g_av_plaq = - ((g_action_density * 6) / Beta - 1)
        av_plaq_err = (density_err * 6) / Beta

        fig, axs = plt.subplots(2,1)
        axs[0].set_title('Gauge action:\n' + fit_name)
        axs[0].errorbar(Lambda, g_action, err, fmt='none', c='tab:green',
                     capsize=5, label='action')
        axs[0].legend()
        axs[1].errorbar(Lambda, g_av_plaq, av_plaq_err, fmt='none',
                     capsize=5, label='average plaquette')
        axs[1].legend()
        plt.savefig('pre_gauge_action.pdf')
        plt.show()

    elif kind in ['top', 'susc', 'top-susc']:
        try:
            data = np.genfromtxt('top_susc.csv', unpack=True)
        except (FileNotFoundError, OSError):
            print(f"No file 'top_susc.csv' for fit {fit_name}")
            return
        Lambda = data[0]
        top, err = data[2], data[3]

        plt.title('Topological susceptibilities:\n' + fit_name)
        plt.errorbar(Lambda, top, err, fmt='none', capsize=5)
        plt.savefig('pre_top_susc.pdf')
        plt.show()

    elif kind in ['t', 'torelons']:
        try:
            data = np.genfromtxt('torelon_length.csv', unpack=True)
        except (FileNotFoundError, OSError):
            print(f"No file 'torelon_length.csv' for fit {fit_name}")
            return
        Lambda = data[0]
        tor_xi, err = data[2], data[3]

        plt.title('Torelons Correlation Lengths:\n$\\beta = ' + fit_name[4:] + '$')
        plt.errorbar(Lambda, tor_xi, err, fmt='none', capsize=5)
        plt.xlabel('$\\lambda$')
        plt.ylabel('$\\xi_T$')
        plt.tight_layout()
        plt.savefig('pre_torelons.pdf')
        plt.show()

"""Preliminary analyses
"""

from numpy import loadtxt
from lib.analysis import sim_paths

def mean_volumes(configs=None):
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

    pprint(mvs)

def divergent_points(configs=None, conf_plot=False):
    from matplotlib.pyplot import plot, show, figure

    convergent = []
    divergent = []
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
    if convergent:
        ax.plot(*zip(*convergent), 'b+')
    if divergent:
        ax.plot(*zip(*divergent), 'r+')

    if conf_plot:
        from numpy import linspace
        yticks_location = linspace(1, len(ylabel), len(ylabel))
        ax.set_yticks(yticks_location)
        ax.set_yticklabels(ylabel)
        ax.set_ylim(0, len(ylabel) + 1)

    show()

def volume_plots():
    pass

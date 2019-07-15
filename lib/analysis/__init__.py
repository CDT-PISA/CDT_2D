# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 11:32:00 2019

@author: alessandro
"""

from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close

def preliminary_analyses(kind, config=None):
    import lib.analysis.pre as pre

    if kind in ['v', 'volumes']:
        pre.mean_volumes(config)
    elif kind in ['d', 'divergent']:
        pre.divergent_points(config)
    else:
        raise RuntimeError('preliminary_analyses: kind not recognized')


def select_from_plot(Lambda, indices, volumes, i=0, dot=None):
    from matplotlib.pyplot import figure, show, figtext

    imin = min(indices)
    imax = max(indices)
    vmin = min(volumes)
    vmax = max(volumes)

    color_cycle = ['xkcd:carmine', 'xkcd:teal', 'xkcd:peach', 'xkcd:mustard',
                   'xkcd:cerulean']

    n_col = len(color_cycle)

    fig = figure()
    ax = fig.add_subplot(111)
    canvas = fig.canvas

    fig.set_size_inches(7, 5)
    ax.plot(indices, volumes, color=color_cycle[i % n_col])
    ax.set_title('λ = ' + str(Lambda))
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
                n = ax.plot(x, vmin, 'k|', ms=20)
                event.canvas.draw()
                m[0].remove()
                n[0].remove()
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

def sim_paths():
    from lib.utils import find_configs
    from os import scandir

    configs = find_configs()

    d = {}
    for name, path in configs.items():
        sims = [x.path for x in scandir(path)
                if x.is_dir() and 'Lambda' in x.name]
        d[name] = sims

    return d

def set_cut():
    pass

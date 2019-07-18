# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 11:32:00 2019

@author: alessandro
"""

from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close

def preliminary_analyses(kind, configs=None, conf_plot=False):
    from re import fullmatch
    from lib.utils import find_configs
    import lib.analysis.pre as pre

    if configs:
        pattern_configs = []
        pure_configs = []
        all_configs = list(find_configs().keys())
        for config in configs:
            if config[0] == '§':
                pattern_configs += [c for c in all_configs
                                    if fullmatch(config[1:], c)]
            else:
                pure_configs += [config]

        configs = list(set(pure_configs + pattern_configs))
        print(f'Chosen configs are:\n  {configs}')
    else:
        configs = list(find_configs().keys())

    if kind in ['mv', 'mean-volumes']:
        pre.mean_volumes(configs)
    elif kind in ['vp', 'volumes-plot']:
        pre.volumes_plot(configs)
    elif kind in ['d', 'divergent']:
        pre.divergent_points(configs, conf_plot)
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

# FIT MANAGEMENT

def new_fit(name, path, caller_path):
    from os.path import isdir, isfile, abspath, basename
    from os import chdir, mkdir, listdir
    from inspect import cleandoc
    import json
    from lib.utils import find_fits, project_folder

    msg_exist = cleandoc("""The requested fit already exists.
                If you want to reset it, please use the specific command.""")

    fits = find_fits()

    chdir(caller_path)

    # actually creates requested folder
    if not path:
        path = caller_path + '/' + name

    if name in fits.keys() or abspath(path) in fits.values():
        print(msg_exist)
        return
    elif basename(path) != name:
        print('At the present time names different from target '
              'directories are not available.')
        return
    else:
        try:
            mkdir(path)
        except (FileExistsError, FileNotFoundError):
            print('Invalid path given.')
            return

    print(f"Created fit '{name}' at path:\n  {abspath(path)}")

    fits = {**fits, name: abspath(path)}
    with open(project_folder() + '/output/fits.json', 'w') as fit_file:
        json.dump(fits, fit_file, indent=4)

def show_fits(paths):
    from lib.utils import find_fits, project_folder
    import pprint as pp

    fits = find_fits()

    if paths:
        for name, path in sorted(fits.items(), key=lambda x: x[0].lower()):
            print(name, path, sep=':\n\t')
    else:
        if isinstance(fits, dict):
            fits = list(fits.keys())

        for name in sorted(fits, key=str.lower):
            print(name)

def reset_fit(names, delete):
    from os.path import isdir
    from os import chdir, mkdir
    from shutil import rmtree
    from re import fullmatch
    import json
    from lib.utils import (authorization_request, fit_dir, find_fits,
                           project_folder)

    pattern_names = []
    pure_names = []
    all_names = list(find_fits().keys())
    for name in names:
        if name[0] == '§':
            pattern_names += [c for c in all_names
                                if fullmatch(name[1:], c)]
        else:
            pure_names += [name]

    names = list(set(pure_names + pattern_names))
    print(f'Chosen fits are:\n  {names}')

    for name in names:
        fit = fit_dir(name)

        if delete:
            action = 'delete'
        else:
            action = 'reset'
        what_to_do = 'to ' + action + ' the configuration \'' + name + '\''
        authorized = authorization_request(what_to_do)
        if authorized == 'yes':
            rmtree(fit)
            if action == 'reset':
                mkdir(fit)
            elif action == 'delete':
                with open(project_folder() + '/output/fits.json', 'r') as file:
                    fits = json.load(file)
                del fits[name]
                with open(project_folder() + '/output/fits.json', 'w') as file:
                    json.dump(fits, file, indent=4)
            print(f'Configuration {name} has been {action}.')
        elif authorized == 'quit':
            print('Nothing done on last fit.')
            return
        else:
            print('Nothing done.')

# def rm_conf(config, force):
#     from os import rmdir, remove
#     from os.path import isfile
#     import json
#     from lib.utils import points_recast, config_dir, project_folder
#
#     points_old, _ = points_recast([], [], '', True, config, 'tools')
#     clear_data(points_old, config, force)
#
#     path = config_dir(config)
#     if isfile(path + '/pstop.pickle'):
#         remove(path + '/pstop.pickle')
#     rmdir(path)
#     print(f"Removed config '{config}' at path:\n  {path}")
#
#     with open(project_folder() + '/output/configs.json', 'r') as config_file:
#         configs = json.load(config_file)
#
#     del configs[config]
#
#     with open(project_folder() + '/output/configs.json', 'w') as config_file:
#         json.dump(configs, config_file, indent=4)

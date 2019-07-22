# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 11:32:00 2019

@author: alessandro
"""

from numpy import loadtxt
from matplotlib.pyplot import plot, imshow, colorbar, figure, savefig, subplots, subplots_adjust, close

# PRELIMINARY ANALYSES

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
            action_p = action + 'd'
        else:
            action = 'reset'
            action_p = action

        what_to_do = 'to ' + action + ' the fit \'' + name + '\''
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
            print(f'Fit {name} has been {action_p}.')
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


def set_fit_props(name, points, config):
    from os import chdir, popen
    import json
    from lib.utils import fit_dir, config_dir, point_dir

    chdir(fit_dir(name))

    try:
        with open('sims.json', 'r') as file:
            sims = json.load(file)
    except FileNotFoundError:
        sims = []

    # SIMS UPDATE

    c_dir = config_dir(config)
    for Point in points:
        p_dir = c_dir + '/' + point_dir(Point)
        if p_dir not in sims:
            sims += [p_dir]

    with open('sims.json', 'w') as file:
        json.dump(sims, file, indent=4)

    # inserire un kind e aggiungere come possibilità quella di settare il tipo di osservabili
    # a cui è riferito il fit (1 sola)
    # cioè se è un fit: al volume, all'azione, alla carica topologica, ...

def show_fit_props(name, kind='sims'):
    from os import chdir
    from os.path import basename, dirname
    from pprint import pprint
    import json
    from lib.utils import fit_dir, config_dir, dir_point

    chdir(fit_dir(name))

    if kind == 'sims':
        try:
            with open('sims.json', 'r') as file:
                sims = json.load(file)

            d = {}
            for s in sims:
                if s[-1] == '/':
                    s = s[:-1]

                config = basename(dirname(s))
                Point = dir_point(basename(s))
                try:
                    d[config] += [Point]
                except KeyError:
                    d[config] = [Point]

            pprint(d)
        except FileNotFoundError:
            print('No simulation already assigned to this fit.')
    elif kind == 'obs':
        pass
    else:
        raise ValueError('info-fit: kind {kind} not recognized')

    # inserire un kind e aggiungere come possibilità quella di visualizzare il tipo di osservabili
    # dato che ogni fit sarà un fit di 1 osservabile basterà un 'obs'

def sim_obs(points, config):
    from os import chdir
    from time import time
    from datetime import datetime
    import json
    from pprint import pprint
    from lib.utils import config_dir, point_dir, authorization_request
    from lib.analysis.fit import set_cut, set_block, eval_volume

    c_dir = config_dir(config)

    col = 216
    print(f'Number of selected points: \033[38;5;{col}m{len(points)}\033[0m')
    print(f'\033[38;5;{col}m', end='')
    pprint(points)
    print('\033[0m')

    i = 0
    for Point in points:
        p_dir = c_dir + '/' + point_dir(Point)
        chdir(p_dir)

        what = 'to select cut & block'
        auth = authorization_request(what_to_do=what, Point=Point)

        if auth == 'quit':
            print('Nothing done on the last sim.')
            return
        elif auth == 'yes':
            try:
                with open('measures.json', 'r') as file:
                    measures = json.load(file)
            except FileNotFoundError:
                measures = {}

            cut = set_cut(p_dir, i)
            print(f'cut = {cut}')
            if cut:
                measures['cut'] = cut
                with open('measures.json', 'w') as file:
                    json.dump(measures, file, indent=4)
            try :
                cut = measures['cut']
            except KeyError:
                pass

            block = set_block(p_dir, i)
            if block:
                measures['block'] = block
                with open('measures.json', 'w') as file:
                    json.dump(measures, file, indent=4)
            try:
                block = measures['block']
            except KeyError:
                pass

            if not cut or not block:
                print('Nothing modified on last sim.')
                return

        what = 'to compute/recompute observables'
        auth = authorization_request(what_to_do=what)

        if auth == 'yes':
            try:
                with open('measures.json', 'r') as file:
                    measures = json.load(file)
            except FileNotFoundError:
                measures = {}

            measures['volume'] = eval_volume(p_dir)
            measures['time'] = datetime.fromtimestamp(time()
                                        ).strftime('%d-%m-%Y %H:%M:%S')

            with open('measures.json', 'w') as file:
                json.dump(measures, file, indent=4)

        i += 1

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


def set_fit_props(name, points, config, remove):
    from os import chdir, popen
    from os.path import basename, dirname
    import json
    from lib.utils import (fit_dir, config_dir, point_dir, dir_point,
                           authorization_request)

    if remove:
        if points:
            print('Warning: points specification not compatible with --remove '
                  'option.')
            return
        elif config != 'test':
            print('Warning: config specification not compatible with --remove '
                  'option.')
            return

    chdir(fit_dir(name))

    try:
        with open('sims.json', 'r') as file:
            sims = json.load(file)
    except FileNotFoundError:
        sims = []

    # SIMS UPDATE

    if not remove:
        c_dir = config_dir(config)
        for Point in points:
            p_dir = c_dir + '/' + point_dir(Point)
            if p_dir not in sims:
                sims += [p_dir]

        with open('sims.json', 'w') as file:
            json.dump(sims, file, indent=4)

    # SIMS REMOTION

    else:
        new_sims = []
        for sim in sims:
            Point = dir_point(basename(sim))
            config = basename(dirname(sim))

            what = f"to remove sim from fit '{name}'"
            extra = f"\033[38;5;80m  config: '{config}'\033[0m"
            auth = authorization_request(Point=Point, what_to_do=what,
                                         extra_message=extra)

            if auth == 'quit':
                print('Nothing done for last sim.')
                return
            elif auth != 'yes':
                new_sims += [sim]
            else:
                print('Sim removed')

        with open('sims.json', 'w') as file:
            json.dump(new_sims, file, indent=4)

    # inserire un kind e aggiungere come possibilità quella di settare il tipo di osservabili
    # a cui è riferito il fit (1 sola)
    # cioè se è un fit: al volume, all'azione, alla carica topologica, ...

def info_fit(name, kind='sims'):
    from os import chdir
    from os.path import basename, dirname
    from pprint import pprint
    import json
    from lib.utils import fit_dir, config_dir, dir_point

    if kind in ['s', 'sims', None]:
        kind = 'sims'
    elif kind in ['o', 'obs']:
        kind = 'obs'

    chdir(fit_dir(name))

    try:
        with open('sims.json', 'r') as file:
            sims = json.load(file)
    except FileNotFoundError:
        print('No simulation already assigned to this fit.')

    d = {}
    for s in sims:
        if s[-1] == '/':
            s = s[:-1]

        if kind == 'sims':
            config = basename(dirname(s))
            Point = dir_point(basename(s))
            try:
                d[config] += [Point]
            except KeyError:
                d[config] = [Point]
        elif kind == 'obs':
            try:
                with open(s + '/measures.json', 'r') as file:
                    measures = json.load(file)
            except FileNotFoundError:
                measures = {}

            flags = ''
            if 'cut' in measures.keys():
                flags += 'C'
            if 'block' in measures.keys():
                flags += 'B'
            if 'volume' in measures.keys():
                flags += 'V'

            config = basename(dirname(s))
            Point = dir_point(basename(s))
            try:
                d[config] += [Point, flags]
            except KeyError:
                d[config] = [Point, flags]


    if kind == 'sims':
        pprint(d)
    elif kind == 'obs':
        pprint(d)
    else:
        raise ValueError('info-fit: kind {kind} not recognized')

    # inserire un kind e aggiungere come possibilità quella di visualizzare il tipo di osservabili
    # dato che ogni fit sarà un fit di 1 osservabile basterà un 'obs'
    # 'obs' attualmente è per le sole flag, ne va implementato uno più esteso con i valori opportuni

def sim_obs(points, config, plot):
    from os import chdir
    from os.path import isfile
    from time import time
    from datetime import datetime
    import json
    from pprint import pprint
    from lib.utils import config_dir, point_dir, authorization_request, eng_not
    from lib.analysis.fit import (set_cut, set_block, eval_volume,
                                  compute_torelons)

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

        if isfile(p_dir + '/max_volume_reached'):
            print(f'\033[38;5;41m(λ, β) = {Point}\033[0m skipped because '
                  '\033[38;5;80mmax_volume_reached\033[0m is present.')
            # print(f"\033[38;5;80m  config: '{config}'\033[0m")
            continue

        try:
            with open('state.json', 'r') as file:
                state = json.load(file)
        except FileNotFoundError:
            print(f'\033[1mCRITICAL:\033[0m no state.json file in sim'
                  f'\033[38;5;41m(λ, β) = {Point}\033[0m')
            return

        try:
            with open('measures.json', 'r') as file:
                measures = json.load(file)

            if 'cut' in measures.keys() and 'block' in measures.keys():
                cb_exist = True
            else:
                print(measures)
                cb_exist = False
        except FileNotFoundError:
            measures = {}
            cb_exist = False

        what = 'to select cut & block'
        extra = ('\033[92m(existing value present for both)\033[0m'
                 if cb_exist else None)
        auth = authorization_request(what_to_do=what, Point=Point,
                                     extra_message=extra)

        if auth == 'quit':
            print('Nothing done on the last sim.')
            return
        elif auth == 'yes':
            try:
                measures['cut'] = state['linear-history-cut']
                cut = state['linear-history-cut']
                with open('measures.json', 'w') as file:
                    json.dump(measures, file, indent=4)
                print("\033[38;5;80m'linear-history-cut'\033[0m "
                      "has been used as cut")
            except KeyError:
                cut = set_cut(p_dir, i)
                if cut:
                    measures['cut'] = cut
                    with open('measures.json', 'w') as file:
                        json.dump(measures, file, indent=4)
                try :
                    cut = measures['cut']
                except KeyError:
                    pass
            if cut:
                print(f'cut = {eng_not(cut)} ({cut})', end='   ')

            block = set_block(p_dir, i)
            if block:
                measures['block'] = block
                with open('measures.json', 'w') as file:
                    json.dump(measures, file, indent=4)
            try:
                block = measures['block']
            except KeyError:
                pass
            print(f'block = {eng_not(block)} {({block})}')

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
            measures['torelon-decay'] = compute_torelons(p_dir, plot)
            measures['time'] = datetime.fromtimestamp(time()
                                        ).strftime('%d-%m-%Y %H:%M:%S')

            with open('measures.json', 'w') as file:
                json.dump(measures, file, indent=4)
        elif auth == 'quit':
            print('Observables have not been recomputed.')
            return
        else:
            print('Observables have not been recomputed.')

        i += 1

def fit(name, kind='volume'):
    from os import chdir
    from os.path import basename, dirname, isfile
    from datetime import datetime
    import json
    from pprint import pprint
    from lib.utils import fit_dir, dir_point
    from lib.analysis.fit import fit_volume

    fit_d = fit_dir(name)
    chdir(fit_d)

    try:
        with open('sims.json', 'r') as file:
            sims = json.load(file)
    except FileNotFoundError:
        print('No simulation already assigned to this fit.')

    d = {}
    lambdas = []
    betas = []
    volumes = []
    sigma_vols = []
    for s in sims:
        if s[-1] == '/':
            s = s[:-1]

        config = basename(dirname(s))
        Point = dir_point(basename(s))

        if isfile(s + '/max_volume_reached'):
            print(f'\033[38;5;41m{Point}\033[0m not included in fit, because '
                  '\033[38;5;80mmax_volume_reached\033[0m is present.')
            print(f"\033[38;5;80m  config: '{config}'\033[0m")
            continue

        try:
            with open(s + '/measures.json', 'r') as file:
                measures = json.load(file)
        except FileNotFoundError:
            measures = {}

        with open(s + '/state.json', 'r') as file:
            state = json.load(file)

        s_time = datetime.strptime(state['end_time'], '%d-%m-%Y %H:%M:%S')
        m_time = datetime.strptime(measures['time'], '%d-%m-%Y %H:%M:%S')

        # print(Point)
        # print(s_time, type(s_time), '\n' + str(m_time), type(m_time))
        if(s_time > m_time):
            print('\033[38;5;203mWarning:\033[0m in Point '
                  f'\033[38;5;41m{Point}\033[0m in '
                  f"\033[38;5;80mconfig: '{config}'\033[0m measures are "
                  '\033[38;5;210mnot up to date\033[0m '
                  'with last simulation\'s data')
            print()

        d[Point] = {'config': config, **measures, 'time_sim_end': state['end_time']}

        if 'volume' in measures.keys():
            lambdas += [Point[0]]
            betas += [Point[1]]
            volumes += [measures['volume'][0]]
            sigma_vols += [measures['volume'][1]]
        else:
            print(f'Mising volume in {Point}, in config: {config}.')
            return

    with open('data.csv', 'w') as file:
        file.write('# Lambda Beta Volume Error Config\n')
        for Point, attr in d.items():
            vol, err = attr['volume']
            data = [Point[0], Point[1], vol, err, attr['config']]
            line = ' '.join([str(x) for x in data])
            file.write(line + '\n')

    fit_volume(lambdas, volumes, sigma_vols, betas)

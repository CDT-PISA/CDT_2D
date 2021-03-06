# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:46 2019

@author: alessandro
"""
def launch(points_old, points_new, config, linear_history, end_time, end_steps,
           force, time_lengths, adj, max_volume, move22, move24, move_gauge,
           fake_run, debug, queue, arch, file):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Parameters
    ----------
    points_old : type
        Description of parameter `points_old`.
    points_new : type
        Description of parameter `points_new`.
    config : type
        Description of parameter `config`.
    linear_history : type
        Description of parameter `linear_history`.
    time : type
        Description of parameter `time`.
    steps : type
        Description of parameter `steps`.
    force : type
        Description of parameter `force`.
    time_lengths : type
        Description of parameter `time_lengths`.
    fake_run : type
        Description of parameter `fake_run`.
    debug : type
        Description of parameter `debug`.

    Raises
    ------
    Exception
        descrizione dell'eccezione lanciata
    """

    from os import mkdir, chdir, getcwd, scandir
    from os.path import isfile, isdir
    from shutil import copyfile
    from re import split, sub
    from platform import node
    import json
    from lib.utils import (find_running, point_dir, point_str,
                           moves_weights, authorization_request, end_parser,
                           launch_script_name, make_script_name,
                           config_dir, project_folder)
    from lib.platforms import launch_run

    # set moves' weights
    move22, move24, move_gauge = moves_weights(move22, move24, move_gauge)

    points_run, _ = find_running()
    points_run = [x[0] for x in points_run if x[1] == config]

    points_old_auth = []   # old ones which will get the authorization to rerun
    points_req_run = []    # those requested which are already running
    for Point in points_old:
        if Point not in points_run:
            if not config == 'test' and not force:
                what_to_do = "to rerun simulation"
                authorized = authorization_request(what_to_do, Point)
            else:
                authorized = 'yes'
            if authorized == 'yes':
                points_old_auth += [Point]
            elif authorized == 'quit':
                print('No simulation launched.')
                return
        else:
            points_req_run += [Point]

    points = points_old_auth + points_new

    if len(points_new) > 0:
        print("New simulations will be launched for following (λ, β): ",
              points_new)
    if len(points_old_auth) > 0:
        print("Old simulations will be rerunned for following (λ, β): ",
              points_old_auth)
    if len(points_req_run) > 0:
        print("Simulations for following (λ, β) were already running: ",
              points_req_run)
    if len(points) > 0:
        print()

    arg_strs = {}

    for Point in points:
        chdir(config_dir(config))

        dir_name = point_dir(Point)
        launch_script_n = launch_script_name(Point)
        make_script_n = make_script_name(Point)

        if Point in points_old:
            if not isdir(dir_name + "/history/adjacencies"):
                mkdir(dir_name + "/history/adjacencies")

            with open(dir_name + "/state.json", "r+") as state_file:
                state = json.load(state_file)

            if state['is_thermalized']:
                print('((λ, β) = ' + str(Point) + ') Ha già finito!')
                # @todo da migliorare
                continue

            if state['last_run_succesful']:
                run_num = state['run_done'] + 1
            else:
                print('((λ, β) = ' + str(Point) + ') Problem in the last run')
                continue

            if state['is_thermalized'] and linear_history == '0':
                linear_history = '1M'

            # I'm putting the default because this case is present only for
            # backward compatibility, and before the timelength was stuck to 80
            try:
                time_length = state['timelength']
            except KeyError:
                time_length = time_lengths[Point]

            checkpoints = [x.name for x in scandir(dir_name + "/checkpoint")
                           if (split('_|\.|run', x.name)[1] == str(run_num - 1)
                           and x.name[-4:] != '.tmp')]
            # nell'ordinamento devo sostituire i '.' con le '~', o in generale
            # un carattere che venga dopo '_', altrimenti 'run1.1_...' viene
            # prima di 'run1_...'
            checkpoints.sort(key=lambda s: s.replace('.', '~'))
            last_check = checkpoints[-1]
        else:
            mkdir(dir_name)
            mkdir(dir_name + "/checkpoint")
            mkdir(dir_name + "/history")
            mkdir(dir_name + "/history/adjacencies")
            mkdir(dir_name + "/bin")

            make_template = project_folder() + '/lib/scripts/make_script.py'
            launch_template = project_folder() + '/lib/scripts/launch_script.py'
            copyfile(make_template, dir_name + '/' + make_script_n)
            copyfile(launch_template, dir_name + '/' + launch_script_n)

            if fake_run:
                print('Created simulation directory for: (Lambda= ' +
                      str(Point[0]) + ', Beta= ' + str(Point[1]) + ')')

            run_num = 1
            last_check = None
            time_length = time_lengths[Point]

        # devo farlo qui perché prima non sono sicuro che dir_name esista
        # ('mkdir(dir_name)')
        chdir(dir_name)

        if isfile('max_volume_reached'):
            print(f'Point {Point} won\'t be relaunched because it reached '
                  'maximum volume available in the previous run.')
            continue

        if int(run_num) > 1:
            from lib.tools import recovery_history
            recovery_history()

            if linear_history != '0' and not state['linear-history']:
                state['linear-history-cut'] = state['iter_done']
            if state['linear-history']:
                if linear_history == '0':
                    print('\033[38;5;69mWarning:\033[0m')
                    print(f"Point {Point} has been already run with "
                          f"linear_history {state['linear-history']}, so this "
                          f"value will be used.")
                elif linear_history != state['linear-history']:
                    print('\033[38;5;69mWarning:\033[0m')
                    print(f"Point {Point} has been already run with "
                          f"linear_history {state['linear-history']}, so this "
                          f"will be used instead of: {linear_history}.")
                linear_history = state['linear-history']

        # ensure state_file existence or update it
        if int(run_num) == 1:
            state = {'Lambda': Point[0], 'Beta': Point[1], 'run_done': 0,
                     'is_thermalized': False, 'last_checkpoint': None,
                     'iter_done': 0, 'timelength': time_length}

        with open('state.json', 'w') as state_file:
            json.dump(state, state_file, indent=4)

        # END CONDITION MANIPULATION

        # ricongiungo le due variabili perché è ancora facile
        # distinguerle dall'ultimo carattere
        if end_steps != '0':
            end_condition = end_steps
        else:
            end_condition = end_time

        # needed for thermalization loop
        end_partial, end_condition, end_type = end_parser(end_condition)

        if linear_history != '0':  # i.e. `if linear_history:`
            if end_type == 'time':
                end_partial = str(end_condition) + 's'
            else:
                end_partial = end_condition

        # set debug_flag for c++ (in c++ style)
        debug_flag = str(debug).lower()
        # set adj_flag for c++ (in c++ style)
        adj_flag = str(adj).lower()

        # max_volume
        max_volume = int(max_volume[0]
                         if type(max_volume) == list else max_volume)

        # is necessary to recompile each run because on the grid the launch node
        # could be different from run_node
        exe_name = "CDT_2D-" + point_str(Point) #+ "_run" + str(run_num)

        arguments = [project_folder(),
                     run_num,
                     Point[0],
                     Point[1],
                     time_length,
                     end_condition,
                     debug_flag,
                     last_check,
                     linear_history,
                     adj_flag,
                     move22,
                     move24,
                     max_volume,
                     end_partial,
                     end_type,
                     exe_name]
        arg_str = ''
        for x in arguments:
            arg_str += ' ' + str(x)
        arg_strs[Point] = arg_str

        if fake_run:
            print()
            print(*(["bin/" + exe_name] + arguments[:8]))

    if not fake_run:
        from lib.platforms import launch_run
        points = list(arg_strs.keys())
        launch_run(points, arg_strs, config, queue, arch, file)


def r_f(string, n):
    return string[:n].rjust(n)
def l_f(string, n):
    return string[:n].ljust(n)

def show_state(configs, full_show=False):
    # @todo: add support for the other platforms
    # @todo: for clusters: add 'pending' state
    import pickle
    import json
    from os import environ, popen
    from platform import node
    from datetime import datetime
    from time import time
    from lib.utils import find_running, point_dir, config_dir
    from lib.platforms import get_ps_out

    if not type(configs) == list:
        configs = [configs]

    # if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
    ps_out = get_ps_out()
    # else:
    #     ps_out = []
    #     print("This platform is still not supported")
    #     return

    empty = len(['' for line in ps_out if ' bin/CDT_2D-Lambda' in line]) == 0
    if len(ps_out) > 1 and not empty:
        print(' LAMBDA-λ    BETA-β      TIME     STATUS     CONFIG', end='')
        if full_show == '0':
            print()
        elif full_show == '1':
            print('   RUN_ID   PID      PPID')
        elif full_show == '2':
            print('     LIN_HIST   START     DISK US.')

        points_run_all, sim_all = find_running()

        configs += ['-']
        d = {}
        for config in configs:
            points_run_list = []
            sim_list = []
            for i in range(len(sim_all)):
                try:
                    if points_run_all[i][1] == config:
                        points_run_list += [points_run_all[i]]
                        sim_list += [sim_all[i]]
                except IndexError:
                    # It's possible that find_running can't retrieve the config
                    # for some simulations, these will be manged after
                    pass
            d[config] = points_run_list, sim_list

        # for i in range(len(sim_all)):
        #     if len(points_run_all[i]) == 1:
        #         points_run_list += [points_run_all[i] + ['-']]
        #         sim_list += [sim_all[i]]
        # d['-'] = points_run_list, sim_list

    else:
        print("There are no running simulations currently.")
        return

    for config in configs:
        try:
            if config == '-':
                raise FileNotFoundError

            with open(config_dir(config) + '/pstop.pickle', 'rb') as stop_file:
                points_stopped = pickle.load(stop_file)
        except FileNotFoundError:
            points_stopped = []

        if len(ps_out) > 1 and not empty:

            points_run_list, sim_list = d[config]

            for i in range(0, len(sim_list)):
                points_run = points_run_list[i]
                sim = sim_list[i]
                Point = points_run[0]
                l_conf = points_run[1]
                if Point in points_stopped:
                    state = 'killed'
                else:
                    state = 'running'
                print(r_f(str(Point[0]), 9), r_f(str(Point[1]), 9),
                      sim[0].rjust(11), ' ', state.ljust(10), l_conf.ljust(11),
                      end='')
                if full_show == '0':
                    print()
                elif full_show == '1':
                    print(sim[1].rjust(4), ' ', sim[2].ljust(8),
                          sim[3].ljust(8))
                elif full_show == '2':
                    if config != '-':
                        Point_dir = config_dir(config) + '/' + \
                                    point_dir(Point) + '/'
                        with open(Point_dir + 'state.json', 'r') as state_file:
                            state = json.load(state_file)
                        lin_hist = state['linear-history']
                        start = state['start_time']
                        disk_us = popen('du -hs ' + Point_dir).read().split()[0]
                    else:
                        lin_hist = '-'
                        start = '-'
                        disk_us = '-'
                    print(str(lin_hist).ljust(9), start[-8:].ljust(10),
                          disk_us.rjust(8))

            points_run = [x[0] for x in points_run_list if x[1] == config]
            l_aux = []
            for Point in points_stopped:
                if Point in points_run:
                    l_aux += [Point]
            points_stopped = l_aux
        else:
            points_stopped = []

        if config != '-':
            with open(config_dir(config) + '/pstop.pickle', 'wb') as stop_file:
                pickle.dump(points_stopped, stop_file)

    if len(ps_out) > 1 and not empty:
        clock = datetime.fromtimestamp(time()).strftime('%H:%M:%S')
        print('\n [CLOCK: ' + clock + ']')

def stop(points_old, config, is_all, pids, force):
    # @todo: distinguere fra processi 'data' e 'test'
    # si fa con un argomento config che viene da args.is_data
    from os import environ, system, popen
    import pickle
    from lib.utils import find_running, point_dir, config_dir

    points_run, sim_info = find_running()
    points_run = [x[0] for x in points_run if x[1] == config]
    # if config or not is_all:
    #     if not config:
    #         config = 'test'
    #     points_run = [x[0] for x in points_run if x[1] == config]
    # else:
    #     points_run = [x[0] for x in points_run]

    running_pids = [ps_i[2] for ps_i in sim_info]

    if pids:
        for pid in pids:
            if pid in running_pids or force:
                ps_out = popen('ps -fu ' + environ['USER']).read().split('\n')
                for line in ps_out[1:-1]:
                    infos = line.split()
                    ps_pid = int(infos[1])
                    ps_ppid = int(infos[2])
                    if ps_pid == pid or ps_ppid == pid:
                        if ps_ppid != 1:
                            system('kill ' + str(ps_ppid))
                        system('kill ' + str(ps_pid))
            else:
                print(f'Invalid PID: {pid}, ' +
                       'there is no running simulation with that one.')
        return

    try:
        with open(config_dir(config) + '/pstop.pickle', 'rb') as stop_file:
            points_stopped = pickle.load(stop_file)
    except FileNotFoundError:
        points_stopped = []

    l_aux = []
    for Point in points_stopped:
        if Point in points_run:
            l_aux += [Point]
    points_stopped = l_aux

    points_stopping = []
    points_notstop = []
    for Point in points_old:
        if Point in points_run and Point not in points_stopped:
            points_stopped += [Point]
            points_stopping += [Point]
            from os import system
            from time import time
            from datetime import datetime
            sf = '%d-%m-%Y %H:%M:%S'
            system('echo ' + datetime.fromtimestamp(time()).strftime(sf) +
                   ' > ' + config_dir(config) + '/' + point_dir(Point) +
                   '/stop')
            # forse '.stop' anzichè 'stop'
        else:
            points_notstop += [Point]

    with open(config_dir(config) + '/pstop.pickle', 'wb') as stop_file:
        pickle.dump(points_stopped, stop_file)

    if len(points_stopping) > 0:
        print("Simulations for following (λ, β) just stopped: ", points_stopping)
    if len(points_notstop) > 0 and not is_all:
        print("Simulations for following (λ, β) were not running: ",
              points_notstop)

def show(points_old, config, disk_usage=''):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Descrizione...

    Parameters
    ----------
    p1 : tipo
        descrizione del primo parametro p1

    Returns
    -------
    tipo
        descrizione del tipo di ritorno
    """
    from textwrap import wrap
    from numpy import histogram, median
    from lib.utils import eng_not, config_dir

    if len(points_old) == 0:
        print("There are no folders currently.")
    else:
        print('┌' + '─' * (len(config) + 9) + '┐')
        print('│ ' + config.upper() + ' CONFIG │')
        print('╰' + '─' * (len(config) + 9) + '┘\n')
        num = str(len(points_old))
        print("  " + num + " λ values in the range requested:")
        for x in wrap(str(points_old), width=65, initial_indent=' '*3,
                      subsequent_indent=' '*4):
            print(x)

        lambdas_old = [p[0] for p in points_old]

        if disk_usage == '':
            hist_lambda = histogram(lambdas_old, 20)
            highest = max(hist_lambda[0])

            print()
            for h in range(0, highest):
                for x in hist_lambda[0]:
                    if(x >= highest - h):
                        print(' X ', end='')
                    else:
                        print('   ', end='')
                print("")

            l_min = eng_not(min(lambdas_old))
            l_med = eng_not(median(lambdas_old))
            l_max = eng_not(max(lambdas_old))
            print(l_min, ' '*23, l_med, ' '*23, l_max)

        elif disk_usage == 'disk':
            from os import popen, chdir
            from lib.utils import color_mem, color_lambda

            chdir(config_dir(config))

            x = popen('du -hd 1').read().split('\n')
            x[:-1].sort(key=lambda x: x.split()[0])
            y = popen('du -hd 2 */checkpoint').read().split('\n')
            y[:-1].sort(key=lambda x: x.split()[0])
            z = popen('du -hd 2 */bin').read().split('\n')
            z[:-1].sort(key=lambda x: x.split()[0])
            a = popen('du -hd 2 */history').read().split('\n')
            a[:-1].sort(key=lambda x: x.split()[0])

            dim = []
            for i in range(len(x) - 2):
                w = x[i].split('\t./Lambda')
                v = y[i].split()
                u = z[i].split()
                t = a[i].split()
                s = ', '.join(w[1].split('_Beta'))
                dim += [[s, w[0], v[0], u[0], t[0]]]

            print('\n', ' '*3, '┌', '─'*56, '╮', sep='')
            print(' '*3, '│  POINT (λ, β)  │  SIZE  │  CHECK  │  BIN.  │  ',
                  'HISTORY  │', sep='')
            print(' '*3, '╰', '─'*16, '┼', '─'*8, '┼', '─'*9, '┼', '─'*8,
                   '┼', '─'*11, '┘', sep='')
            for l in dim:
                b = color_mem(l[1].ljust(4), size=True)
                c = color_mem(l[2].ljust(4))
                d = color_mem(l[3].ljust(4))
                e = color_mem(l[4].ljust(4))
                point = l[0].split(', ')
                x = '  ' + r_f(point[0], 7) + ', ' + point[1][:7]
                a = color_lambda(x.rjust(18), [b, c, d, e])
                print(a, ' │ ', b, ' │  ', c, ' │ ', d, ' │  ', e)
            print()
            print('The overall disk used is: ', x[-2].split()[0])

        elif disk_usage == 'num':
            from os import popen, chdir
            from lib.utils import color_mem, color_num, color_lambda

            chdir(config_dir(config))

            x = popen('du -hd 1').read().split('\n')

            dim = []
            for i in range(len(x) - 2):
                w = x[i].split('\t./Lambda')
                v = str(int(popen('ls -1q Lambda' + w[1] +
                                  '/checkpoint/ | wc -l').read()))
                u = str(int(popen('ls -1q Lambda' + w[1] +
                                  '/bin/ | wc -l').read()))
                s = ', '.join(w[1].split('_Beta'))
                dim += [[s, w[0], v, u]]
            dim.sort(key=lambda x: x[0])

            print('\n', ' '*3, '┌', '─'*44, '╮', sep='')
            print(' '*3, '│  POINT (λ, β)  │  SIZE  │  CHECK  │  BIN.  │',
                  sep='')
            print(' '*3, '╰', '─'*16, '┼', '─'*8, '┼', '─'*9, '┼', '─'*8,
                  '┘', sep='')
            for l in dim:
                b = color_mem(l[1].ljust(4), size=True)
                c = color_num(l[2].rjust(4))
                d = color_num(l[3].rjust(4))
                point = l[0].split(', ')
                x = '  ' + r_f(point[0], 7) + ', ' + point[1][:7]
                a = color_lambda(x.rjust(18), [b, c, d])
                print(a, ' │ ', b, ' │ ', c, '  │ ', d)
            print()

def plot(points_old, config, gauge=False):
    from matplotlib.pyplot import figure, show
    import numpy as np
    from lib.utils import find_running, point_dir, config_dir

    points_run, _ = find_running()
    points_run = [x[0] for x in points_run if x[1] == config]
    color_cycle = ['xkcd:carmine', 'xkcd:teal', 'xkcd:peach', 'xkcd:mustard',
                   'xkcd:cerulean']
    n_col = len(color_cycle)

    canvases = []
    props = []
    i = -1
    for Point in points_old:
        i += 1

        Lambda = Point[0]
        Beta = Point[1]

        if not gauge:
            vol_file = (config_dir(config) + '/' + point_dir(Point) +
                        '/history/volumes.txt')
            indices, volumes = np.loadtxt(vol_file, unpack=True)
            file = vol_file
        else:
            vol_file = (config_dir(config) + '/' + point_dir(Point) +
                        '/history/volumes.txt')
            v_indices, volumes = np.loadtxt(vol_file, unpack=True)
            gauge_file = (config_dir(config) + '/' + point_dir(Point) +
                        '/history/gauge.txt')
            g_indices, gauge_action, topological_charge, \
                 av_contr = np.loadtxt(gauge_file, unpack=True)

            v_indices = tuple([np.searchsorted(v_indices, g_indices)])

            indices = g_indices
            volumes = 6 * (gauge_action / volumes[v_indices]) / Beta
            file = gauge_file

        fig = figure()
        ax = fig.add_subplot(111)
        props += [{'fig': fig, 'ax': ax, 'skip': len(volumes),
                  'file': file}]
        canvases += [fig.canvas]

        fig.set_size_inches(7, 5)
        ax.plot(indices, volumes, color=color_cycle[i % n_col])
        if Point in points_run:
            run_t = ', running'
        else:
            run_t = ''

        title = 'λ = ' + str(Point[0]) + ', β = ' + str(Point[1]) + run_t
        if gauge:
            title = 'average plaquette\n' + title
        ax.set_title(title)

        def on_key(event):
            i = canvases.index(event.canvas)
            p = props[i]
            if event.key == 'f5':
                try:
                    ind_aux, vol_aux = np.loadtxt(p['file'], unpack=True,
                                               skiprows=p['skip'])
                except ValueError:
                    ind_aux = []
                    vol_aux = []

                try:
                    if len(vol_aux) > 10:
                        props[i]['skip'] += len(vol_aux)
                        p['ax'].plot(ind_aux, vol_aux,
                                     color=color_cycle[i % n_col])
                        p['fig'].canvas.draw()
                except TypeError:
                    pass

        if not gauge:
            fig.canvas.mpl_connect('key_press_event', on_key)

    show()

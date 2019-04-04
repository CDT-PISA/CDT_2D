#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

#Created on Fri Mar 15 11:18:52 2019
"""
"""

from os import chdir, scandir
from lib.utils import find_running
    
def data(lambdas_old, lambdas_new, config, linear_history, time, steps):
    from lib.data import launch
    launch(lambdas_old, lambdas_new, config, linear_history, time, steps)

def show(lambdas_old, lambdas_new):
    from lib.data import show
    show(lambdas_old, lambdas_new)
    
def clear(lambdas_old, lambdas_new, config):
    from lib.utils import clear_data
    
    clear_data(lambdas_old, config)
    if len(lambdas_new) > 0:
        print("Following lambdas not found: ", lambdas_new)

def state(configs, full_show=False):
    from lib.utils import show_state
    show_state(configs, full_show)
              
def stop(lambdas_old, lambdas_new, config):
    # @todo: distinguere fra processi 'data' e 'test'
    # si fa con un argomento config che viene da args.is_data
    import pickle
    
    lambdas_run, sim_info = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
        
    try:
        with open('output/' + config + '/pstop.pickle','rb') as stop_file:
            lambdas_stopped = pickle.load(stop_file)
    except FileNotFoundError:
        lambdas_stopped = []
        
    l_aux = []
    for Lambda in lambdas_stopped:
        if Lambda in lambdas_run:
            l_aux += [Lambda]
    lambdas_stopped = l_aux
            
    for Lambda in lambdas_run:
        if Lambda in lambdas_old and not Lambda in lambdas_stopped:
            lambdas_stopped += [Lambda]
            from os import system
            from time import time
            from datetime import datetime
            sf = '%d-%m-%Y %H:%M:%S'
            system('echo ' + datetime.fromtimestamp(time()).strftime(sf) +
                   ' > output/' + config + '/Lambda' + str(Lambda) + '/stop')
            # forse '.stop' anzichè 'stop'
    
    with open('output/' + config + '/pstop.pickle','wb') as stop_file:
            pickle.dump(lambdas_stopped, stop_file)
    
def recovery(lambdas_old, lambdas_new, config):
    from lib.utils import recovery_history
    
    for Lambda in lambdas_old:
        chdir('output/' + config + '/Lambda' + str(Lambda))
        recovery_history()
        
def info(lambdas_old, config):
    from lib.utils import sim_info
    
    if len(lambdas_old) == 0:
        print("Lambda non trovato") # da migliorare
    elif len(lambdas_old) == 1:
        sim_info(lambdas_old[0], config)
    else:
        print()
        
def therm(lambdas_old, config, is_therm):
    import json
    
    for Lambda in lambdas_old:
        filename = 'output/' + config + '/Lambda' + str(Lambda) + '/state.json'
        with open(filename, 'r') as state_file:
            state = json.load(state_file)
            state['is_thermalized'] = eval(is_therm)
            
        with open(filename, 'w') as state_file:
            json.dump(state, state_file, indent=4)
        
def plot(lambdas_old, lambdas_new, config):
    from matplotlib.pyplot import subplots, show
    from numpy import loadtxt
    
    indices, volumes = loadtxt('output/' + config + '/Lambda' + str(lambdas_old[0]) + 
                               '/history/volumes.txt', unpack=True)
    
    fig, ax = subplots()
    ax.plot(indices, volumes, color='xkcd:carmine')
    
    def on_key(event):
        if event.key == 'f5':
            ind_aux, vol_aux = loadtxt('output/' + config + '/Lambda' +
                                       str(lambdas_old[0]) + '/history/volumes.txt', 
                                       unpack=True, skiprows=on_key.skip)
            
            if type(vol_aux) != float and len(vol_aux) > 5:
                on_key.skip += len(vol_aux)
                ax.plot(ind_aux, vol_aux, color='xkcd:carmine')
                fig.canvas.draw()
    on_key.skip = len(volumes)

    fig.canvas.mpl_connect('key_press_event', on_key)
    show()
    
def lambdas_recast(lambda_list, is_range=False, is_all=False, 
                   config='test', cmd=show):
    from lib.utils import find_all_availables
    
    if len(lambda_list) == 0 and cmd == 'show':
        is_all = True
        
    lambdas = []
    lambdas_old = []
    lambdas_new = []
    all_lambdas = find_all_availables(config)
    
    if is_all:
        lambdas_old = all_lambdas
    else:
        if is_range:
            if len(lambda_list) == 2:
                extremes = lambda_list
                lambdas_old = [x for x in all_lambdas \
                               if x >= extremes[0] and x <= extremes[1]]
            elif len(lambda_list) == 3:                
                from numpy import linspace
                lambdas = list(linspace(*lambda_list))
            else:
                raise ValueError('Testo da scrivere (#arg è quello di un range!)')
        else:
            lambdas = lambda_list
            
    if len(lambdas) > 0:
        lambdas_old = [x for x in lambdas if x in all_lambdas]
        lambdas_new = [x for x in lambdas if x not in lambdas_old]
            
    return lambdas_old, lambdas_new
    
import sys
import argparse
from os.path import expanduser
from platform import node

if(node() == 'Paperopoli'):
    import argcomplete

def main():

    chdir(expanduser('~/projects/CDT_2D'))
    
    parser = argparse.ArgumentParser(description='Manage CDT_2D simulations.')
    
    # todo: devo scriverci gli esempi di come si lancia
    #   tipo senza nulla con un numero
    #   oppure il tipo di numeri
    # migliorare la descrizione di ogni comando
    
    # to add: clear_bin (with argument '°' or the possibility of pass lambdas)
    
    sys.argv = [x if x != '°' else '-°' for x in sys.argv]
    sys.argv = [x if x != '@' else '-@' for x in sys.argv]
    
    # SUBPARSERS
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = False
    
    parser.add_argument('--version', action='version', version='CDT_2D 0.2')
    configs = [x.name for x in scandir('output') if x.is_dir()]
    
    # run command
    
    run_sub = subparsers.add_parser('run', help='run')
    run_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    run_sub.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    run_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    run_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    run_sub.add_argument('--linear-history', default='0',
                        help="it takes an integer argument, that if set greater \
                        then zero let data points be saved at regular intervals, \
                        instead of at increasing ones (units: {k,M,G}) \
                        | ex: --linear-history 2k")
    #run_sub.add_argument('--log-history', dest='linear_history', 
    #               action='store_false', 
    #               help="if set data points are saved at increasing intervals")
    end_conditions = run_sub.add_mutually_exclusive_group()
    end_conditions.add_argument('--time', default='30m', 
                                help='if set it specifies the duration of the run \
                                (default: 30 minutes, units: {s,m,h}) | \
                                ex: --time 2h')
    end_conditions.add_argument('--steps', default='0',
                                help='if set it specifies the length of the run \
                                in MC steps (is not the default, units: {k,M,G}) \
                                | ex: --steps 200M')
    
    # state command
    class ConfigAction(argparse.Action):
        def __init__(self, option_strings, dest, ifcall, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ConfigAction, self).__init__(option_strings, dest, nargs='?',
                 **kwargs)
            self.ifcall = ifcall
        def __call__(self, parser, namespace, values, option_string=None):
            if values == None:
                setattr(namespace, self.dest, self.ifcall)
            else:
                setattr(namespace, self.dest, values)
    
    state_sub = subparsers.add_parser('state', help='state')
    state_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    state_sub.add_argument('-c', '--config', choices=configs, default=configs,
                           ifcall='test', action=ConfigAction, help='config')
    state_sub.add_argument('-f', '--full-show', action='store_true',
                           help='full-show')
    
    # stop command
    
    stop_sub = subparsers.add_parser('stop', help='stop')
    stop_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    lambdas = stop_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    stop_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    stop_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # show command
    
    show_sub = subparsers.add_parser('show', help='show')
    show_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    lambdas = show_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    show_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    show_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # clear command
    
    clear_sub = subparsers.add_parser('clear', help='clear')
    clear_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    lambdas = clear_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    clear_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    clear_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # recovery command
    
    recovery_sub = subparsers.add_parser('recovery', help='recovery')
    recovery_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    lambdas = recovery_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    recovery_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    recovery_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # info command
    
    info_sub = subparsers.add_parser('info', help='info')
    info_sub.add_argument('lambdas', metavar='L', nargs=1, type=float, 
                         help='lambdas')
    info_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    info_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # thermalization command
    
    therm_sub = subparsers.add_parser('therm', help='therm')
    therm_sub.add_argument('lambdas', metavar='L', nargs='+', type=float, 
                         help='lambdas')
    therm_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    therm_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    therm_sub.add_argument('-t', '--is-therm', default='True', 
                           choices=['True', 'False'], help='thermalization')
    
    # plot command
    
    plot_sub = subparsers.add_parser('plot', help='plot')
    plot_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='lambdas')
    plot_sub.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    plot_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    plot_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    
    if args.is_data:
        args.config = 'data'
    
    if not hasattr(args, 'lambdas'):
        lambdas = []
    else:
        lambdas = args.lambdas 
    if not hasattr(args, 'is_all'):
        args.is_all = False
    if not hasattr(args, 'is_range'):
        args.is_range = False
    
    if not args.command == 'state':
        lambdas_old, lambdas_new = lambdas_recast(lambdas, args.is_range, 
                                                  args.is_all, args.config,
                                                  args.command)
        
    if args.command == 'run':
        data(lambdas_old, lambdas_new, args.config, args.linear_history,
             args.time, args.steps)
        
    elif args.command == 'state':
#        print(args)
        state(args.config, args.full_show)
    
    elif args.command == 'stop':
        stop(lambdas_old, lambdas_new, args.config)
        
    elif args.command == 'show':
        show(lambdas_old, lambdas_new)
        
    elif args.command == 'clear':
        clear(lambdas_old, lambdas_new, args.config)
    
    elif args.command == 'recovery':
        recovery(lambdas_old, lambdas_new, args.config)
        
    elif args.command == 'info':
        info(lambdas_old, args.config)
    
    elif args.command == 'therm':
        therm(lambdas_old, args.config, args.is_therm)
    
    elif args.command == 'plot':
        plot(lambdas_old, lambdas_new, args.config)
            
if __name__ == "__main__":
    main()

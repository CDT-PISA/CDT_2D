#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

#Created on Fri Mar 15 11:18:52 2019
"""
"""

from platform import node
from os import chdir, popen, system
from os.path import expanduser
from numpy import linspace
from lib.utils import find_all_availables, find_running
# @todo
from lib.utils import recovery_history, clear_data
import lib.test as test_cdt
    
def data(lambdas_old, lambdas_new, config, linear_history, time, steps):
    test_cdt.launch(lambdas_old, lambdas_new, config, linear_history, time, steps)

def show(lambdas_old, lambdas_new):
    test_cdt.show(lambdas_old, lambdas_new)
    
def clear(lambdas_old, lambdas_new, config):
    clear_data(lambdas_old, config)
    if len(lambdas_new) > 0:
        print("Following lambdas not found: ", lambdas_new)

def state(config, full_show=False):
    # @todo: add support for the other platforms
    # @todo: for clusters: add 'pending' state
    # @todo: show only for one config
    # @todo: quando sarà implementato a subparser aggiungere anche 'entrambi
    # le config' come opzione, e in quel caso deve stampare un campo in più
    # per dire a quale config appartiene
    import pickle
    
    if not type(config) == list:
        config = [config]
    
    for config in config:
        try:
            with open('output/' + config + '/pstop.pickle','rb') as stop_file:
                lambdas_stopped = pickle.load(stop_file)
        except FileNotFoundError:
            lambdas_stopped = []
        
        if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
            ps_out = popen('ps -f').read().split('\n')
        else:
            ps_out = []
            print("This platform is still not supported")
        
        empty = len([1 for line in ps_out if 'CDT_2D-Lambda' in line]) == 0
        if len(ps_out) > 1 and not empty:
            lambdas_run = []
            print('  LAMBDA\t  TIME\t\t STATUS', end='')
            if not full_show:
                print()
            else:
                print('\t    RUN_ID \t PID')
                
            for line in ps_out[1:]:
                if 'CDT_2D-Lambda' in line:
                    pinfos = line.split()
                    Lambda = float(pinfos[-6])
                    start_time = pinfos[6]
                    lambdas_run += [Lambda]
                    if Lambda in lambdas_stopped:
                        state = 'killed'
                    else:
                        state = 'running'
                    print(str(Lambda).rjust(10), '\t', start_time, '\t', state,
                          end='')
                    if not full_show:
                        print()
                    else:
                        PID = int(pinfos[1])
                        run_id = pinfos[8]
                        print(' ', run_id.rjust(8), '\t', PID)
                        
            l_aux = []
            for Lambda in lambdas_stopped:
                if Lambda in lambdas_run:
                    l_aux += [Lambda]
            lambdas_stopped = l_aux
        else:
            lambdas_stopped = []
        
        with open('output/' + config + '/pstop.pickle','wb') as stop_file:
                pickle.dump(lambdas_stopped, stop_file)
              
def stop(lambdas_old, lambdas_new, config):
    # @todo: distinguere fra processi 'data' e 'test'
    # si fa con un argomento config che viene da args.is_data
    import pickle
    
    lambdas_run = find_running()
        
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
            from time import time
            from datetime import datetime
            sf = '%d-%m-%Y %H:%M:%S'
            system('echo ' + datetime.fromtimestamp(time()).strftime(sf) +
                   ' > output/' + config + '/Lambda' + str(Lambda) + '/stop')
            # forse '.stop' anzichè 'stop'
    
    with open('output/' + config + '/pstop.pickle','wb') as stop_file:
            pickle.dump(lambdas_stopped, stop_file)
    
def recovery(lambdas_old, lambdas_new, config):
    for Lambda in lambdas_old:
        chdir('output/' + config + '/Lambda' + str(Lambda))
        recovery_history()
    
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
    # @todo: quando sarà implementato a subparser '--show'
    # avrà is_all = True di default
    if len(lambda_list) == 0 and cmd == show:
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
    
    # commands (mutually exclusive)
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument('-r', '--run', dest='my_command', action='store_const', 
                       default=data, const=data, help='run')
    group.add_argument('-s', '--show', dest='my_command', action='store_const', 
                       const=show, help='show')
    group.add_argument('-c', '--clear', dest='my_command', action='store_const', 
                       const=clear, help='clear')
    group.add_argument('--state', dest='my_command', action='store_const', 
                       const=state, help='state')
    group.add_argument('--stop', dest='my_command', action='store_const', 
                       const=stop, help='stop')
    group.add_argument('--recovery', dest='my_command', action='store_const', 
                       const=recovery, help='recovery')
    group.add_argument('--plot', dest='my_command', action='store_const', 
                       const=plot, help='plot')
    
    group.add_argument('--version', action='version', version='CDT_2D 0.0')
    
    # lambdas
    parser.add_argument('lambdas', metavar='L', nargs='*', type=float, help='lambdas')
    
    parser.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    
    lambdas_specs = parser.add_mutually_exclusive_group()
    lambdas_specs.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    lambdas_specs.add_argument('--range', dest='is_range', 
                                    action='store_true', help='range')
        
    # additional flags
    parser.add_argument('--linear-history', default='0',
                        help="it takes an integer argument, that if set greater \
                        then zero let data points be saved at regular intervals, \
                        instead of at increasing ones (units: {k,M,G}) \
                        | ex: --linear-history 2k")
    #parser.add_argument('--log-history', dest='linear_history', action='store_false',
    #                    help="if set data points are saved at increasing intervals")
    
    end_conditions = parser.add_mutually_exclusive_group()
    end_conditions.add_argument('--time', default='30m', 
                                help='if set it specifies the duration of the run \
                                (default: 30 minutes, units: {s,m,h}) | \
                                ex: --time 2h')
    end_conditions.add_argument('--steps', default='0',
                                help='if set it specifies the length of the run \
                                in MC steps (is not the default, units: {k,M,G}) \
                                | ex: --steps 200M')

    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    
    cmds = [data, show, clear, stop, recovery, plot]
    if args.is_data:
        config = 'data'
    else:
        config = 'test'
        
    if args.my_command in cmds:
        lambdas = args.lambdas
        if lambdas == None:
            lambdas = []
        
        lambdas_old, lambdas_new = lambdas_recast(lambdas, args.is_range, 
                                                  args.is_all, config,
                                                  args.my_command)
        
        if args.my_command == data:
            data(lambdas_old, lambdas_new, config, args.linear_history,
                 args.time, args.steps)
        elif args.my_command == show:
            show(lambdas_old, lambdas_new)
        elif args.my_command == clear:
            clear(lambdas_old, lambdas_new, config)
        else:
            args.my_command(lambdas_old, lambdas_new, config)
    elif args.my_command == state:
        state(config)
            
if __name__ == "__main__":
    main()

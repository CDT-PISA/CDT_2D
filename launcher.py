#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

#Created on Fri Mar 15 11:18:52 2019
"""
"""

__all__ = []
__version__ = '0.2'
__author__ = 'Alessandro Candido'

# Useful on running

def data(lambdas_old, lambdas_new, config, linear_history, time, steps,
         force, timelength):
    from lib.data import launch
    launch(lambdas_old, lambdas_new, config, linear_history, time, steps,
           force, timelength)

def state(configs, full_show=False):
    from lib.data import show_state
    show_state(configs, full_show)

def stop(lambdas_old, lambdas_new, config, is_all):
    from lib.data import stop
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
    stop(lambdas_old, config, is_all)
    
# Useful offline
    
def show(lambdas_old, config, disk_usage):
    from lib.data import show
    show(lambdas_old, config, disk_usage)
            
def plot(lambdas_old, lambdas_new, config):
    from lib.data import plot
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
    if len(lambdas_old) > 0:
        print()
    plot(lambdas_old, config)
    
def fit(lambdas_old, lambdas_new, config, skip):
    from lib.analysis import fit
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
    fit(lambdas_old, config, skip)

# Utilities

def recovery(lambdas_old, lambdas_new, config, force, very_forced):
    from os import getcwd, chdir
    from lib.tools import recovery_history
    from lib.utils import authorization_request
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_news)
        if len(lambdas_old) > 0:
            print()
    
    proj_dir = getcwd()
    
    for Lambda in lambdas_old:
        if not config == 'test' and not force:
            what_to_do = "to recovery simulation data"
            authorized = authorization_request(what_to_do, Lambda)
        else:
            authorized = True
        if authorized:
            chdir('output/' + config + '/Lambda' + str(Lambda))
            recovery_history(very_forced)
            chdir(proj_dir) 
        
def info(lambdas_old, config):
    from lib.tools import sim_info
    
    if len(lambdas_old) == 0:
        print("λ not found") # da migliorare
    elif len(lambdas_old) == 1:
        sim_info(lambdas_old[0], config)
        
def therm(lambdas_old, lambdas_new, config, is_therm, force):
    from lib.tools import therm
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
        if len(lambdas_old) > 0:
            print()
    therm(lambdas_old, config, is_therm, force)
            
def up_launch(lambdas_old, lambdas_new, config, both, make, force):
    from lib.tools import up_launch
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
        if len(lambdas_old) > 0:
            print()
    up_launch(lambdas_old, config, both, make, force)
    
def remove(lambdas_old, lambdas_new, config, force, cbin, check):
    from lib.tools import remove
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
        if len(lambdas_old) > 0:
            print()
    remove(lambdas_old, config, force, cbin, check)
    
def remote(lambdas_old, lambdas_new, config, upload, download, force, rshow):
    from os import popen
    import json
    from lib.tools import remote
    
    try:
        config_file = open('config.json', 'r')
        proj_configs = json.load(config_file)
        exist = True
    except FileNotFoundError:
        exist = False
    
    rclone_remote = proj_configs['rclone_remote']
    remote_path = proj_configs['rclone_path']
    if not exist or rclone_remote == None:
        print("No valid remote found.")
        return
    
    # @todo: scrivere nell'help che serve che nel remote ci si almeno il
    # path valido
    print('checking remote...')
    path_content = popen('rclone lsd ' + rclone_remote + ':' +
                         remote_path).read()
    if not 'CDT_2D' in path_content:
        print('No valid remote found (is also possible that only the ' + 
              'specified path is wrong).')
        return
    
    remote(lambdas_old, lambdas_new, config, upload, download, force, rshow)
    
def config(email, remote, path, show):
    from lib.tools import config
    
    # @todo: scrivere in qualche help di usare `tools remote` senza argomenti
    # per testare la validità del path inserito
    config(email, remote, path, show)
    
def new_conf(name):
    from lib.tools import new_conf
    
    new_conf(name[0])
    
def reset_conf(name, delete=False):
    from lib.tools import reset_conf
    
    reset_conf(name, delete)

def clear(lambdas_old, lambdas_new, config, force):
    from lib.tools import clear_data
    
    if len(lambdas_new) > 0:
        print("Following λ not found: ", lambdas_new)
    clear_data(lambdas_old, config, force)
    
import sys
import argparse
from os import chdir, scandir
from os.path import dirname, realpath
from platform import node

if(node() == 'Paperopoli'):
    import argcomplete

def main():
    chdir(dirname(realpath(__file__)))
    
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
    
    parser.add_argument('--version', action='version', version='CDT_2D ' +
                        'Pure Gravity: ' + __version__)
    configs = [x.name for x in scandir('output') if x.is_dir()]
    
    # run command
    
    run_sub = subparsers.add_parser('run', help='run')
    run_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    run_sub.add_argument('-g', '--gym', metavar='g', nargs='*', type=float, 
                         help='g_ym values')
    run_sub.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    run_sub.add_argument('-@', dest='is_data', action='store_true', 
                         help="data configuration flag \
                         (the '-' in front is not needed)")
    run_sub.add_argument('-c', '--config', choices=configs, default='test',
                          help='config')
    run_sub.add_argument('-f', '--force', action='store_true', help='force')
    run_sub.add_argument('--timelength', nargs=1, type=int,
                         default=80, help='set timelength')
    run_sub.add_argument('--lin', '--linear-history', dest='linear_history', 
                        default='0',
                        help="it takes an integer argument, that if set \
                        greater then zero let data points be saved at regular \
                        intervals, instead of at increasing ones (units: \
                        {k,M,G}) | ex: --linear-history 2k")
    #run_sub.add_argument('--log-history', dest='linear_history', 
    #               action='store_false', 
    #               help="if set data points are saved at increasing intervals")
    end_conditions = run_sub.add_mutually_exclusive_group()
    end_conditions.add_argument('--time', default='30m', 
                                help='if set it specifies the duration of the \
                                run (default: 30 minutes, units: {s,m,h}) | \
                                ex: --time 2h')
    end_conditions.add_argument('--steps', default='0',
                                help='if set it specifies the length of the \
                                run in MC steps (is not the default, units: \
                                | ex: --steps 200M')
    
    # state command
    class ToggleChoiceAction(argparse.Action):
        def __init__(self, option_strings, dest, ifcall, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ToggleChoiceAction, self).__init__(option_strings, dest,
                 nargs='?', **kwargs)
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
                           ifcall='test', action=ToggleChoiceAction, 
                           help='config')
    state_sub.add_argument('-f', '--full-show', choices=['1','2'], default='0',
                           ifcall='1', action=ToggleChoiceAction, 
                           help='full-show')
    
    # stop command
    
    stop_sub = subparsers.add_parser('stop', help='stop')
    stop_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    run_sub.add_argument('-g', '--gym', metavar='g', nargs='*', type=float, 
                         help='g_ym values')
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
                         help='λ values')
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
    show_sub.add_argument('-d', '--disk-usage', default='', const='disk',
                          action='store_const', help='show disk usage')
    show_sub.add_argument('-n', '--number', dest='disk_usage', const='num',
                          action='store_const', help='show number of files')
    
    # plot command
    
    plot_sub = subparsers.add_parser('plot', help='plot')
    plot_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    plot_sub.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    plot_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    plot_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # fit command
    
    fit_sub = subparsers.add_parser('fit', help='fit')
    fit_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    lambdas = fit_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    fit_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    fit_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    fit_sub.add_argument('-s', '--skip', action='store_true', help='skip')
    
    # utilities subparser
    
    tools = subparsers.add_parser('tools', help='tools for simulation\
                                  management')
    tools_sub = tools.add_subparsers(dest='tools')
    
    # recovery command
    
    recovery_sub = tools_sub.add_parser('recovery', help='recovery')
    recovery_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
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
    recovery_sub.add_argument('-f', '--force', action='store_true', help='force')
    recovery_sub.add_argument('-F', '--FORCE', action='store_true', 
                              help='very forced')
    
    # info command
    
    info_sub = tools_sub.add_parser('info', help='info on a sim')
    info_sub.add_argument('lambdas', metavar='L', nargs=1, type=float, 
                         help='λ values')
    info_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    info_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    
    # thermalization command
    
    therm_sub = tools_sub.add_parser('set-therm', help='set thermalisation')
    therm_sub.add_argument('lambdas', metavar='L', nargs='+', type=float, 
                         help='λ values')
    therm_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    therm_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    therm_sub.add_argument('-f', '--force', action='store_true', help='force')
    therm_sub.add_argument('-t', '--is-therm', default='True', 
                           choices=['True', 'False'], help='thermalization')
    
    # thermalization command
    
    launch_sub = tools_sub.add_parser('up-launch', 
                                     help='update launch/make_script')
    launch_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    lambdas = launch_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    launch_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    launch_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    launch_sub.add_argument('-f', '--force', action='store_true', help='force')
    script = launch_sub.add_mutually_exclusive_group()
    script.add_argument('-m', '--make', action='store_true',
                        help='update make_script instead')
    script.add_argument('-b', '--both', action='store_true',
                        help='update both launch_script and make_script')
    
    # autoremove command
    
    remove_sub = tools_sub.add_parser('autoremove', help='autoremove')
    remove_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    lambdas = remove_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    remove_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    remove_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    remove_sub.add_argument('-f', '--force', action='store_true', help='force')
    what = remove_sub.add_mutually_exclusive_group()
    what.add_argument('--bin', ifcall='0', action=ToggleChoiceAction, 
                      help='remove older bins')
    what.add_argument('--check', ifcall='0', action=ToggleChoiceAction, 
                      help='remove older checkpoints')
    
    # upload/download command
    
    remote_sub = tools_sub.add_parser('remote', 
                                     help='upload/download sim dirs')
    remote_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
    lambdas = remote_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', dest='is_range', action='store_true', 
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true', 
                                    help="all (the '-' in front is not needed)")
    remote_sub.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag \
                        (the '-' in front is not needed)")
    remote_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    remote_sub.add_argument('-f', '--force', action='store_true', help='force')
    load = remote_sub.add_mutually_exclusive_group()
    load.add_argument('-u', '--upload', action='store_true',
                        help='update make_script instead')
    load.add_argument('-d', '--download', action='store_true',
                        help='update both launch_script and make_script')
    load.add_argument('-s', '--show', action='store_true',
                        help='show list of sims on remote')
    
    # config command
    
    config_sub = tools_sub.add_parser('config', help='edit project\'s \
                                      configuration file')
    configs_arg = config_sub.add_mutually_exclusive_group()
    configs_arg.add_argument('-e', '--email', action=ToggleChoiceAction, 
                         default=None, ifcall='-', help='set receiver email')
    configs_arg.add_argument('-r', '--remote', action=ToggleChoiceAction, 
                         default=None, ifcall='-', help='set rclone remote')
    configs_arg.add_argument('-p', '--path', action=ToggleChoiceAction, 
                         default=None, ifcall='-', help='set rclone path')
    config_sub.add_argument('-s', '--show', action='store_true',
                         help='show config_file')
    
    # new configuration command
    
    new_conf_sub = tools_sub.add_parser('new-conf', help='create new config')
    new_conf_sub.add_argument('name', nargs=1, type=str)
    
    # reset configuration command
    
    reset_conf_sub = tools_sub.add_parser('reset', help='reset or delete config')
    reset_conf_sub.add_argument('name', choices=configs)
    reset_conf_sub.add_argument('-d', '--delete', action='store_true',
                                help='defintely delete config')
    
    # clear command
    
    clear_sub = tools_sub.add_parser('clear', help='clear')
    clear_sub.add_argument('lambdas', metavar='L', nargs='*', type=float, 
                         help='λ values')
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
    clear_sub.add_argument('-f', '--force', action='store_true', help='force')
    
    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    
    if not hasattr(args, 'lambdas'):
        lambdas = []
    else:
        lambdas = args.lambdas 
    if not hasattr(args, 'is_data'):
        args.is_data = False
    if not hasattr(args, 'config'):
        args.config = 'test'
    if not hasattr(args, 'is_all'):
        args.is_all = False
    if not hasattr(args, 'is_range'):
        args.is_range = False
        
    if args.is_data:
        args.config = 'data'
    
    if not args.command == 'state':
        from lib.utils import lambdas_recast
        lambdas_old, lambdas_new = lambdas_recast(lambdas, args.is_range, 
                                                  args.is_all, args.config,
                                                  args.command)
        
    if args.command == 'run':
        data(lambdas_old, lambdas_new, args.config, args.linear_history,
             args.time, args.steps, args.force, args.timelength)
        
    elif args.command == 'state':
        state(args.config, args.full_show)
    
    elif args.command == 'stop':
        stop(lambdas_old, lambdas_new, args.config, args.is_all)
        
    elif args.command == 'show':
        show(lambdas_old, args.config, args.disk_usage)
        
    elif args.command == 'fit':
        fit(lambdas_old, lambdas_new, args.config, args.skip)
    
    elif args.command == 'tools':
        if args.tools == 'recovery':
            recovery(lambdas_old, lambdas_new, args.config, args.force,
                     args.FORCE)
        elif args.tools == 'info':
            info(lambdas_old, args.config)
        elif args.tools == 'set-therm':
            therm(lambdas_old, lambdas_new, args.config, args.is_therm,
                  args.force)
        elif args.tools == 'up-launch':
            up_launch(lambdas_old, lambdas_new, args.config, 
                      args.both, args.make, args.force)
        if args.tools == 'autoremove':
            remove(lambdas_old, lambdas_new, args.config, args.force,
                       args.bin, args.check)
        elif args.tools == 'remote':
            remote(lambdas_old, lambdas_new, args.config, 
                      args.upload, args.download, args.force, args.show)
        elif args.tools == 'config':
            config(args.email, args.remote, args.path, args.show)
        elif args.tools == 'new-conf':
            new_conf(args.name)
        elif args.tools == 'reset':
            reset_conf(args.name, args.delete)
        elif args.tools == 'clear':
            clear(lambdas_old, lambdas_new, args.config, args.force)
        
    elif args.command == 'plot':
        plot(lambdas_old, lambdas_new, args.config)
            
if __name__ == "__main__":
    main()

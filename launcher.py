#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

# Created on Fri Mar 15 11:18:52 2019
"""
"""

__all__ = []
__version__ = '0.2'
__author__ = 'Alessandro Candido'

import argparse
import sys
from os import chdir, getcwd
from os.path import dirname, realpath
from platform import node

import lib.parser

# WRAPPERS

# Useful on running

def data(points_old, points_new, config, linear_history, time, steps,
         force, time_length, adj, max_vol, move22, move24, move_gauge,
         fake_run, debug):
    from lib.data import launch
    launch(points_old, points_new, config, linear_history, time, steps,
           force, time_length, adj, max_vol, move22, move24, move_gauge,
           fake_run, debug)

def state(configs, full_show=False):
    from lib.data import show_state
    show_state(configs, full_show)

def stop(points_old, points_new, config, is_all, pids, force):
    from lib.data import stop

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    stop(points_old, config, is_all, pids, force)

# Useful offline

def show(points_old, config, disk_usage):
    from lib.data import show
    show(points_old, config, disk_usage)

def plot(points_old, points_new, config):
    from lib.data import plot

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    if len(points_old) > 0:
        print()
    plot(points_old, config)

def fit(points_old, points_new, config, skip):
    from lib.analysis import fit

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    fit(points_old, config, skip)

# Utilities

def recovery(points_old, points_new, config, force, very_forced):
    from os import getcwd, chdir
    from lib.tools import recovery_history
    from lib.utils import authorization_request, point_dir

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
        if len(points_old) > 0:
            print()

    proj_dir = getcwd()

    for Point in points_old:
        if not config == 'test' and not force:
            what_to_do = "to recovery simulation data"
            authorized = authorization_request(what_to_do, Point)
        else:
            authorized = True
        if authorized:
            chdir('output/' + config + point_dir(Point))
            recovery_history(very_forced)
            chdir(proj_dir)

def info(points_old, config):
    from lib.tools import sim_info

    if len(points_old) == 0:
        print("(λ, β) not found")  # da migliorare
    elif len(points_old) == 1:
        sim_info(points_old[0], config)
    else:
        print('Only one point admitted.')

def therm(points_old, points_new, config, is_therm, force):
    from lib.tools import therm

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
        if len(points_old) > 0:
            print()
    therm(points_old, config, is_therm, force)

def up_launch(points_old, points_new, config, both, make, force):
    from lib.tools import up_launch

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
        if len(points_old) > 0:
            print()
    up_launch(points_old, config, both, make, force)

def remove(points_old, points_new, config, force, cbin, check):
    from lib.tools import remove

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
        if len(points_old) > 0:
            print()
    remove(points_old, config, force, cbin, check)

def remote(points_old, points_new, config, upload, download, force, rshow):
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
    if not exist or rclone_remote is None:
        print("No valid remote found.")
        return

    # @todo: scrivere nell'help che serve che nel remote ci sia almeno il
    # path valido
    print('checking remote...')
    path_content = popen('rclone lsd ' + rclone_remote + ':' +
                         remote_path).read()
    if 'CDT_2D' not in path_content:
        print('No valid remote found (is also possible that only the ' +
              'specified path is wrong).')
        return

    remote(points_old, points_new, config, upload, download, force, rshow)

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

def clear(points_old, points_new, config, force):
    from lib.tools import clear_data

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    clear_data(points_old, config, force)


if(node() == 'Paperopoli'):
    import argcomplete

def main():
    chdir(dirname(realpath(__file__)))

    parser, file_commands = lib.parser.define_parser(__file__, __version__)

    if len(sys.argv) < 2:
        parser.print_usage()
        print("Try 'launcher.py -h/--help' for more information.")
        return
    elif sys.argv[1] == 'tools' and len(sys.argv) == 2:
        print('usage: launcher.py tools [-h] {sub}')
        print("Try 'launcher.py tools -h/--help' for more information.")
        return
    elif sys.argv[1] == 'analysis' and len(sys.argv) == 2:
        print('usage: launcher.py analysis [-h] {sub}')
        print("Try 'launcher.py analysis -h/--help' for more information.")
        return

    # Input file management
    try:
        # at the present time input files are available only for run command
        assert sys.argv[1] == 'run'
        assert sys.argv[2] == '--file'

        if sys.argv[3] == '?':
            from inspect import cleandoc
            import pprint
            help = cleandoc(f"""Help for input files
                               --------------------

                               Each input has to start with the following line:
                               ### CDT_2D ###
                               tags are assignable in the form:
                               TAG=VALUE
                               and it isn't  whitespace-sensitive.

                               Available tags are:""")
            print(help)
            pprint.pprint(file_commands)
            quit()
        else:
            sys.argv = file_input(sys.argv[2], file_commands)
    except (AssertionError, IndexError):
        # if not file adds support for some special keyword
        sys.argv = ['-' + x if x in ['°', '@'] else x for x in sys.argv]
        sys.argv = [str(float(x)) if x[0] == '-' and x[1].isdigit() else x
                    for x in sys.argv]

    # Arguments retrieval
    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not hasattr(args, 'tools'):
        args.tools = ''

    # Further parsing (not supported by `argparse`)
    wo_point = ['state', 'config', 'new-conf', 'reset']
    if hasattr(args, 'is_all') and args.is_all:
        if any([hasattr(args, x) for x in ['lamda', 'beta']]) and \
           any([args.__dict__[x] is not None for x in ['lamda', 'beta']]):
            parser.error('° chosen together with (λ, β).')
    else:
        if all([x not in wo_point for x in [args.command, args.tools]]):
            if not all([hasattr(args, x) for x in ['lamda', 'beta']]):
                parser.error('(λ, β) point not specified.')

    # Supplies missing arguments
    if not hasattr(args, 'lamda') or args.lamda is None:
        lambdas = []
    else:
        lambdas = args.lamda
    if not hasattr(args, 'beta') or args.beta is None:
        betas = []
    else:
        betas = args.beta
    if not hasattr(args, 'is_data'):
        args.is_data = False
    if not hasattr(args, 'config'):
        args.config = 'test'
    if not hasattr(args, 'is_all'):
        args.is_all = False
    if not hasattr(args, 'range'):
        args.range = ''

    if args.is_data:
        args.config = 'data'

    if all([x not in wo_point for x in [args.command, args.tools]]):
        from lib.utils import points_recast

        points_old, points_new = points_recast(lambdas, betas, args.range,
                                                  args.is_all, args.config,
                                                  args.command)

    # Wrappers' calls
    if args.command == 'run':
        data(points_old, points_new, args.config, args.linear_history,
             args.time, args.steps, args.force, args.timelength, args.adj_flag,
             args.max_volume, args.move22, args.move24, args.move_gauge,
             args.fake_run, args.debug)

    elif args.command == 'state':
        state(args.config, args.full_show)

    elif args.command == 'stop':
        stop(points_old, points_new, args.config, args.is_all,
             args.pid, args.force)

    elif args.command == 'show':
        show(points_old, args.config, args.disk_usage)

    elif args.command == 'fit':
        fit(points_old, points_new, args.config, args.skip)

    elif args.command == 'tools':
        if args.tools == 'recovery':
            recovery(points_old, points_new, args.config, args.force,
                     args.FORCE)
        elif args.tools == 'info':
            info(points_old, args.config)
        elif args.tools == 'set-therm':
            therm(points_old, points_new, args.config, args.is_therm,
                  args.force)
        elif args.tools == 'up-launch':
            up_launch(points_old, points_new, args.config,
                      args.both, args.make, args.force)
        if args.tools == 'autoremove':
            remove(points_old, points_new, args.config, args.force,
                   args.bin, args.check)
        elif args.tools == 'remote':
            remote(points_old, points_new, args.config,
                   args.upload, args.download, args.force, args.show)
        elif args.tools == 'config':
            config(args.email, args.remote, args.path, args.show)
        elif args.tools == 'new-conf':
            new_conf(args.name)
        elif args.tools == 'reset':
            reset_conf(args.name, args.delete)
        elif args.tools == 'clear':
            clear(points_old, points_new, args.config, args.force)

    elif args.command == 'plot':
        plot(points_old, points_new, args.config)


if __name__ == "__main__":
    main()

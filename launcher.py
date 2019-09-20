#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

# Created on Fri Mar 15 11:18:52 2019
"""
"""

__all__ = []
__version__ = '0.2'
__author__ = 'Alessandro Candido'

import sys
from os import chdir, getcwd
from os.path import dirname, realpath
from platform import node

import lib.parser

sys.path += [realpath(__file__)]

# WRAPPERS

# Useful on running

def data(points_old, points_new, config, linear_history, time, steps,
         force, time_lengths, adj, max_vol, move22, move24, move_gauge,
         fake_run, debug, queue, arch, file):
    from lib.data import launch
    launch(points_old, points_new, config, linear_history, time, steps,
           force, time_lengths, adj, max_vol, move22, move24, move_gauge,
           fake_run, debug, queue, arch, file)

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

def plot(points_old, points_new, config, gauge):
    from lib.data import plot

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    if len(points_old) > 0:
        print()
    plot(points_old, config, gauge)

# def fit(points_old, points_new, config, skip):
#     from lib.analysis import fit
#
#     if len(points_new) > 0:
#         print("Following (λ, β) not found: ", points_new)
#     fit(points_old, config, skip)

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

def new_conf(name, path, caller_path):
    from lib.tools import new_conf

    new_conf(name[0], path, caller_path)

def show_confs(paths):
    from lib.tools import show_confs

    show_confs(paths)

def reset_conf(name):
    from lib.tools import reset_conf

    reset_conf(name)

def rm_conf(config, force):
    from lib.tools import rm_conf

    rm_conf(config, force)

def clear(points_old, points_new, config, force):
    from lib.tools import clear_data

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)
    clear_data(points_old, config, force)

# Analyses

def pre(kind, config, conf_plot, path, load_path, caller_path):
    from lib.analysis import preliminary_analyses

    preliminary_analyses(kind, config, conf_plot, path, load_path, caller_path)

def pre_plot(fit_name, kind):
    from lib.analysis import preplot

    preplot(fit_name[0], kind)

def new_fit(name, path, caller_path):
    from lib.analysis import new_fit

    new_fit(name[0], path, caller_path)

def show_fits(paths):
    from lib.analysis import show_fits

    show_fits(paths)

def reset_fit(name, delete):
    from lib.analysis import reset_fit

    reset_fit(name, delete)

def set_fit(name, points, points_new, config, remove):
    from lib.analysis import set_fit_props

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)

    set_fit_props(name[0], points, config, remove)

def info_fit(name, kind):
    from lib.analysis import info_fit

    info_fit(name[0], kind)

def sim_obs(points, points_new, config, plot, fit, excl_tor, excl_boot,
            fit_name, force):
    from lib.analysis import sim_obs

    if len(points_new) > 0:
        print("Following (λ, β) not found: ", points_new)

    if fit_name:
        from re import fullmatch
        from lib.utils import find_fits

        pattern_names = []
        pure_names = []
        all_names = list(find_fits().keys())
        for name in fit_name:
            if name[0] == '§':
                pattern_names += [c for c in all_names
                                    if fullmatch(name[1:], c)]
            else:
                pure_names += [name]

        names = sorted(list(set(pure_names + pattern_names)))
        print(f'Chosen fits are:\n  {names}')
    else:
        names = [None]

    for fit_name in names:
        if fit_name:
            msg = f"""\033[94m
            ┌────{'─'*len(fit_name)}──┐
            │FIT '{fit_name}'│
            └────{'─'*len(fit_name)}──┘
            \033[0m"""
            print(msg)

        sim_obs(points, config, plot, fit, excl_tor, excl_boot, fit_name, force)

def export_data(names, unpack):
    from re import fullmatch
    from lib.utils import find_fits
    from lib.analysis import export_data

    pattern_names = []
    pure_names = []
    all_names = list(find_fits().keys())
    for name in names:
        if name[0] == '§':
            pattern_names += [c for c in all_names
                                if fullmatch(name[1:], c)]
        else:
            pure_names += [name]

    names = sorted(list(set(pure_names + pattern_names)))
    print(f'Chosen fits are:\n  {names}')

    for name in names:
        msg = f"""\033[94m
        ┌────{'─'*len(name)}──┐
        │FIT '{name}'│
        └────{'─'*len(name)}──┘
        \033[0m"""
        print(msg)

        export_data(name, unpack)

def fit(name, reload, kind='volumes'):
    from lib.analysis import fit_divergence

    fit_divergence(name[0], kind, reload)

##################
#      MAIN      #
##################

if(node() == 'Paperopoli'):
    import argcomplete

def main():
    caller_path = getcwd()

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
            from lib.parser import file_input
            file_path = realpath(sys.argv[3])
            sys.argv = file_input(file_path, file_commands)
            sys.argv += ['--file', file_path]
    except (AssertionError, IndexError):
        # if not file adds support for some special keyword
        sys.argv = ['-' + x if x in ['°', '@'] else x for x in sys.argv]
        sys.argv = [str(float(x)) if x[0] == '-' and x[1].isdigit() else x
                    for x in sys.argv]

    chdir(dirname(realpath(__file__)))

    # Arguments retrieval
    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if not hasattr(args, 'tools'):
        args.tools = ''
    if not hasattr(args, 'analysis'):
        args.analysis = ''

    # Further parsing (not supported by `argparse`)
    wo_point = ['state', 'config', 'new-conf', 'show-confs', 'reset', 'rm-conf',
                'pre', 'pre-plot',
                'fit', 'new-fit', 'show-fits', 'info-fit', 'export-data']
    if hasattr(args, 'is_all') and args.is_all:
        if any([hasattr(args, x) for x in ['lamda', 'beta']]) and \
           any([args.__dict__[x] is not None for x in ['lamda', 'beta']]):
            parser.error('° chosen together with (λ, β).')
    else:
        if all([x not in wo_point for x in [args.command, args.tools,
                                            args.analysis]]):
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

    if all([x not in wo_point for x in [args.command, args.tools,
                                        args.analysis]]):
        from lib.utils import points_recast

        if args.command == 'show' and not lambdas:
            args.is_all = True

        if (lambdas and betas) or args.is_all:
            points_old, points_new = points_recast(lambdas, betas, args.range,
                                      args.is_all, args.config, args.command)
        else:
            points_old, points_new = [], []

    # Wrappers' calls
    if args.command == 'run':
        from lib.utils import timelengths_recast
        points = points_old + points_new
        timelengths = timelengths_recast(args.timelength, lambdas, betas,
                                         points)

        data(points_old, points_new, args.config, args.linear_history,
             args.time, args.steps, args.force, timelengths, args.adj_flag,
             args.max_volume, args.move22, args.move24, args.move_gauge,
             args.fake_run, args.debug, args.queue, args.arch, args.file)

    elif args.command == 'state':
        state(args.config, args.full_show)

    elif args.command == 'stop':
        stop(points_old, points_new, args.config, args.is_all,
             args.pid, args.force)

    elif args.command == 'show':
        show(points_old, args.config, args.disk_usage)

    elif args.command == 'plot':
        plot(points_old, points_new, args.config, args.gauge)

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
            new_conf(args.name, args.path, caller_path)
        elif args.tools == 'show-confs':
            show_confs(args.paths)
        elif args.tools == 'reset':
            reset_conf(args.name)
        elif args.tools == 'rm-conf':
            rm_conf(args.config, args.force)
        elif args.tools == 'clear':
            clear(points_old, points_new, args.config, args.force)

    elif args.command == 'analysis':
        if args.analysis == 'pre':
            pre(args.kind, args.config, args.conf_plot, args.save_path,
                args.load_path, caller_path)
        elif args.analysis == 'pre-plot':
            pre_plot(args.fit_name, args.kind)
        elif args.analysis == 'new-fit':
            new_fit(args.fit_name, args.path, caller_path)
        elif args.analysis == 'show-fits':
            show_fits(args.paths)
        elif args.analysis == 'reset':
            reset_fit(args.fit_name, args.delete)
        elif args.analysis == 'set-fit':
            set_fit(args.fit_name, points_old, points_new, args.config,
                    args.remove)
        elif args.analysis == 'info-fit':
            info_fit(args.fit_name, args.kind)
        elif args.analysis == 'sim-obs':
            sim_obs(points_old, points_new, args.config, args.plot,
                    args.fit, args.exclude_torelons, args.exclude_bootstrap,
                    args.fit_name, args.force)
        elif args.analysis == 'export-data':
            export_data(args.fit_name, args.unpack)
        elif args.analysis == 'fit':
            fit(args.fit_name, args.reload, args.kind)


if __name__ == "__main__":
    main()

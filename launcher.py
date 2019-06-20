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
         force, timelength, fake_run, debug):
    from lib.data import launch
    launch(lambdas_old, lambdas_new, config, linear_history, time, steps,
           force, timelength, fake_run, debug)

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
from os import chdir, getcwd
from os.path import dirname, realpath
from platform import node
import lib.parser

def file_input(file_path, commands):
    """Short summary.

    Parameters
    ----------
    file_path : str
        The relative path of the file, from the pwd.
    commands : dict
        Dictionary of available commands.

    Returns
    -------
    list
        List of arguments, as if `cdt2d` input was given as command.
    """
    def decode_line(line, i, d):
        """Transform a single line into a command argument."""
        if line[0] not in ['#', '\n']:
            if line.count('=') == 1:
                cmd_name, cmd_value = line.split('=')

                # flags or empty tags
                if cmd_value == 'True':
                    cmd_value = ''
                elif cmd_value in ['False', '']:
                    return ''

                return f'{ d[cmd_name]} {cmd_value.strip()}'
            else:
                msg = f"Invalid input file: {file_path}"
                msg += f"\nerror in line {i}:\n\t{line}"
                raise ValueError(msg)
        else:
            return ''

    args = [__file__]
    with open(file_path, 'r') as file:
        i = 1

        # check if it is a CDT_2D input file
        if next(file) != '### CDT_2D ###':
            raise ValueError('File given is not a CDT_2D file input.')

        for line in file:
            args += [decode_line(line, i, commands)]
            i += 1

    return args

if(node() == 'Paperopoli'):
    import argcomplete

def main():
    chdir(dirname(realpath(__file__)))

    parser, commands = lib.parser.define_parser(__file__, __version__)

    try:
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
            pprint.pprint(commands)
            quit()
        else:
            sys.argv = file_input(sys.argv[2], commands)
    except (AssertionError, IndexError):
        sys.argv = ['-' + x if x in ['°', '@'] else x for x in sys.argv]

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
             args.time, args.steps, args.force, args.timelength,
             args.fake_run, args.debug)

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

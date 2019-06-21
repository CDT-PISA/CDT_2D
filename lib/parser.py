"""
Parser definition for the CDT_2D simulations' launcher.
"""

from os import chdir, getcwd, scandir
from os.path import dirname, realpath, exists, isdir
import argparse

def update_cmds(cmds, subp_cmd):
    """Updates commands' dictionary, checking for keys' conflicts.

    Parameters
    ----------
    cmds : dict
        Dictionary to update.
    subp_cmd : dict
        Subparser dictionary with which updating `cmds`.

    Returns
    -------
    dict
        Updated dictionary.

    Raises
    ------
    AssertionError
        If there is a keys' conflict.
    """
    for key in subp_cmd.keys() & cmds.keys():
        if subp_cmd[key] != cmds[key]:
            raise AssertionError('Issue in `parser.py`: keywords must yield' +
                                 'unique commands')
    return {**cmds, **subp_cmd}

def define_parser(launcher_path, version):
    """Define the parser for the launcher.

    Parameters
    ----------
    launcher_path : str
        Path to launcher source.
    version: str
        The CDT_2D version number.

    Returns
    -------
    argparse.ArgumentParser
        The argument parser for the launcher.
    dict
        The dictionary of commands to decode file inputs.
    """
    starting_cwd = getcwd()
    chdir(dirname(realpath(launcher_path)))

    if exists('./output') and isdir('./output'):
        configs = [x.name for x in scandir('output') if x.is_dir()]
    else:
        configs = []

    parser = argparse.ArgumentParser(description='Manage CDT_2D simulations.')

    parser.add_argument('--version', action='version', version='CDT_2D ' +
                        'Gauge Fields: ' + version)
    # todo: devo scriverci usage
    #   tipo senza nulla con un numero
    #   oppure il tipo di numeri
    # migliorare la descrizione di ogni comando

    cmds = {'SUBPARSER': '',
            'HELP': '',
            'VERSION': ''}

    # SUBPARSERS
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = False

    # run command

    run_cmd = {'LAMBDA': '--lambda',
               'BETA': '--beta',
               'RANGE': '--range',
               'CONFIG': '--config',
               'FORCE': '--force',
               'TIMELENGTH': '--timelength',
               'DEBUG': '--debug',
               'FAKE-RUN': '--fake-run',
               'LINEAR-HISTORY': '--linear-history',
               'TIME': '--time',
               'STEPS': '--steps'}
    cmds = update_cmds(cmds, run_cmd)

    run_sub = subparsers.add_parser('run', help='run')
    run_sub.add_argument('-l', '--lambda', nargs='+', type=float, required=True,
                         help='λ values')
    run_sub.add_argument('-b', '--beta', nargs='+', type=float, required=True,
                         help='β values')
    run_sub.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help='range')
    run_sub.add_argument('-@', dest='is_data', action='store_true',
                         help="data configuration flag \
                         (the '-' in front is not needed)")
    run_sub.add_argument('-c', '--config', choices=configs, default='test',
                         help='config')
    run_sub.add_argument('-f', '--force', action='store_true', help='force')
    run_sub.add_argument('--timelength', nargs=1, type=int,
                         default=80, help='set timelength')
    run_sub.add_argument('-d', '--debug', action='store_true', help='debug')
    run_sub.add_argument('-k', '--fake-run', action='store_true',
                         help="if toggled prevents the simulation to start \
                         and instead prints the command that would be run \
                         otherwise")
    run_sub.add_argument('--lin', '--linear-history', dest='linear_history',
                         default='0',
                         help="it takes an integer argument, that if set \
                         greater then zero let data points be saved at regular \
                         intervals, instead of at increasing ones (units: \
                         {k,M,G}) | ex: --linear-history 2k")
    # run_sub.add_argument('--log-history', dest='linear_history',
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
    run_sub.add_argument('--file', help="launch simulation from config file: \
                          launch with '?' to show the help, else give the \
                          relative path of a valid CDT_2D valid from your \
                          PWD")

    # state command
    class ToggleChoiceAction(argparse.Action):
        def __init__(self, option_strings, dest, ifcall, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super(ToggleChoiceAction, self).__init__(option_strings, dest,
                                                     nargs='?', **kwargs)
            self.ifcall = ifcall
        def __call__(self, parser, namespace, values, option_string=None):
            if values is None:
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
    state_sub.add_argument('-f', '--full-show', choices=['1', '2'], default='0',
                           ifcall='1', action=ToggleChoiceAction,
                           help='full-show')

    # stop command

    stop_sub = subparsers.add_parser('stop', help='stop')
    stop_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                          required=True, help='λ values')
    stop_sub.add_argument('-b', '--beta', nargs='+', type=float, required=True,
                          help='β values')
    lambdas = stop_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
    show_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                          help='λ values')
    show_sub.add_argument('-b', '--beta', nargs='+', type=float,
                          help='β values')
    lambdas = show_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
    plot_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                          required=True, help='λ values')
    plot_sub.add_argument('-b', '--beta', nargs='+', type=float, required=True,
                          help='β values')
    plot_sub.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                          help='range')
    plot_sub.add_argument('-@', dest='is_data', action='store_true',
                          help="data configuration flag \
                          (the '-' in front is not needed)")
    plot_sub.add_argument('-c', '--config', choices=configs, default='test',
                          help='config')

    # fit command

    fit_sub = subparsers.add_parser('fit', help='fit')
    fit_sub.add_argument('-l', '--lambda', nargs='+', type=float, required=True,
                         help='λ values')
    fit_sub.add_argument('-b', '--beta', nargs='+', type=float, required=True,
                         help='β values')
    lambdas = fit_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
    recovery_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                              required=True, help='λ values')
    recovery_sub.add_argument('-b', '--beta', nargs='+', type=float,
                              required=True, help='β values')
    lambdas = recovery_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                                    help="all (the '-' in front is not needed)")
    recovery_sub.add_argument('-@', dest='is_data', action='store_true',
                              help="data configuration flag \
                              (the '-' in front is not needed)")
    recovery_sub.add_argument('-c', '--config', choices=configs, default='test',
                              help='config')
    recovery_sub.add_argument('-f', '--force', action='store_true',
                              help='force')
    recovery_sub.add_argument('-F', '--FORCE', action='store_true',
                              help='very forced')

    # info command

    info_sub = tools_sub.add_parser('info', help='info on a sim')
    info_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                          required=True, help='λ values')
    info_sub.add_argument('-b', '--beta', nargs='+', type=float,
                          required=True, help='β values')
    info_sub.add_argument('-@', dest='is_data', action='store_true',
                          help="data configuration flag \
                          (the '-' in front is not needed)")
    info_sub.add_argument('-c', '--config', choices=configs, default='test',
                          help='config')

    # thermalization command

    therm_sub = tools_sub.add_parser('set-therm', help='set thermalisation')
    therm_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                           required=True, help='λ values')
    therm_sub.add_argument('-b', '--beta', nargs='+', type=float,
                           required=True, help='β values')
    therm_sub.add_argument('-@', dest='is_data', action='store_true',
                           help="data configuration flag \
                           (the '-' in front is not needed)")
    therm_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    therm_sub.add_argument('-f', '--force', action='store_true', help='force')
    therm_sub.add_argument('-t', '--is-therm', default='True',
                           choices=['True', 'False'], help='thermalization')

    # launcher update command

    launch_sub = tools_sub.add_parser('up-launch',
                                      help='update launch/make_script')
    launch_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                            required=True, help='λ values')
    launch_sub.add_argument('-b', '--beta', nargs='+', type=float,
                            required=True, help='β values')
    lambdas = launch_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
    script.add_argument('--both', action='store_true',
                        help='update both launch_script and make_script')

    # autoremove command

    remove_sub = tools_sub.add_parser('autoremove', help='autoremove')
    remove_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                            required=True, help='λ values')
    remove_sub.add_argument('-b', '--beta', nargs='+', type=float,
                            required=True, help='β values')
    lambdas = remove_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
    remote_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                            required=True, help='λ values')
    remote_sub.add_argument('-b', '--beta', nargs='+', type=float,
                            required=True, help='β values')
    lambdas = remote_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
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
                      p='update make_script instead')
    load.add_argument('-d', '--download', action='store_true',
                      help='update both launch_script and make_script')
    load.add_argument('-s', '--show', action='store_true',
                      help='show list of sims on remote')

    # config command

    config_sub = tools_sub.add_parser('config', help='edit project\'s \
                                      configuration file')
    configs_arg = config_sub.add_mutually_exclusive_group()
    configs_arg.add_argument('-e', '--email', action=ToggleChoiceAction,
                             default=None, ifcall='-',
                             help='set receiver email')
    configs_arg.add_argument('-r', '--remote', action=ToggleChoiceAction,
                             default=None, ifcall='-', help='set rclone remote')
    configs_arg.add_argument('-p', '--path', action=ToggleChoiceAction,
                             default=None, ifcall='-', help='set rclone path')
    configs_arg.add_argument('-n', '--node', action=ToggleChoiceAction,
                             default=None, ifcall='-', help='set node name')
    config_sub.add_argument('-s', '--show', action='store_true',
                            help='show config_file')

    # new configuration command

    new_conf_sub = tools_sub.add_parser('new-conf', help='create new config')
    new_conf_sub.add_argument('name', nargs=1, type=str)

    # reset configuration command

    reset_conf_sub = tools_sub.add_parser('reset',
                                          help='reset or delete config')
    reset_conf_sub.add_argument('name', choices=configs)
    reset_conf_sub.add_argument('-d', '--delete', action='store_true',
                                help='defintely delete config')

    # clear command

    clear_sub = tools_sub.add_parser('clear', help='clear')
    clear_sub.add_argument('-l', '--lambda', nargs='+', type=float,
                           required=True, help='λ values')
    clear_sub.add_argument('-b', '--beta', nargs='+', type=float,
                           required=True, help='β values')
    lambdas = clear_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help='range')
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                                    help="all (the '-' in front is not needed)")
    clear_sub.add_argument('-@', dest='is_data', action='store_true',
                           help="data configuration flag \
                           (the '-' in front is not needed)")
    clear_sub.add_argument('-c', '--config', choices=configs, default='test',
                           help='config')
    clear_sub.add_argument('-f', '--force', action='store_true', help='force')

    chdir(starting_cwd)

    return parser, cmds


def decode_line(line, i, d, file_path):
    """Transform a single line into a command argument."""
    if line[0] not in ['#', '\n']:
        if line.count('=') == 1:
            cmd_name, cmd_value = line.split('=')
            cmd_name = cmd_name.strip()
            cmd_value = cmd_value.strip()

            # flags or empty tags
            if cmd_value == 'True':
                cmd_value = ''
            elif cmd_value in ['False', '']:
                return ''

            return f'{ d[cmd_name]} {cmd_value}'
        else:
            msg = f"Invalid input file: {file_path}"
            msg += f"\nerror in line {i}:\n\t{line}"
            raise ValueError(msg)
    else:
        return ''

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
    args = [__file__]
    with open(file_path, 'r') as file:
        i = 1

        # check if it is a CDT_2D input file
        if next(file) != '### CDT_2D ###':
            raise ValueError('File given is not a CDT_2D file input.')

        for line in file:
            args += [decode_line(line, i, commands, file_path)]
            i += 1

    return args

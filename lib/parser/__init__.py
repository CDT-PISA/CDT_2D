"""
Parser definition for the CDT_2D simulations' launcher.
"""

from os import chdir, getcwd, scandir, listdir
from os.path import dirname, realpath, exists, isdir, isfile
from inspect import cleandoc
import argparse
import lib.parser.msgs
from lib.utils import project_folder

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

def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        msg = f"{value} is an invalid positive int value"
        raise argparse.ArgumentTypeError(msg)
    return ivalue

def positive_float(value):
    ivalue = float(value)
    if ivalue <= 0:
        msg = f"{value} is an invalid positive float value"
        raise argparse.ArgumentTypeError(msg)
    return ivalue

def non_negative_float(value):
    ivalue = float(value)
    if ivalue < 0:
        msg = f"{value} is an invalid non negative float value"
        raise argparse.ArgumentTypeError(msg)
    return ivalue

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
    chdir(project_folder())

    if exists('output') and isdir('output'):
        if isfile('output/configs.json'):
            import json

            with open('output/configs.json', 'r') as config_file:
                configs_d = json.load(config_file)
            configs = list(configs_d.keys())
        else:
            configs = [x.name for x in scandir('output') if x.is_dir()]
    else:
        configs = []

    meta_configs = '{...}' if len(configs) > 5 else None
    # ┏━━━━━━━━━━━━━━━━┓
    # ┗━━━━━━━━━━━━━━━━┛

    msg = cleandoc("""
    ┎────────────────┒
    ┃ CDT2D LAUNCHER ┃
    ┖────────────────┚
    Manage CDT_2D simulations.

    To show the help of subcommand 'sub' run:
        launcher.py sub -h""")

    parser = argparse.ArgumentParser(description=msg,
                        formatter_class=argparse.RawDescriptionHelpFormatter)

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

    run_cmd = {'LAMBDA': '--lamda',
               'BETA': '--beta',
               'RANGE': '--range',
               'CONFIG': '--config',
               'QUEUE': '--queue',
               'FORCE': '--force',
               'TIMELENGTH': '--timelength',
               'DEBUG': '--debug',
               'FAKE-RUN': '--fake-run',
               'LINEAR-HISTORY': '--linear-history',
               'TIME': '--time',
               'STEPS': '--steps',
               'ADJACENCIES': '--adjacencies',
               'MOVE22': '--move22',
               'MOVE24': '--move24',
               'MOVE_GAUGE': '--move-gauge'}
    cmds = update_cmds(cmds, run_cmd)

    run_sub = subparsers.add_parser('run', help=msgs.run_h,
                        description=msgs.run,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    run_sub.add_argument('-l', '--lamda', nargs='+', type=float, required=True,
                         help=msgs.lamda)
    run_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                         required=True, help=msgs.beta)
    run_sub.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    run_sub.add_argument('-@', dest='is_data', action='store_true',
                         help=msgs.data)
    run_sub.add_argument('-c', '--config', choices=configs, default='test',
                         metavar=meta_configs,
                         help=msgs.config)
    run_sub.add_argument('-q', '--queue', default='debug',
                         choices=['p', 'prod', 'd', 'dbg', 'debug'],
                         help=msgs.queue)
    run_sub.add_argument('-f', '--force', action='store_true', help=msgs.force)
    run_sub.add_argument('--timelength', nargs='+', type=int, default=80,
                         help=msgs.timelength)
    run_sub.add_argument('-d', '--debug', action='store_true', help='debug')
    run_sub.add_argument('-k', '--fake-run', action='store_true',
                         help=msgs.fake_run)
    run_sub.add_argument('--lin', '--linear-history', dest='linear_history',
                         default='0', type=str, help=msgs.linear_history)
    # run_sub.add_argument('--log-history', dest='linear_history',
    #               action='store_false',
    #               help="if set data points are saved at increasing intervals")
    end_conditions = run_sub.add_mutually_exclusive_group()
    end_conditions.add_argument('--time', default='30m', help=msgs.time)
    end_conditions.add_argument('--steps', default='0', help=msgs.steps)
    run_sub.add_argument('--adj', '--adjacencies', dest='adj_flag',
                         action='store_true', help=msgs.adjacencies)
    run_sub.add_argument('--vol', '--max-volume', dest='max_volume',
                         type=positive_float, nargs=1, default=1e5,
                         help=msgs.maxvol)
    moves_weights = run_sub.add_argument_group("moves' weights",
                                        description=msgs.moves_weights)
    moves_weights.add_argument('--move22', nargs=1, type=non_negative_float,
                               default=0.1, metavar='W_22', help=msgs.move22)
    moves_weights.add_argument('--move24', nargs=1, type=non_negative_float,
                               default=0.2, metavar='W_24', help=msgs.move24)
    moves_weights.add_argument('--move-gauge', nargs=1, type=non_negative_float,
                               default=0.4, metavar='W_g', help=msgs.moveg)
    run_sub.add_argument('--file', help=msgs.file)

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

    state_sub = subparsers.add_parser('state', help=msgs.state_h,
                        description=msgs.state,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    state_sub.add_argument('-@', dest='is_data', action='store_true',
                           help=msgs.data)
    state_sub.add_argument('-c', '--config', choices=configs, default=configs,
                           metavar=meta_configs,
                           ifcall='test', action=ToggleChoiceAction,
                           help=msgs.config)
    state_sub.add_argument('-f', '--full-show', choices=['1', '2'], default='0',
                           ifcall='1', action=ToggleChoiceAction,
                           help=msgs.full_show)

    # stop command

    stop_sub = subparsers.add_parser('stop', help=msgs.stop_h,
                        description=msgs.stop,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    points = stop_sub.add_argument_group()
    points.add_argument('-l', '--lamda', nargs='+', type=float, help=msgs.lamda)
    points.add_argument('-b', '--beta', nargs='+', type=positive_float,
                        help=msgs.beta)
    points.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    points.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    stop_sub.add_argument('-@', dest='is_data', action='store_true',
                          help=msgs.data)
    stop_sub.add_argument('-c', '--config', choices=configs, default='test',
                          metavar=meta_configs,
                          help=msgs.config)
    stop_sub.add_argument('--pid', nargs='+', type=int, default=None,
                          help=msgs.pid)
    stop_sub.add_argument('-f', '--force', action='store_true', help=msgs.force)

    # plot command

    plot_sub = subparsers.add_parser('plot', help=msgs.plot_h,
                        description=msgs.plot,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    plot_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                          required=True, help=msgs.lamda)
    plot_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                          required=True, help=msgs.beta)
    plot_sub.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                          help=msgs.range)
    plot_sub.add_argument('-@', dest='is_data', action='store_true',
                          help=msgs.data)
    plot_sub.add_argument('-c', '--config', choices=configs, default='test',
                          metavar=meta_configs,
                          help=msgs.config)

    # show command

    show_sub = subparsers.add_parser('show', help=msgs.show_h,
                        description=msgs.show,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    show_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                          help=msgs.lamda)
    show_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                          help=msgs.beta)
    lambdas = show_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    show_sub.add_argument('-@', dest='is_data', action='store_true',
                          help=msgs.data)
    show_sub.add_argument('-c', '--config', choices=configs, default='test',
                          metavar=meta_configs,
                          help=msgs.config)
    show_sub.add_argument('-d', '--disk-usage', default='', const='disk',
                          action='store_const', help=msgs.disk_usage)
    show_sub.add_argument('-n', '--number', dest='disk_usage', const='num',
                          action='store_const', help=msgs.disk_number)

    # utilities subparser

    tools = subparsers.add_parser('tools', help=msgs.tools)
    tools_sub = tools.add_subparsers(dest='tools')

    # recovery command

    recovery_sub = tools_sub.add_parser('recovery', help='recovery',
                        description=msgs.recovery,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    recovery_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                              required=True, help=msgs.lamda)
    recovery_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                              required=True, help=msgs.beta)
    lambdas = recovery_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    recovery_sub.add_argument('-@', dest='is_data', action='store_true',
                              help=msgs.data)
    recovery_sub.add_argument('-c', '--config', choices=configs, default='test',
                              metavar=meta_configs,
                              help=msgs.config)
    recovery_sub.add_argument('-f', '--force', action='store_true',
                              help=msgs.force)
    recovery_sub.add_argument('-F', '--FORCE', action='store_true',
                              help=msgs.very_force)

    # info command

    info_sub = tools_sub.add_parser('info', help='info on a sim',
                        description=msgs.info,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    info_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                          required=True, help=msgs.lamda)
    info_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                          required=True, help=msgs.beta)
    info_sub.add_argument('-@', dest='is_data', action='store_true',
                          help=msgs.data)
    info_sub.add_argument('-c', '--config', choices=configs, default='test',
                          metavar=meta_configs,
                          help=msgs.config)

    # thermalization command

    therm_sub = tools_sub.add_parser('set-therm', help='set thermalisation',
                        description=msgs.therm,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    therm_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                           required=True, help=msgs.lamda)
    therm_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                           required=True, help=msgs.beta)
    therm_sub.add_argument('-@', dest='is_data', action='store_true',
                           help=msgs.data)
    therm_sub.add_argument('-c', '--config', choices=configs, default='test',
                           metavar=meta_configs,
                           help=msgs.config)
    therm_sub.add_argument('-f', '--force', action='store_true',
                           help=msgs.force)
    therm_sub.add_argument('-t', '--is-therm', default='True',
                           choices=['True', 'False'], help=msgs.is_therm)

    # update launcher command

    launch_sub = tools_sub.add_parser('up-launch',
                  help='update launch/make_script', description=msgs.up_launch,
                  formatter_class=argparse.RawDescriptionHelpFormatter)
    points = launch_sub.add_argument_group()
    points.add_argument('-l', '--lamda', nargs='+', type=float, help=msgs.lamda)
    points.add_argument('-b', '--beta', nargs='+', type=positive_float,
                      help=msgs.beta)
    points.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                       help=msgs.range)
    points.add_argument('-°', dest='is_all', action='store_true',
                       help=msgs.is_all)
    launch_sub.add_argument('-@', dest='is_data', action='store_true',
                            help=msgs.data)
    launch_sub.add_argument('-c', '--config', choices=configs, default='test',
                            metavar=meta_configs,
                            help=msgs.config)
    launch_sub.add_argument('-f', '--force', action='store_true',
                            help=msgs.force)
    script = launch_sub.add_mutually_exclusive_group()
    script.add_argument('-m', '--make', action='store_true', help=msgs.make)
    script.add_argument('--both', action='store_true', help=msgs.both)

    # autoremove command

    remove_sub = tools_sub.add_parser('autoremove', help='autoremove',
                        description=msgs.autoremove,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    remove_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                            required=True, help=msgs.lamda)
    remove_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                            required=True, help=msgs.beta)
    lambdas = remove_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    remove_sub.add_argument('-@', dest='is_data', action='store_true',
                            help=msgs.data)
    remove_sub.add_argument('-c', '--config', choices=configs, default='test',
                            metavar=meta_configs,
                            help=msgs.config)
    remove_sub.add_argument('-f', '--force', action='store_true',
                            help=msgs.force)
    what = remove_sub.add_mutually_exclusive_group()
    what.add_argument('--bin', ifcall='0', action=ToggleChoiceAction,
                      help=msgs.bin)
    what.add_argument('--check', ifcall='0', action=ToggleChoiceAction,
                      help=msgs.check)

    # upload/download command

    remote_sub = tools_sub.add_parser('remote', help='upload/download sim dirs',
                        description=msgs.remote,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    remote_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                            required=True, help=msgs.lamda)
    remote_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                            required=True, help=msgs.beta)
    lambdas = remote_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    remote_sub.add_argument('-@', dest='is_data', action='store_true',
                            help=msgs.data)
    remote_sub.add_argument('-c', '--config', choices=configs, default='test',
                            metavar=meta_configs,
                            help=msgs.config)
    remote_sub.add_argument('-f', '--force', action='store_true',
                            help=msgs.force)
    load = remote_sub.add_mutually_exclusive_group(required=True)
    load.add_argument('-u', '--upload', action='store_true',
                      help=msgs.upload)
    load.add_argument('-d', '--download', action='store_true',
                      help=msgs.download)
    load.add_argument('-s', '--show', action='store_true',
                      help=msgs.remote_show)

    # config command

    config_sub = tools_sub.add_parser('config',
        help='edit project\'s configuration file', description=msgs.config_cmd,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    configs_arg = config_sub.add_mutually_exclusive_group()
    configs_arg.add_argument('-e', '--email', action=ToggleChoiceAction,
                             default=None, ifcall='-',
                             help=msgs.email)
    configs_arg.add_argument('-r', '--remote', action=ToggleChoiceAction,
                             default=None, ifcall='-', help=msgs.rclone_remote)
    configs_arg.add_argument('-p', '--path', action=ToggleChoiceAction,
                             default=None, ifcall='-', help=msgs.rclone_path)
    configs_arg.add_argument('-n', '--node', action=ToggleChoiceAction,
                             default=None, ifcall='-', help=msgs.node)
    config_sub.add_argument('-s', '--show', action='store_true',
                            help=msgs.show_config)

    # new configuration command

    new_conf_sub = tools_sub.add_parser('new-conf', help='create new config',
                      description=msgs.new_conf,
                      formatter_class=argparse.RawDescriptionHelpFormatter)
    new_conf_sub.add_argument('name', nargs=1, type=str)
    new_conf_sub.add_argument('-p', '--path', type=str,
                              default=None, help=msgs.path)

    # show available configurations command

    show_confs_sub = tools_sub.add_parser('show-confs',
                    help='create new config',
                    description=msgs.new_conf,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    show_confs_sub.add_argument('-p', '--paths', action='store_true',
                              help=msgs.show_paths)

    # reset configuration command

    reset_conf_sub = tools_sub.add_parser('reset',
                      help='reset or delete config', description=msgs.reset,
                      formatter_class=argparse.RawDescriptionHelpFormatter)
    reset_conf_sub.add_argument('name', choices=configs)
    # reset_conf_sub.add_argument('-d', '--delete', action='store_true',
    #                             help=msgs.delete)

    # remove configuration command

    rm_conf_sub = tools_sub.add_parser('rm-conf', help='remove config',
                        description=msgs.clear,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    rm_conf_sub.add_argument('config', choices=configs, metavar=meta_configs,
                             help=msgs.config)
    rm_conf_sub.add_argument('-f', '--force', action='store_true',
                             help=msgs.force)

    # clear command

    clear_sub = tools_sub.add_parser('clear', help='clear',
                        description=msgs.clear,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    clear_sub.add_argument('-l', '--lamda', nargs='+', type=float,
                           required=True, help=msgs.lamda)
    clear_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                           required=True, help=msgs.beta)
    lambdas = clear_sub.add_mutually_exclusive_group()
    lambdas.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    lambdas.add_argument('-°', dest='is_all', action='store_true',
                         help=msgs.is_all)
    clear_sub.add_argument('-@', dest='is_data', action='store_true',
                           help=msgs.data)
    clear_sub.add_argument('-c', '--config', choices=configs, default='test',
                           metavar=meta_configs,
                           help=msgs.config)
    clear_sub.add_argument('-f', '--force', action='store_true',
                           help=msgs.force)

    # analysis subparser

    analysis = subparsers.add_parser('analysis', help=msgs.analysis)
    analysis_sub = analysis.add_subparsers(dest='analysis')

    # preliminary command

    def config_pattern(config):
        if not isinstance(config, str):
            msg = f"{config} is not a valid str."
            raise argparse.ArgumentTypeError(msg)
        if config not in configs and config[0] != '§':
            msg = f"{config} is not valid config nor pattern"
            raise argparse.ArgumentTypeError(msg)
        return config

    kinds = ['mv', 'mean-volumes', 'd', 'divergent', 'vp', 'volumes-plot']

    pre_sub = analysis_sub.add_parser('pre', help='preliminary analyses',
                        description=msgs.ana_pre,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    pre_sub.add_argument('-k', '--kind', choices=kinds, help=msgs.pre_kind)
    pre_sub.add_argument('-c', '--config', default=None,
                         metavar=meta_configs, nargs='+', type=config_pattern,
                         help=msgs.config_pattern)
    pre_sub.add_argument('--conf-plot', dest='conf_plot',
                         action='store_true', help=msgs.conf_plot)

    # fit command

    fit_sub = analysis_sub.add_parser('fit', help='fit',
                        description=msgs.fit,
                        formatter_class=argparse.RawDescriptionHelpFormatter)
    fit_sub.add_argument('-l', '--lamda', nargs='+', type=float, required=True,
                         help=msgs.lamda)
    fit_sub.add_argument('-b', '--beta', nargs='+', type=positive_float,
                         required=True, help=msgs.beta)
    fit_sub.add_argument('--range', choices=['b', 'l', 'bl', 'lb'], default='',
                         help=msgs.range)
    fit_sub.add_argument('-c', '--config', choices=configs, default='test',
                         metavar=meta_configs,
                         help=msgs.config)
    fit_sub.add_argument('-s', '--skip', action='store_true', help=msgs.skip)

    chdir(starting_cwd)

    return parser, cmds


def decode_line(line, i, d, file_path):
    """Transform a single line into a command argument."""
    line = line.strip()

    if line and line[0] != '#':
        if line.count('=') == 1:
            cmd_name, cmd_value = line.split('=')
            cmd_name = cmd_name.strip()
            cmd_value = cmd_value.strip()

            # flags or empty tags
            if cmd_value == 'True':
                cmd_value = ''
            elif cmd_value in ['False', '']:
                return ''

            if cmd_value:
                return [d[cmd_name]] + cmd_value.strip().split()
            else:
                return [d[cmd_name]]
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
    from os.path import dirname, abspath
    launcher_path = abspath(dirname(__file__) + '/../../launcher.py')

    args = [launcher_path, 'run']

    with open(file_path, 'r') as file:
        i = 1

        # check if it is a CDT_2D input file
        if next(file).strip() != '### CDT_2D ###':
            raise ValueError('File given is not a CDT_2D file input.')

        for line in file:
            x = decode_line(line, i, commands, file_path)
            if x:
                args += x
            i += 1

    return args

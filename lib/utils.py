# -*- coding: utf-8 -*-

#Created on Sun Jan 27 12:25:38 2019
"""
Collection of useful functions for CDT_2D project
"""
from os import scandir, popen
from re import search
from platform import node
from math import floor, log10

def point_str(Point):
    """Standardizes Point's representation.

    Return `None` if `Point` is not representing a point in parameters' space.

    Parameters
    ----------
    Point : tuple
         (λ, β) floats.

    Returns
    -------
    str
        Directory name of the corresponding point.
    """
    try:
        assert len(Point) == 2
        _ = float(Point[0]), float(Point[1])

        return 'Lambda' + str(Point[0]) + '_Beta' + str(Point[1])
    except (AssertionError, ValueError):
        return None

def point_dir(Point):
    """Standardizes directories' names.

    At the present time it's a wrapper of `point_str` function.

    Parameters
    ----------
    Point : tuple
         (λ, β) floats.

    Returns
    -------
    str
        Directory name of the corresponding point.
    """
    return point_str(Point)


def str_point(point_name):
    """Decodes points' representation.

    It has to be opposite to point_dir:
        str_point(point_str) = id
    if there are no multiple simulations for the same point also:
        point_str(str_point) = id

    Return `None` if the name is not a proper `point_name`

    Parameters
    ----------
    point_name : str
       String representation of the corresponding point.

    Returns
    -------
    tuple
         (λ, β) floats.
    """
    if all([x in point_name for x in ['Lambda', '_Beta']]):
        p = point_name.split('Lambda')[1].split('_Beta')
        return float(p[0]), float(p[1])
    else:
        return None

def dir_point(dir_name):
    """Decodes directories' names.

    Similar to point_dir, now it's a wrapper of str_point.

    Return `None` if the name is not a proper `dir_name`

    Parameters
    ----------
    point_name : str
       Directory name of the corresponding point.

    Returns
    -------
    tuple
         (λ, β) floats.
    """
    return str_point(dir_name)

def project_folder():
    """Tell the absolute path to project folder.

    Returns
    -------
    str
        CDT_2D project folder path.
    """
    from os.path import dirname, realpath

    dir_path = dirname(realpath(__file__))
    return realpath(dir_path + '/..')

def find_configs():
    """Find available configs.

    Returns
    -------
    dict or list
        container of config names, if it is a dict values are paths associate
        to those names.
    """
    from os.path import abspath
    import json

    output_path = project_folder() + '/output'
    config_path = output_path + '/configs.json'
    try:
        with open(config_path, 'r') as config_file:
            configs = json.load(config_file)
    except FileNotFoundError:
        configs = [x.name for x in scandir(output_path) if x.is_dir()]

    return configs

def config_dir(config):
    """Retrieves config directory's path.

    Parameters
    ----------
    config : str
        Name of the configuration to select.

    Returns
    -------
    str
        Path of the requested directory.
    """
    configs = find_configs()

    if isinstance(configs, dict):
        try:
            path = configs[config]
        except IndexError:
            raise FileNotFoundError('Config dir not found.')
    else:
        if config in configs:
            output_path = project_folder() + '/output'
            path = output_path + '/' + config
        else:
            raise FileNotFoundError('Config dir not found.')

    return path

def launch_script_path():
    from os.path import abspath, dirname

    lib_path = abspath(dirname(__file__))
    return lib_path + '/scripts/launch_script.py'

def launch_script_name(Point):
    return 'launch_' + point_str(Point) + '.py'

def make_script_path():
    from os.path import abspath, dirname

    lib_path = abspath(dirname(__file__))
    return lib_path + '/scripts/make_script.py'

def make_script_name(Point):
    return 'make_' + point_str(Point) + '.py'

def find_all_availables(config='data', dir_decode=dir_point):
    """Find all lambdas for which a simulation has been already run

    Parameters
    ----------
    config : str
        the configuration ('data', 'test', ...)
    dir_prefix : str
        the name of the directory that precedes the value
        of lambda *(the number must start from the subsequent
        character)*

    Returns
    -------
    list
        a list of the existing values of lambda
    """
    c_dir = config_dir(config)

    directories = [x.name for x in scandir(c_dir) if x.is_dir()]
    all_availables = [dir_decode(x) for x in directories
                      if dir_decode(x) is not None]
    all_availables.sort()

    return all_availables

def inside_rect(p, extremes):
    """Check if `p` is inside the multidimensional rectangle defined by
    `extremes`.

    Parameters
    ----------
    p : sequence
        point's coordinates
    extremes : sequence
        list of intervals' extremes
    """
    assert len(p) == len(extremes)
    assert all([len(x) == 2 for x in extremes])
    return all([extremes[i][0] <= p[i] <= extremes[i][1]
                for i in range(len(p))])

def points_grid(*coords):
    """Generates the list of points (as coordinates' tuples), from the lists
    of projections on axes.

    Parameters
    ----------
    sequences
        arbitrary number of sequences of coordinates.

    Returns
    -------
    list
        List of points, as tuples of coordinates.
    """
    from numpy import meshgrid
    l = meshgrid(*coords)
    return list(zip(*[list(x.reshape(-1)) for x in l]))

def points_recast(lambda_list, beta_list, range='', is_all=False,
                   config='test', cmd=''):
    """Short summary.

    Parameters
    ----------
    lambda_list : type
        Description of parameter `lambda_list`.
    beta_list : type
        Description of parameter `beta_list`.
    range : type
        Description of parameter `range`.
    is_all : type
        Description of parameter `is_all`.
    config : type
        Description of parameter `config`.
    cmd : type
        Description of parameter `cmd`.

    Returns
    -------
    type
        Description of returned object.

    """
    # If all parameters are absent in subcommand show it should be considered
    # as if `is_all` is True
    lengths = [len(lambda_list), len(beta_list)]
    if 0 in lengths and cmd == 'show':
        if any([x != 0 for x in lengths]):
            raise ValueError('Error in show: only some parameters specified .')
        else:
            is_all = True

    # loads points from already existing directories
    points = []
    points_old = []
    points_new = []
    all_points = find_all_availables(config)

    """Generates points' list
       ----------------------
       strategy:
         - is_all: all old points
       n-ranges are list declared as range of length n
         - all 2-ranges: old points in the specified rectangle
         - some 2-ranges: Error
       if there isn't any 2-range:
         - 3-ranges: converted in lists with `linspace`
         - are lists of projections are merged in a unique grid
    """
    if is_all:
        points = all_points
    else:
        lambda_extremes = None
        beta_extremes = None

        if range == '':
            if len(lambda_list) != len(beta_list):
                raise ValueError('λ and β must be of the same length, if '
                                 'neither of these is a range')
            points = list(zip(lambda_list, beta_list))
        else:
            from numpy import linspace
            if 'l' in range:
                if len(lambda_list) == 3:
                    lambdas = list(linspace(*lambda_list))
                elif len(lambda_list) == 2:
                    lambda_extremes = lambda_list
                else:
                    raise ValueError('λ is a range, but its length is neither '
                                     '2 Nor 3')
            else:
                lambdas = lambda_list
            if 'b' in range:
                if len(beta_list) == 3:
                    betas = list(linspace(*beta_list))
                elif len(beta_list) == 2:
                    beta_extremes = beta_list
                else:
                    raise ValueError('β is a range, but its length is neither '
                                     '2 Nor 3')
            else:
                betas = beta_list

        extremes = [lambda_extremes, beta_extremes]
        if any(extremes):
            if all(extremes):
                points = [p for p in all_points if inside_rect(p, extremes)]
            else:
                raise ValueError('Only some intervals specified, '
                                 'not the whole rectangle')
        elif range != '':
            points = points_grid(lambdas, betas)

    if len(points) > 0:
        points_old = [x for x in points if x in all_points]
        points_new = [x for x in points if x not in points_old]

    points_old = list(set(points_old))
    if len(points_old) > 0: points_old.sort()
    points_new = list(set(points_new))
    if len(points_new) > 0: points_new.sort()

    return points_old, points_new

def timelengths_recast(timelengths, lambdas, betas, points):
    d = {}

    if isinstance(timelengths, list):
        if len(timelengths) == 1:
            for Point in points:
                d[Point] = timelengths[0]
        elif len(timelengths) == len(points):
            assert len(lambdas) == len(betas)
            points = list(zip(lambdas, betas))

            for i in range(len(points)):
                d[points[i]] = timelengths[i]
        else:
            raise ValueError("If `timelengths` is a list should be of the"
                             "same length of points' list.")
    elif isinstance(timelengths, int):
        for Point in points:
            d[Point] = timelengths

    return d

def find_running():
    """Find running simulations and configs to which they belong.

    Returns
    -------
    list
        (lambdas, config) for running simulations.
    list
        other infos to be printed by `cdt2d state`

    Example
    -------
    An example of output from ``ps -fu user``

    ::
        UID    PID  PPID  C STIME TTY          TIME CMD
        user  1350     1  0 15:44 pts/1    00:00:00 python3 \
            /home/user/projects/CDT_2D/output/test/Lambda0.1_Beta1.0\
            /launch_Lambda0.1_Beta1.0.py 1 0.1 1.0 80 1800 false No
        user  1358  1350 98 15:44 pts/1    00:00:56 bin/CDT_2D-\
            Lambda0.1_Beta1.0_run1 1 0.1 1.0 80 360s false None 0
    """
    from os import environ
    from os.path import basename
    from lib.utils import find_configs
    from lib.platforms import get_ps_out

    if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
        ps_out = get_ps_out()

        points_run = []
        sim_info = []
        PPID_list = []
        for line in ps_out[1:]:
            if ' bin/CDT_2D-Lambda' in line:
                pinfos = line.split()
                Lambda = float(pinfos[9])
                Beta = float(pinfos[10])
                start_time = pinfos[6]
                run_id = pinfos[8]
                PID = pinfos[1]
                PPID = pinfos[2]
                points_run += [[(Lambda, Beta)]]
                sim_info += [[start_time, run_id, PID, PPID]]
                PPID_list += [PPID]

        configs = find_configs()
        if isinstance(configs, dict):
            configs_aux = {v:k for k,v in configs.items()}
        else:
            output_path = project_folder() + '/output/'
            configs_aux = {output_path + c: c for c in configs}

        for line in ps_out[1:]:
            pinfos = line.split()
            if len(pinfos) > 0:
                try:
                    i = PPID_list.index(pinfos[1])
                except ValueError:
                    continue

                from re import split
                path = split('/Lambda', pinfos[8])[0]
                config = configs_aux[path]

                points_run[i] += [config]

    else:
        points_run = []
        sim_info = []
        print("RUNNING SIMS: This platform is still not supported")

    return points_run, sim_info

def authorization_request(what_to_do='', Point=None, extra_message=''):
    """Short summary.

    Parameters
    ----------
    what_to_do : type
        Description of parameter `what_to_do`.
    Point : type
        Description of parameter `Point`.
    extra_message : type
        Description of parameter `extra_message`.

    Returns
    -------
    type
        Description of returned object.

    """
    import readline

    if Point is not None:
        print("((λ, β) = " + str(Point) + ") ", end='')
    print("Do you really want " + what_to_do + "? [y/n]")
    if extra_message != '':
        print(extra_message)
    authorized = False
    ans_recog = False
    count = 0
    while not ans_recog and count < 3:
        count += 1
        try:
            ans = input('--> ')
        except EOFError:
            print()
            ans = 'n'
        ans_recog = True
        if ans == 'y':
            authorized = True
        elif ans == 'q' or ans == 'quit':
            authorized = 'quit'
        elif ans != 'n':
            ans_recog = False
            print('Answer not recognized', end='')
            if count < 3:
                print(', type it again [y/n]')
            else:
                print(' (nothing done)')

    return authorized

def moves_weights(move22, move24, move_gauge):
    """Compute the values of weights in presence of custom ones.

    The default values are supposed to be float, while the custom one must be
    'list' of length 1.
    The assumed behaviour is compliant with that of the parser.

    Parameters
    ----------
    move22 : float or list
        The weight of self-dual moves (its doubled in the overall sum of
        weigths because it's used for two moves).
    move24 : float or list
        The weight of volume creation-destruction moves (its doubled in the
        overall sum of weigths because it's used for two moves).
    move_gauge : float or list
        The weight of gauge move.

    Returns
    -------
    tuple
        The same arguments given, after the manipulation.

    Raises
    ------
    ValueError
        If all three arguments are custom (i.e. lists), or the overall sum
        exceeds 1
    """

    weights = [move22, move24, move_gauge]

    for i in range(2):
        if type(weights[i]) == list:
            weights[i][0] *= 2
        else:
            weights[i] *= 2

    custom_w = [x for x in weights if type(x) == list]
    if len(custom_w) == 3:
        raise ValueError('Is possible to choose only two of the weights '
                         'for the three kinds of moves at the same time')
    elif len(custom_w) != 0:
        sum_ = sum([x[0] for x in custom_w])
        if sum_ > 1.:
            raise ValueError("The overall sum of moves' weights "
                             "must not exceed 1")
        weights_values = [x[0] if type(x) == list else x for x in weights]
        sum_defaults = sum(weights_values) - sum_
        for i in range(len(weights)):
            if weights[i] in custom_w:
                weights[i] = weights[i][0]
            else:
                weights[i] *= (1. - sum_) / sum_defaults

    for i in range(2):
        if type(weights[i]) == list:
            weights[i] = weights[i][0] / 2
        else:
            weights[i] /= 2
    return weights

def end_parser(end_condition):
    """Short summary.

    Parameters
    ----------
    end_condition : type
        Description of parameter `end_condition`.

    Returns
    -------
    int
        End condition for the subrun, in the format readable by simulations.
    int
        End condition for the run, as the number of seconds or steps.
    str
        Type of end_condition {'time'|'steps'}.
    """
    last_char = end_condition[-1]
    if last_char in ['s', 'm', 'h']:
        end_type = 'time'
        end_condition = int(float(end_condition[:-1]))
        if last_char == 'm':
            end_condition *= 60
        elif last_char == 'h':
            end_condition *= 60*60

        if end_condition < 600:
            end_partial = end_condition
        elif end_condition < 1e4:
            end_partial = end_condition // 5
        else:
            end_partial = 3600

    elif last_char.isdigit or end_condition[-1] in ['k', 'M', 'G']:
        end_type = 'steps'
        if last_char.isdigit:
            end_condition = int(float(end_condition))
        else:
            end_condition = int(float(end_condition[:-1]))
            if last_char == 'k':
                end_condition *= int(1e3)
            elif last_char == 'M':
                end_condition *= int(1e6)
            elif last_char == 'G':
                end_condition *= int(1e9)

        if end_condition < 6e7:
            end_partial = end_condition
        elif end_condition < 1e9:
            end_partial = end_condition // 5
        else:
            end_partial = 1e5 * 3600

        end_partial = int(end_partial)
    else:
        raise ValueError("End condition not recognized")

    return end_partial, end_condition, end_type

def color_mem(s, size=False):
    """ va a soglie:
            - sopra i 30M colora il testo verde
            - sopra i 60M colora il testo giallo
            - sopra i 150M colora il testo rosso
            - sopra i 400M colora lo sfondo rosso
        se size==True raddoppia le soglie
        se l'ultimo carattere è 'K' o un numero non fa nulla
        se è M applica le soglie
        se è diverso applica la soglia massima
    """
    return s

def color_num(s):
    return s

def color_lambda(s, details):
    # se qualcuno in details è colorato si colora del colore più grave
    return s

s = {-9: 'n',
     -6: 'u',
     -3: 'm',
     0: '',
     3: 'k',
     6: 'M',
     9: 'G',
     12: 'T',
     15: 'P',
     18: 'E',
     21: 'Z',
     24: 'Y'
     }

def eng_not(num):
    """Cast number in engeeniring notation

    Parameters
    ----------
    num : int
        the number to recast

    Returns
    -------
    str
        a string representing a 3-digit number,
        with engineering prefix for the exponent

    Raises
    ------
    IndexError
        - if the number is too big there are no SI prefixes
        - the function is for integers, so it not accepts numbers less than 1
    """
    if num < 0:
        num = -num
        sign = True
    else:
        sign = False

    e = int(floor(log10(num)))
    if e > 27:
        raise IndexError("Too big: there are no SI prefixes for exponents > 24")
    if e < -9:
        raise IndexError("Too small: no support for SI prefixes for exponents < -9")

    sx = s[e - (e % 3)]
    k = round(num / 10**e, 2) * 10**(e % 3)
    if k >= 100.:
        k = int(k)

    format_num = str(k) + sx
    if sign:
        format_num = '-' + format_num

    return format_num

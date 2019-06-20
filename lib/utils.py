# -*- coding: utf-8 -*-

#Created on Sun Jan 27 12:25:38 2019
"""
Collection of useful functions for CDT_2D project
"""
from os import scandir, popen
from re import search
from platform import node
from math import floor, log10

def lambdas_recast(lambda_list, is_range=False, is_all=False,
                   config='test', cmd=''):
    """Short summary.

    Parameters
    ----------
    lambda_list : type
        Description of parameter `lambda_list`.
    is_range : type
        Description of parameter `is_range`.
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

    lambdas_old = list(set(lambdas_old))
    if len(lambdas_old) > 0: lambdas_old.sort()
    lambdas_new = list(set(lambdas_new))
    if len(lambdas_new) > 0: lambdas_new.sort()

    return lambdas_old, lambdas_new

def find_all_availables(config='data', dir_prefix='Lambda'):
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
    config_dir = "output/" + config
    l = len(dir_prefix)

    directories = [x.name for x in scandir(config_dir) if x.is_dir()]
    matches = {x : search("-?\d*.?\d*", x[l:]) for x in directories if x[0:l] == dir_prefix}
    all_availables = [float(x[6:6+matches[x].end()]) for x in directories if x[0:l] == dir_prefix]
    all_availables.sort()

    return all_availables

def find_running():
    """Find running simulations and configs to which they belong.

    Returns
    -------
    list
        (lambdas, config) for running simulations.
    list
        other infos to be printed by `cdt2d state`
    """
    from os import environ

    if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
        ps_out = popen('ps -fu ' + environ['USER']).read().split('\n')
#        lambdas_run = [float(line.split()[-6]) \
#                       for line in ps_out[1:] if 'CDT_2D-Lambda' in line]
        lambdas_run = []
        sim_info = []
        PPID_list = []
        for line in ps_out[1:]:
            if 'CDT_2D-Lambda' in line:
                pinfos = line.split()
                Lambda = float(pinfos[-7])
                start_time = pinfos[6]
                run_id = pinfos[8]
                PID = pinfos[1]
                PPID = pinfos[2]
                lambdas_run += [[Lambda]]
                sim_info += [[start_time, run_id, PID, PPID]]
                PPID_list += [PPID]

        for line in ps_out[1:]:
            pinfos = line.split()
            if len(pinfos) > 0:
                try:
                    i = PPID_list.index(pinfos[1])
                except ValueError:
                    continue

                from re import split
                config = split('.*/output|/', pinfos[8])[2]
                lambdas_run[i] += [config]

    else:
        lambdas_run = []
        sim_info = []
        print("This platform is still not supported")

    return lambdas_run, sim_info

def authorization_request(what_to_do='', Lambda=None, extra_message=''):
    """Short summary.

    Parameters
    ----------
    what_to_do : type
        Description of parameter `what_to_do`.
    Lambda : type
        Description of parameter `Lambda`.
    extra_message : type
        Description of parameter `extra_message`.

    Returns
    -------
    type
        Description of returned object.

    """
    import readline

    if not Lambda == None:
        print("(λ = " + str(Lambda) + ") ", end='')
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

def end_parser(end_condition):
    """Short summary.

    Parameters
    ----------
    end_condition : type
        Description of parameter `end_condition`.

    Returns
    -------
    type
        Description of returned object.

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
            end_partial = str(int(end_condition)) + 's'
        elif end_condition < 1e4:
            end_partial = str(int(end_condition // 5)) + 's'
        else:
            end_partial = '1h'

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

        end_partial = str(int(end_partial))
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

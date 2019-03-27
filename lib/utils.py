# -*- coding: utf-8 -*-

#Created on Sun Jan 27 12:25:38 2019
"""
Collection of useful functions for CDT_2D project
"""
from os import scandir
from re import search
from shutil import rmtree
from math import floor, log10

def find_all_availables(config="data", dir_prefix="Lambda"):
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
    matches = {x : search("\d*.?\d*", x[l:]) for x in directories if x[0:l] == dir_prefix}
    all_availables = [float(x[6:6+matches[x].end()]) for x in directories if x[0:l] == dir_prefix]
    all_availables.sort()

    return all_availables

def clear_data(lambdas, config='test'):
    """Remove data for a given value of lambda

    Parameters
    ----------
    Lambda : float
        the parameter of the simulation whose data you want to remove
    """
    for Lambda in lambdas:
        try:
            rmtree("output/" + config + "/Lambda"+str(Lambda))
        except FileNotFoundError:
            all_lambdas = find_all_availables()
            raise ValueError("A folder with the given lambda it doesn't exist"+
                             "\n\t\t\t all_lambdas: " + str(all_lambdas))

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

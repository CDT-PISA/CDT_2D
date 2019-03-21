# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 12:25:38 2019

@author: alessandro
"""
from os.path import isdir
from os import mkdir, scandir
from re import search
from inspect import cleandoc
from shutil import rmtree
from math import floor, log10
from numpy import linspace

# commons

def find_all_availables(config="data", dir_prefix="Lambda"):
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
    """
    config_dir = "output/" + config
    
    directories = [x.name for x in scandir(config_dir) if x.is_dir()]
    matches = {x : search("\d*.?\d*",x[6:]) for x in directories if x[0:6] == dir_prefix}
    all_availables = [float(x[6:6+matches[x].end()]) for x in directories if x[0:6] == dir_prefix]
    all_availables.sort()
    
    return all_availables

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
    if(num < 0):
        num = -num
        sign = True
    else:
        sign = False
        
    e = int(floor(log10(num)))
    if(e>27):
        raise IndexError("non posso gestire numeri infinitamente grossi")
    if(e<-9):
        raise IndexError("non posso gestire numeri infinitamente piccoli")
        
    sx = s[e - (e % 3)]
    k = round(num / 10**e, 2) * 10**(e % 3)
    if(k >= 100.):
        k = int(k)
    
    format_num = str(k) + sx
    if sign:
         format_num = '-' + format_num
         
    return format_num

# test

def out_test():
    """Find the run folder in test configuration
    
    Find the first integer free for a new run.
    Is not intended to preserve chronological ordering,
    but only to find a unique folder for each test.
    
    Returns
    -------
    str
        the path to run folder, relative to project folder
    int
        the number of current run
    """
    # Find output directory
    outdir = "output/test/run"
    run_num = 1
    
    # todo: per non fare valanghe di tentativ inutili è meglio che legga il run corrente
    # dal file runs.txt, e se non esiste lascia run_num = 1
    while(isdir(outdir+str(run_num))):
        run_num += 1
    
    outdir += str(run_num)
    mkdir(outdir)
    
    return outdir, run_num

def clear_test():
    """Remove all the test simulation
    
        The function remove all the folders with test simulations' outputs,
        but not the checkpoints
    """
    rmtree("output/test/run")
    mkdir("output/test/run")

def clear_test_checkpoint():
    """Remove all the test checkpoints
    
        The function remove all the test checkpoints,
        but not the simulations' outputs
    """
    rmtree("output/test/run")
    mkdir("output/test/run")
    
# datas
    
def clear_data(Lambda):
    """Remove data for a given value of lambda
    
    Parameters
    ----------
    Lambda : float
        the parameter of the simulation whose data you want to remove
    """
    try:
        rmtree("output/data/Lambda"+str(Lambda))
    except FileNotFoundError:
        all_lambdas = find_all_availables()
        raise ValueError("A folder with the given lambda it doesn't exist"+#
                         "\n\t\t\t all_lambdas: " + str(all_lambdas))
    else:
        mkdir("output/data/Lambda"+str(Lambda))
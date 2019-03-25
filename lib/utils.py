# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 12:25:38 2019

@author: alessandro
"""
from os import scandir
from re import search
from shutil import rmtree
from math import floor, log10

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
    
def clear_data(lambdas, config='test'):
    """Remove data for a gi
    print('Work in progress')ven value of lambda
    
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
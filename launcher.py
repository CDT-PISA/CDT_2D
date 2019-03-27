#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Created on Fri Mar 15 11:18:52 2019
"""

"""

from os import chdir
from os.path import expanduser
from numpy import linspace
from lib.utils import find_all_availables, clear_data
import lib.test as test_cdt
import lib.data as data_cdt

def data(lambdas_old, lambdas_new):
    data_cdt.launch(lambdas_old, lambdas_new)

def show(lambdas_old, lambdas_new):
    data_cdt.show(lambdas_old, lambdas_new)
    
def clear(lambdas_old, lambdas_new):
    clear_data(lambdas_old, config='data')
    if len(lambdas_new) > 0:
        print("Following lambdas not found: ", lambdas_new)
    
def test(lambdas_old, lambdas_new):
    test_cdt.launch(lambdas_old, lambdas_new)

def checkpoint(lambdas_old, lambdas_new):
    test_cdt.show(lambdas_old, lambdas_new)
    
def clear_test(lambdas_old, lambdas_new):
    clear_data(lambdas_old, config='test')
    if len(lambdas_new) > 0:
        print("Following lambdas not found: ", lambdas_new)
    
def lambdas_recast(lambda_list, is_range=False, is_all=False, is_data=False, cmd=show):
    if len(lambda_list) == 0 and cmd in [show, checkpoint]:
        is_all = True
    
    if is_data:
        config = 'data'
    elif cmd in [data, show, clear]:
        config = 'test'
    else:
        raise NameError('Testo da scrivere (non dovresti poter arrivare qui\
                                                se non sei un comando nelle liste\
                                                di cui sopra)')
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
                lambdas = list(linspace(*lambda_list))
            else:
                raise ValueError('Testo da scrivere (#arg è quello di un range!)')
        else:
            lambdas = lambda_list
            
    if len(lambdas) > 0:
        lambdas_old = [x for x in lambdas if x in all_lambdas]
        lambdas_new = [x for x in lambdas if x not in lambdas_old]
            
    return lambdas_old, lambdas_new
    
from platform import node
import argparse
import sys

if(node() == 'Paperopoli'):
    import argcomplete

def main():
    
    chdir(expanduser('~/projects/CDT_2D'))
    
    parser = argparse.ArgumentParser(description='Manage CDT_2D simulations.')
    
    # todo: devo scriverci gli esempi di come si lancia
    #   tipo senza nulla con un numero
    #   oppure il tipo di numeri (e specificare che per '(x)','*' si deve mettere gli apici)
    # migliorare la descrizione di ogni comando
    
    # to add: state, stop, plot, clear_bin (with default argument '*' and the possibility of pass lambdas)
    
    sys.argv = [x if x != '°' else '-°' for x in sys.argv]
    sys.argv = [x if x != '@' else '-@' for x in sys.argv]
    
    # commands (mutually exclusive)
    group = parser.add_mutually_exclusive_group()
    
    group.add_argument('-d', '--data', dest='my_command', action='store_const', 
                       default=data, const=data, help='data')
    group.add_argument('-s', '--show', dest='my_command', action='store_const', 
                       const=show, help='show')
#    group.add_argument('--clear-data', dest='my_command', action='store_const', 
#                       const=clear_data_wrap, help='clear data')
#    group.add_argument('-t', '--test', dest='my_command', action='store_const',
#                       const=test, help='test')
#    group.add_argument('-c', '--checkpoint', dest='my_command', action='store_const', 
#                       const=checkpoint, help='checkpoint')
    group.add_argument('-c', '--clear', dest='my_command', action='store_const', 
                       const=clear, help='clear test')
    group.add_argument('--version', action='version', version='CDT_2D 0.0')
    
    parser.add_argument('-@', dest='is_data', action='store_true', 
                        help="data configuration flag (the '-' in front is not needed)")
    
    # lambdas
    parser.add_argument('lambdas', metavar='L', nargs='*', type=float, help='lambdas')
    
    lambdas_specifiers = parser.add_mutually_exclusive_group()
    lambdas_specifiers.add_argument('-°', dest='is_all', action='store_true', 
                        help="all (the '-' in front is not needed)")
    lambdas_specifiers.add_argument('-r', '--range', dest='is_range', action='store_true', help='range')
        
    if(node() == 'Paperopoli'):
        argcomplete.autocomplete(parser)
    args = parser.parse_args()
    
    cmds = [data, show, clear]
    test_config = {data  : test,
                   show  : checkpoint,
                   clear : clear_test
                   }
    if args.my_command in cmds:
        lambdas_old, lambdas_new = lambdas_recast(args.lambdas, args.is_range, 
                                                  args.is_all, args.is_data,
                                                  args.my_command)
        if args.is_data:
            args.my_command(lambdas_old, lambdas_new)
        else:
            test_config[args.my_command](lambdas_old, lambdas_new)
            
if __name__ == "__main__":
    main()
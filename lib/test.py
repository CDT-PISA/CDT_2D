# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:46 2019

@author: alessandro
"""

from os import mkdir, chdir, system, getcwd, scandir, remove
from shutil import copyfile
from re import split
from platform import node
import json
from subprocess import Popen
from numpy import histogram, median
from lib.utils import eng_not, find_running, recovery_history

def launch(lambdas_old, lambdas_new, linear_history, time, steps):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Descrizione...
    
    Parameters
    ----------
    p1 : tipo
        descrizione del primo parametro p1
    p2 : tipo
        descrizione del secondo parametro p2
    p3 : tipo, optional
        descrizione del terzo parametro opzionale p3
    
    Returns
    -------
    tipo
        descrizione del tipo di ritorno
        
    Raises
    ------
    Exception
        descrizione dell'eccezione lanciata
    """
    
    lambdas = lambdas_old + lambdas_new
    lambdas_run = find_running()
    
    project_folder = getcwd()
    
    for Lambda in lambdas:
        if not Lambda in lambdas_run:
            chdir(project_folder + '/output/test')
            
            dir_name = "Lambda" + str(Lambda)
            launch_script_name = 'launch_' + str(Lambda) + '.py'
            make_script_name = 'make_' + str(Lambda) + '.py'
            
            if Lambda in lambdas_old:
                with open(dir_name + "/state.json", "r+") as state_file: # @todo nei print c'è da
                                                                         # specificare il valore di Lambda
                    state = json.load(state_file)
                    if state['is_thermalized']:
                        print('Ha già finito idiota!') # @todo da migliorare
                        continue
                    
                    if state['last_run_succesful']:
                        run_num = state['run_done'] + 1
                    else:
                        print('Problem in the last run')
                        continue
                    
                checkpoints = [x.name for x in scandir(dir_name + "/checkpoint") \
                               if (split('_|\.|run', x.name)[1] == str(run_num - 1)
                               and x.name[-4:] != '.tmp')]
                checkpoints.sort()
                last_check = checkpoints[-1]
            else:
                mkdir(dir_name)
                mkdir(dir_name + "/checkpoint")
                mkdir(dir_name + "/history")
                mkdir(dir_name + "/bin")
                
                copyfile('../../lib/launch_script.py', dir_name + '/' + launch_script_name)
                copyfile('../../lib/make_script.py', dir_name + '/' + make_script_name)
                
                run_num = 1
                last_check = None
            
            # devo farlo qui perché prima non sono sicuro che dir_name esista ('mkdir(dir_name)')
            chdir(dir_name)
            if run_num > 1:
                recovery_history()
            
            if steps != '0':
                end_condition = steps
            else:
                end_condition = time
            
            TimeLength = 80
            debug_flag = 'false'
            arguments = [run_num, Lambda, TimeLength, end_condition, debug_flag, 
                         last_check, linear_history]
            arg_str = ''
            for x in arguments:
                arg_str += ' ' + str(x)
            
            make_script = Popen(["python3", make_script_name, str(run_num), 
                                 str(Lambda)])
            make_script.wait()
            
            if(node() == 'Paperopoli'):
                system('nohup python3 $PWD/' + launch_script_name + arg_str + ' &')
            elif(node() == 'fis-delia.unipi.it'):
                system('nohup python36 $PWD/' + launch_script_name + arg_str + ' &')
            elif(node() == 'gridui3.pi.infn.it'):
                system('bsub -q local -o stdout.txt -e stderr.txt -J ' + \
                       dir_name + ' $PWD/' + launch_script_name + arg_str)
            elif(node() == 'r000u06l01'):
                print('support for marconi still missing')
            else:
                raise NameError('Node not recognized (known nodes in data.py)')
        
def show(lambdas_old, lambdas_new):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Descrizione...
    
    Parameters
    ----------
    p1 : tipo
        descrizione del primo parametro p1
    
    Returns
    -------
    tipo
        descrizione del tipo di ritorno
    """
    
    if len(lambdas_old) == 0:
        print("There are no folders currently")
    else:
        print("  {} lambdas in the range requested".format(len(lambdas_old)))
        print(lambdas_old)
        
        hist_lambda = histogram(lambdas_old,20)
        highest = max(hist_lambda[0])
        
        print()
        for h in range(0,highest):
            for x in hist_lambda[0]:
                if(x >= highest - h):
                    print(' X ', end='')
                else:
                    print('   ', end='')
            print("")
        
        l_min = eng_not(min(lambdas_old))
        l_med = eng_not(median(lambdas_old))
        l_max = eng_not(max(lambdas_old))
        print(l_min, ' '*23, l_med, ' '*23, l_max)
        

def clear_bin():
    """
    Ripulisco tutti i binari che scritto nel frattempo
    """
    print(2)

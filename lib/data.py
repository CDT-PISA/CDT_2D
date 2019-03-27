# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:46 2019

@author: alessandro
"""

from os import mkdir, chdir, system, getcwd, scandir
from shutil import copyfile
from platform import node
import json
from numpy import histogram, median
from lib.utils import eng_not

def launch(lambdas_old, lambdas_new):
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
    
    project_folder = getcwd()
    
    for Lambda in lambdas:
        chdir(project_folder + '/output/data')
        
        dir_name = "Lambda" + str(Lambda)
        launch_script_name = 'launch_' + str(Lambda) + '.py'
        
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
                           if (x.name[3] == str(run_num - 1) and x.name[-4:] != '.tmp')]
            checkpoints.sort()
            last_check = checkpoints[-1]
        else:
            mkdir(dir_name)
            mkdir(dir_name + "/checkpoint")
            mkdir(dir_name + "/history")
            mkdir(dir_name + "/bin")
            
            copyfile('../../lib/launch_script.py', dir_name + '/' + launch_script_name)
            
            run_num = 1
            last_check = None
        
        # devo farlo qui perché prima non sono sicuro che dir_name esista ('mkdir(dir_name)')
        chdir(dir_name)
        
        # @todo aggiungere su json checkpoint
#        if(run_num != 1):
#            runs_history.write('\nstarted from checkpoint: ' + last_check)
        
        
#        arguments = [dir_name, Lambda, 5e5, 3]
        outdir = '.'
        TimeLength = 80
        attempts = 100000
        debug_flag = 'false'
        arguments = [dir_name, run_num, Lambda, outdir, TimeLength, attempts, 
                     debug_flag, last_check]
        arg_str = ''
        for x in arguments:
            arg_str += ' ' + str(x)
        
        if(node() == 'Paperopoli' or node() == 'fis-delia.unipi.it'):
            system('python3 $PWD/' + launch_script_name + arg_str)
            
        elif(node() == 'gridui3.pi.infn.it'):
            system('bsub -q local -o stdout.txt -e stderr.txt -J ' + \
                   dir_name + ' $PWD/' + launch_script_name + arg_str)
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
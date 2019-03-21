# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:46 2019

@author: alessandro
"""

from os import mkdir, chdir, system, getcwd, scandir
from shutil import copyfile
from platform import node
from datetime import datetime
from time import time
from re import search
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
            with open(dir_name + "/runs.txt", "r+") as runs:
                runs.seek(0)
                last_lines = list(enumerate(runs))[-2:-1]
                last_run = last_lines[0][1]
                
                match = search("RUN \d*", last_run)
                run_num = int(last_run[match.start()+4:match.end()]) + 1
                
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
            last_check = 'empty'
        
        chdir(dir_name)
        runs_history = open("runs.txt", "a")
        
        runs_history.write("#---------------- RUN " + str(run_num) + " ----------------#")
        
        timestamp = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')                       
        runs_history.write("\n" + timestamp)
        if(run_num != 1):
            runs_history.write('\nstarted from checkpoint: ' + last_check)
        
        runs_history.write("\n#-------------- END RUN " + str(run_num) + " --------------#\n\n")
        runs_history.close()
        
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
        
        if(node() == 'Paperopoli'):
            system('python3 $PWD/' + launch_script_name + arg_str)
            
        elif(node() == 'gridui3.pi.infn.it'):
            system('bsub -q theophys -o stdout.txt -e stderr.txt -J ' + \
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
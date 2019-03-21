# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:29 2019

@author: alessandro
"""

from os.path import getsize
from os import remove
from time import time
from datetime import datetime
from subprocess import run, CalledProcessError
from math import log
from numpy import histogram, median
from lib.analysis import analyze_output
from lib.utils import out_test, eng_not

def launch(lambdas):
    outdir, run_num = out_test()
    
    # Open files and write log
    runs_history = open(outdir+"/../runs.txt", "a")
    output_file = open(outdir+"/stdout.txt", "w")
    error_file = open(outdir+"/stderr.txt", "w")
    
    record = "run"+str(run_num)+": "+datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')+"\t\t"
    runs_history.write(record)
    
    # Simulation Arguments
    Lambda = log(2)
    TimeLength = 80
    attempts = 50000
    debug_flag = False
    loadfile = "osndv"
    Lambda_str = str(Lambda)
    TimeLength_str = str(TimeLength)
    attempts_str = str(attempts)
    debug_flag_str = str(debug_flag).lower()
    
    # Simulation run
    try:
        run(["bin/cdt_2d", outdir, Lambda_str, TimeLength_str, attempts_str, debug_flag_str, loadfile], stdout=output_file, stderr=error_file, text=True, check=True)
    except CalledProcessError as err:
        err_name = "<"+str(err).split("<")[1]
        runs_history.write("Il run "+str(run_num)+" del programma \""+err.cmd[0][-6:]+"\" è fallito con errore: "+err_name+"\n")
        succeed = False
    else:
        succeed = True
        runs_history.write("\n")
    finally:
    #    output_file.write("\n")
        output_file.close()
        if(getsize(output_file.name) == 0):
            remove(outdir+"/stdout.txt")
        error_file.close()
        if(getsize(error_file.name) == 0):
            remove(outdir+"/stderr.txt")
        runs_history.close()
    
    if(succeed):
        analyze_output(outdir)
        
def show(lambda_input='*'):
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
    
    lambdas = find_lambdas(lambda_input,'test')
    # print(lambdas)
    #
    # i lambda vanno trovati nei file di checkpoint!!!
    
    hist_lambda = histogram(lambdas,20)
    highest = max(hist_lambda[0])
    
    print()
    for h in range(0,highest):
        for x in hist_lambda[0]:
            if(x >= highest - h):
                print(' X ', end='')
            else:
                print('   ', end='')
        print("")
    
    l_min = eng_not(min(lambdas))
    l_med = eng_not(median(lambdas))
    l_max = eng_not(max(lambdas))
    print(l_min, ' '*23, l_med, ' '*23, l_max)

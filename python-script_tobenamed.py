# -*- coding: utf-8 -*-

from os.path import isdir, getsize
from os import mkdir, remove
from time import time
from datetime import datetime
from subprocess import run, CalledProcessError
from math import log
from lib.analysis import analyze_output

# Find output directory
outdir = "output/run"
run_num = 1

# todo: per non fare valanghe di tentativ inutili è meglio che legga il run corrente
# dal file runs.txt, e se non esiste lascia run_num = 1
while(isdir(outdir+str(run_num))):
    run_num += 1

outdir += str(run_num)
mkdir(outdir)

# Open files and write log
runs_history = open("output/runs.txt", "a")
output_file = open(outdir+"/stdout.txt", "w")
error_file = open(outdir+"/stderr.txt", "w")

record = "run"+str(run_num)+": "+datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')+"\t\t"
runs_history.write(record)

# Simulation Arguments
Lambda = 0.65
TimeLength = 80
attempts = 500000
debug_flag = False
Lambda_str = str(Lambda)
TimeLength_str = str(TimeLength)
attempts_str = str(attempts)
debug_flag_str = str(debug_flag).lower()
    
# Simulation run
try:
    run(["bin/cdt_2d", outdir, Lambda_str, TimeLength_str, attempts_str, debug_flag_str], stdout=output_file, stderr=error_file, text=True, check=True)
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
    
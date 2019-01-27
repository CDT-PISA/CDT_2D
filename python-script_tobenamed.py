# -*- coding: utf-8 -*-

from os.path import isdir
from os import mkdir
from time import time
from datetime import datetime
from subprocess import run, CalledProcessError
from lib.analysis import analyze_output

# Find output directory
outdir = "output/run"
run_num = 1

while(isdir(outdir+str(run_num))):
    run_num += 1

outdir += str(run_num)
mkdir(outdir)

# Open files and write log
runs_history = open("output/runs.txt","a")
output_file = open(outdir+"/stdout.txt","w")
error_file = open(outdir+"/stderr.txt","w")
    
record = "run"+str(run_num)+": "+datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')+"\n"
runs_history.write(record)

# Simulation Arguments
Lambda = 0
TimeLength = 101
attempts = 150
Lambda_str = str(Lambda)
TimeLength_str = str(TimeLength)
attempts_str = str(attempts)

# Simulation run
try:
    run(["bin/cdt_2d",outdir,Lambda_str,TimeLength_str,attempts_str],stdout=output_file,stderr=error_file,text=True,check=True)
except CalledProcessError as err:
    err_name = "<"+str(err).split("<")[1]
    runs_history.write("Il run "+str(run_num)+" del programma \""+err.cmd[0][-6:]+"\" è fallito con errore: "+err_name+"\n")
    succeed = False
else:
    error_file.write("tutto ok")
    succeed = True
finally:
    output_file.close()
    error_file.close()
    runs_history.close()
    
if(succeed):
    analyze_output(run_num)
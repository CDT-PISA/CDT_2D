# -*- coding: utf-8 -*-

from os.path import isdir
from os import mkdir
from time import time
from datetime import datetime

outdir = "output/run"
run_num = 1

while(isdir(outdir+str(run_num))):
    run_num += 1
    
#runs_history = open("output/runs","a")
log = "run"+str(run_num)+": "+datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')+"\n"
runs_history = open("output/runs.txt","a")
runs_history.write(log)
runs_history.close()
    
outdir += str(run_num)
mkdir(outdir)

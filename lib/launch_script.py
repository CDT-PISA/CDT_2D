# -*- coding: utf-8 -*-

#Created on Mon Mar 18 20:27:00 2019
"""
Script that manages the single simulations of CDT_2D, each values of lambda
has its own copy in its folder.
"""

from os import remove, stat, scandir
from sys import argv
from re import split
from subprocess import Popen, CalledProcessError
from datetime import datetime
from time import time
import json
from platform import node
from numpy import loadtxt

def main():
    run_num = argv[1]
    Lambda_str = argv[2]
    arguments = argv[1:]

    # is necessary to recompile each run because on the grid the node could be different
    exe_name = "CDT_2D-Lambda" + Lambda_str + "_run" + run_num

    log_file = open("runs.txt", "a")
    log_file.write("#---------------- RUN " + str(run_num) + " ----------------#")
    log_file.close()

    out = open('stdout.txt', 'a')
    err = open('stderr.txt', 'a')

    #out_f = open('stdout.txt', 'w')
    #sim = Popen(["bin/ciao"] + arguments)

    start_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')

    succesful = True
    try:
        sim = Popen(["bin/" + exe_name] + arguments, stdout = out, stderr = err)
        sim.wait()
    except CalledProcessError as e:
        print("Error '{0}' occured. Arguments {1}.".format(e, e.args))
        succesful = False
    
    out.close()
    err.close()
    
    iter_done = loadtxt('iterations_done')
    
    checkpoints = [x.name for x in scandir("checkpoint") \
                   if split('_|\.|run', x.name)[1] == str(run_num)]
    checkpoints.sort()
    if not succesful:
        if checkpoints[-1][-4:] == '.tmp':
            from numpy import savetxt
            vol_file = loadtxt('history/volumes.txt', dtype=int)
            pro_file = loadtxt('history/profiles.txt', dtype=int)
            vol_file = vol_file[vol_file[:,0] < iter_done]
            pro_file = pro_file[pro_file[:,0] < iter_done]
            savetxt('history/volumes.txt', vol_file, fmt='%d',
                    header='iteration[0] - volume[1]\n')
            savetxt('history/profiles.txt', pro_file, fmt='%d',
                    header='iteration[0] - profile[1:]\n')
    remove('iterations_done')

    if stat('stderr.txt').st_size != 0:
        succesful = False

    log_file = open("runs.txt", "a")
    end_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')
    if succesful:
        log_file.write("\n" + end_time + "\t Run COMPLETED")
    else:
        log_file.write("\n" + end_time + "\t Run FINISHED with ERRORS")
    log_file.write("\n#-------------- END RUN " + str(run_num) + " --------------#\n\n")
    log_file.close()

    is_thermalized = False
    if int(run_num) > 1:
        with open('state.json', 'r') as state_file:
            state = json.load(state_file)
        remove('state.json')
    else:
        state = {'Lambda': float(Lambda_str), 'run_done': 0, 'is_thermalized': is_thermalized,
                 'last_run_succesful': True, 'last_checkpoint': None, 'iter_done': 0}

    with open('state.json', 'w') as state_file:
        state['last_run_succesful'] = succesful
        state['start_time'] = start_time
        state['end_time'] = end_time
        state['run_done'] += 1
        state['iter_done'] = int(iter_done)
        if succesful:
            state['last_checkpoint'] = checkpoints[-1]
        else:
            state['last checkpoint'] = checkpoints[-2]
        json.dump(state, state_file, indent=4)
        
    if stat('nohup.out').st_size == 0:
        remove('nohup.out')

    if(node() != 'Paperopoli'):
        import smtplib
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        #   quando uno c'ha sbatta sarebbe carino trovare il modo di criptare la password
        server.login("cdt2d.email", "ciao_ciao")
        server.sendmail(
          "cdt2d.email@gmail.com",
          "candido.ale@gmail.com",
          "Il run" + run_num + " per lambda = " + Lambda_str + " e' finito")
        server.quit()

if __name__ == "__main__":
    main()

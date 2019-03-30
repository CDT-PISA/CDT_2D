# -*- coding: utf-8 -*-

#Created on Mon Mar 18 20:27:00 2019
"""
Script that manages the single simulations of CDT_2D, each values of lambda
has its own copy in its folder.
"""

from os import remove, getcwd
from sys import argv
from subprocess import Popen
from datetime import datetime
from time import time
import json
from platform import node

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
        sim = Popen(["bin/" + exe_name] + arguments, stdout=out)
        #sim = Popen(["bin/" + exe_name] + arguments, stdout = out, stderr = err)
        sim.wait()
    except Exception as e:
        print("Error '{0}' occured. Arguments {1}.".format(e, e.args))
        succesful = False

    log_file = open("runs.txt", "a")
    end_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')
    log_file.write("\n" + end_time + "\t Run COMPLETED")
    log_file.write("\n#-------------- END RUN " + str(run_num) + " --------------#\n\n")
    log_file.close()

    out.close()
    err.close()

    is_thermalized = False
    if int(run_num) > 1:
        with open('state.json', 'r') as state_file:
            state = json.load(state_file)
        remove('state.json')
    else:
        state = {'Lambda': float(Lambda_str), 'run_done': 0, 'is_thermalized': is_thermalized,
                 'last_run_succesful': True, 'last_checkpoint': None}

    with open('state.json', 'w') as state_file:
        state['last_run_succesful'] = succesful
        state['start_time'] = start_time
        state['end_time'] = end_time
        state['last_checkpoint'] = arguments[6]
        if succesful:
            state['run_done'] += 1
        json.dump(state, state_file, indent=4)

    print("\nRun " + run_num + " completed.\n")

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

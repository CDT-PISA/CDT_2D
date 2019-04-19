# -*- coding: utf-8 -*-

#Created on Mon Mar 18 20:27:00 2019
"""
Script that manages the single simulations of CDT_2D, each values of lambda
has its own copy in its folder.
"""

from os import remove, stat, scandir
from os.path import isfile
from sys import argv
from re import split
from subprocess import Popen, CalledProcessError
from datetime import datetime
from time import time
import json
from platform import node
from numpy import loadtxt

def run_sim(exe_name, arguments):    
    out = open('stdout.txt', 'a')
    err = open('stderr.txt', 'a')

    #out_f = open('stdout.txt', 'w')
    #sim = Popen(["bin/ciao"] + arguments)

    succesful = True
    try:
        sim = Popen(["bin/" + exe_name] + arguments, stdout = out, stderr = err)
        sim.wait()
    except CalledProcessError as e:
        print("Error '{0}' occured. Arguments {1}.".format(e, e.args))
        succesful = False
    
    out.close()
    err.close()
    
    if stat('stderr.txt').st_size != 0:
        succesful = False
       
    stopped = isfile('stop')
    if stopped:
        remove('stop')
    
    return succesful, stopped

def recovery_sim(run_id, succesful):
    iter_done = loadtxt('iterations_done')
    
    checkpoints = [x.name for x in scandir("checkpoint") \
                   if split('_|run', x.name)[1] == run_id]
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
    
    return checkpoints, iter_done

def log_header(run_id):
    log_file = open("runs.txt", "a")
    log_file.write("#---------------- RUN " + run_id + " ----------------#")
    log_file.close()

def log_footer(run_id, succesful):
    log_file = open("runs.txt", "a")
    end_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')
    if succesful:
        log_file.write("\n" + end_time + "\t Run COMPLETED")
    else:
        log_file.write("\n" + end_time + "\t Run FINISHED with ERRORS")
    log_file.write("\n#-------------- END RUN " + run_id + " --------------#\n\n")
    log_file.close()
    
def end_parser(end_condition):
       
    last_char = end_condition[-1]
    if last_char in ['s', 'm', 'h']:
        end_type = 'time'
        end_condition = int(float(end_condition[:-1]))
        if last_char == 'm':
            end_condition *= 60
        elif last_char == 'h':
            end_condition *= 60*60
            
        if end_condition < 600:
            end_partial = str(int(end_condition)) + 's'
        elif end_condition < 1e4:
            end_partial = str(int(end_condition // 5)) + 's'
        else:
            end_partial = '1h'
            
    elif last_char.isdigit or end_condition[-1] in ['k', 'M', 'G']:
        end_type = 'steps'
        if last_char.isdigit:
            end_condition = int(float(end_condition))
        else:
            end_condition = int(float(end_condition[:-1]))
            if last_char == 'k':
                end_condition *= int(1e3)
            elif last_char == 'M':
                end_condition *= int(1e6)
            elif last_char == 'G':
                end_condition *= int(1e9)
                
        if end_condition < 6e7:
            end_partial = end_condition
        elif end_condition < 1e9:
            end_partial = end_condition // 5
        else:
            end_partial = 1e5 * 3600
            
        end_partial = str(int(end_partial))
    else:
        raise ValueError("End condition not recognized")
        
    return end_partial, end_condition, end_type

def remove_from_stopped(Lambda):
    import pickle
    
    try:
        with open('../pstop.pickle','rb') as stop_file:
            lambdas_stopped = pickle.load(stop_file)
    except FileNotFoundError:
        raise FileNotFoundError("Ci dev'essere, perché il processo è ancora \
                                in corso e quindi state non può averlo \
                                eliminato")    
    lambdas_stopped.remove(Lambda)
    
    with open('../pstop.pickle','wb') as stop_file:
        pickle.dump(lambdas_stopped, stop_file)
        
    return

def main():
    run_num = argv[1]
    Lambda_str = argv[2]
    arguments = argv[1:]
    
    if(node() == 'gridui3.pi.infn.it' or node()[0:4] == 'r000'):
        import smtplib
        from email.message import EmailMessage
        
        if int(run_num) > 1:
            with open('state.json', 'r') as state_file:
                state = json.load(state_file)
        else:
            state = {'Lambda': float(Lambda_str), 'run_done': 0}
            
        msg = EmailMessage()
        msg.set_content(json.dumps(state, indent=4)[1:-1])
        msg['Subject'] = "Lambda" + Lambda_str + " inizia il run " + run_num
        msg['From'] = "cdt2d.email@gmail.com"
        msg['To'] = "candido.ale@gmail.com"
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # quando uno c'ha sbatta sarebbe carino trovare il modo di criptare
        # la password
        server.login("cdt2d.email", "ciao_ciao")
        server.sendmail(msg)
        server.quit()
        
    # IMPORT FROM LIB
    from sys import path
    from os.path import realpath
    path += [realpath('../../..')] # CDT_2D project_folder
    from lib.analysis import is_thermalized
    
    if int(run_num) > 1:
        with open('state.json', 'r') as state_file:
            state = json.load(state_file)
            
        if state['is_thermalized'] and arguments[6] == '0':
            arguments[6] = '1M'
            
        arguments[2] = state['timelength']
    else:
        state = {'Lambda': float(Lambda_str), 'run_done': 0, 
                 'is_thermalized': False, 'last_checkpoint': None,
                 'iter_done': 0, 'timelength': arguments[2]}
    
    # END CONDITION MANIPULATION
    # needed for thermalization loop
    arguments[3], end_condition, end_type = end_parser(arguments[3])
    
    if not arguments[6] == '0':
        arguments[3] == end_condition

    # is necessary to recompile each run because on the grid the launch node
    # could be different from run_node
    exe_name = "CDT_2D-Lambda" + Lambda_str + "_run" + run_num

    start_record = time()
    start_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')
    state['start_time'] = start_time
    state['linear-history'] = not (arguments[6] == '0')
    with open('state.json', 'w') as state_file:
        json.dump(state, state_file, indent=4)
    
    run_id = str(run_num)
    log_header(run_id)
    succesful, stopped = run_sim(exe_name, arguments)
    checkpoints, iter_done = recovery_sim(run_id, succesful)
    log_footer(run_id, succesful)
    
    # lo eseguo solo se non è termalizzato
    # serve appunto a controllare se termalizza
    if arguments[6] == '0':
        rerun = 0
        if end_type == 'time':
            end_run = (time() - start_record) > end_condition
        elif end_type == 'steps':
            end_run = iter_done > end_condition
        
        while succesful and not is_thermalized() and not end_run and not stopped:
            rerun += 1
            run_id = str(run_num) + '.' + str(rerun)
            arguments[0] = run_id
            
            log_header(run_id)
            arguments[5] = checkpoints[-1]
            succesful, stopped = run_sim(exe_name, arguments)
            
            checkpoints, iter_done = recovery_sim(run_id, succesful)
            log_footer(run_id, succesful)
            
            if end_type == 'time':
                end_run = (time() - start_record) > end_condition
            elif end_type == 'steps':
                end_run = iter_done > end_condition
        
    end_time = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')

    with open('state.json', 'w') as state_file:
        state['last_run_succesful'] = succesful
        state['end_time'] = end_time
        state['run_done'] += 1
        state['iter_done'] = int(iter_done)
        if not state['is_thermalized'] and not state['run_done'] == 1:
            state['is_thermalized'] = is_thermalized()
        if succesful:
            state['last_checkpoint'] = checkpoints[-1]
        else:
            state['last checkpoint'] = checkpoints[-2]
        json.dump(state, state_file, indent=4)
        
    if stat('nohup.out').st_size == 0:
        remove('nohup.out')
    if stat('stdout.txt').st_size == 0:
        remove('stdout.txt')
    if stat('stderr.txt').st_size == 0:
        remove('stderr.txt')
        
    if stopped:
        remove_from_stopped(float(Lambda_str))
            
    if(node() != 'Paperopoli'):
        import smtplib
        from email.message import EmailMessage
        
        with open('state.json', 'r') as state_file:
            state = json.load(state_file)
            
        msg = EmailMessage()
        msg.set_content(json.dumps(state, indent=4)[1:-1])
        msg['Subject'] = "Lambda" + Lambda_str + " ha finito il run " + run_num
        msg['From'] = "cdt2d.email@gmail.com"
        msg['To'] = "candido.ale@gmail.com"
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # quando uno c'ha sbatta sarebbe carino trovare il modo di criptare
        # la password
        server.login("cdt2d.email", "ciao_ciao")
        server.sendmail(msg)
        server.quit()

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-

#Created on Mon Mar 18 20:27:00 2019
"""
Script that manages the single simulations of CDT_2D, each couples
(lambda, beta) (in general each instance of CDT_2D simulation) has its own copy
of this file in its folder.
"""

from os import remove, stat, scandir
from os.path import isfile
from sys import argv
from re import split
from subprocess import run, CalledProcessError
from datetime import datetime
from time import time
import json
from platform import node
from numpy import loadtxt

def run_sim(exe_name, arguments):
    out = open('stdout.txt', 'a')
    err = open('stderr.txt', 'a')

    succesful = True
    try:
        sim = run(["bin/" + exe_name] + arguments, stdout = out, stderr = err)
        sim.check_returncode()
    except CalledProcessError as e:
        print(f"Error:\n{e.returncode}\n\n")
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
            pro_file = loadtxt('history/gauge.txt', dtype=int)
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
    log_file.write("\n#-------------- END RUN " +
                   run_id + " --------------#\n\n")
    log_file.close()

def remove_from_stopped(Lambda, Beta):
    import pickle
    Point = (Lambda, Beta)

    try:
        with open('../pstop.pickle','rb') as stop_file:
            points_stopped = pickle.load(stop_file)
    except FileNotFoundError:
        raise FileNotFoundError("Ci dev'essere, perché il processo è ancora \
                                in corso e quindi state non può averlo \
                                eliminato")
    points_stopped.remove(Point)

    with open('../pstop.pickle','wb') as stop_file:
        pickle.dump(points_stopped, stop_file)

    return

def start_mail(run_num, Lambda, Beta):
    if(node() == 'gridui3.pi.infn.it' or node()[0:4] == 'r000'):
        import smtplib
        from email.message import EmailMessage

        if int(run_num) > 1:
            with open('state.json', 'r') as state_file:
                state = json.load(state_file)
        else:
            state = {'Lambda': float(Lambda), 'Beta': float(Beta),
                     'run_done': 0}

        msg = EmailMessage()
        msg.set_content(json.dumps(state, indent=4)[1:-1])
        msg['Subject'] = "Lambda" + Lambda + "Beta" + Beta +\
                         " inizia il run " + run_num
        msg['From'] = "cdt2d.email@gmail.com"
        msg['To'] = "candido.ale@gmail.com"

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # quando uno c'ha sbatta sarebbe carino trovare il modo di criptare
        # la password
        server.login("cdt2d.email", "ciao_ciao")
        server.sendmail(msg)
        server.quit()

def end_mail(run_num, Lambda, Beta):
    if(node() != 'Paperopoli'):
        import smtplib
        from email.message import EmailMessage

        with open('state.json', 'r') as state_file:
            state = json.load(state_file)

        msg = EmailMessage()
        msg.set_content(json.dumps(state, indent=4)[1:-1])
        msg['Subject'] = "Lambda" + Lambda + "Beta" + Beta +\
                         " ha finito il run " + run_num
        msg['From'] = "cdt2d.email@gmail.com"
        msg['To'] = "candido.ale@gmail.com"

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        # quando uno c'ha sbatta sarebbe carino trovare il modo di criptare
        # la password
        server.login("cdt2d.email", "ciao_ciao")
        server.sendmail(msg)
        server.quit()

def main(run_num, Lambda, Beta, time_length, end_condition,
             debug_flag, last_check, linear_history,
             adj_flag, move22, move24,
             end_partial, end_type, exe_name):
    """All parameters are considered to be string.

    Parameters
    ----------
    run_num : type
        Description of parameter `run_num`.
    Lambda : type
        Description of parameter `Lambda`.
    Beta : type
        Description of parameter `Beta`.
    time_length : type
        Description of parameter `time_length`.
    end_condition : type
        Description of parameter `end_condition`.
    debug_flag : type
        Description of parameter `debug_flag`.
    last_check : type
        Description of parameter `last_check`.
    linear_history : type
        Description of parameter `linear_history`.
    adj_flag : type
        Description of parameter `adj_flag`.
    move22 : type
        Description of parameter `move22`.
    move24 : type
        Description of parameter `move24`.
    end_partial : type
        Description of parameter `end_partial`.
    end_type : type
        Description of parameter `end_type`.
    exe_name : type
        Description of parameter `exe_name`.
    """

    start_mail(run_num, Lambda, Beta)

    # IMPORT FROM LIB
    from sys import path
    from os.path import realpath
    path += [realpath('../../..')] # CDT_2D project_folder
    from lib.analysis import is_thermalized

    with open('state.json', 'r') as state_file:
        state = json.load(state_file)

    start_record = time()
    start_time = datetime.fromtimestamp(start_record)\
                         .strftime('%d-%m-%Y %H:%M:%S')
    state['start_time'] = start_time
    state['linear-history'] = not (linear_history == '0')
    with open('state.json', 'w') as state_file:
        json.dump(state, state_file, indent=4)

    arguments = [run_num,
                 Lambda,
                 Beta,
                 time_length,
                 end_partial,
                 debug_flag,
                 last_check,
                 linear_history,
                 adj_flag,
                 move22,
                 move24]
    run_id = str(run_num)
    log_header(run_id)
    succesful, stopped = run_sim(exe_name, arguments)
    checkpoints, iter_done = recovery_sim(run_id, succesful)
    log_footer(run_id, succesful)

    # lo eseguo solo se non è termalizzato
    # serve appunto a controllare se termalizza
    end_condition = int(end_condition)
    if not linear_history != '0':  # i.e. `if not linear_history:`
        rerun = 0
        if end_type == 'time':
            end_run = (time() - start_record) > end_condition
        elif end_type == 'steps':
            end_run = iter_done > end_condition

        max_volume_reached = isfile('max_volume_reached') 

        while (succesful and not is_thermalized() and not end_run
               and not stopped and not max_volume_reached):
            rerun += 1
            run_id = str(run_num) + '.' + str(rerun)
            arguments[0] = run_id

            log_header(run_id)
            arguments[6] = checkpoints[-1]
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
            if len(checkpoints) >= 2:
                state['last_checkpoint'] = checkpoints[-2]
            else:
                state['last_checkpoint'] = checkpoints[-1]
                print('\nUnsuccesful run from the beginning.')
        json.dump(state, state_file, indent=4)

    if stat('nohup.out').st_size == 0:
        remove('nohup.out')
    if stat('stdout.txt').st_size == 0:
        remove('stdout.txt')
    if stat('stderr.txt').st_size == 0:
        remove('stderr.txt')

    if stopped:
        remove_from_stopped(float(Lambda), float(Beta))

    end_mail(run_num, Lambda, Beta)

if __name__ == "__main__":
    args = argv[1:]
    main(*args)

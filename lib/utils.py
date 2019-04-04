# -*- coding: utf-8 -*-

#Created on Sun Jan 27 12:25:38 2019
"""
Collection of useful functions for CDT_2D project
"""
from os import scandir, chdir, popen
from re import search, split
from platform import node
from shutil import rmtree
from math import floor, log10

def find_all_availables(config="data", dir_prefix="Lambda"):
    """Find all lambdas for which a simulation has been already run

    Parameters
    ----------
    config : str
        the configuration ('data', 'test', ...)
    dir_prefix : str
        the name of the directory that precedes the value
        of lambda *(the number must start from the subsequent
        character)*

    Returns
    -------
    list
        a list of the existing values of lambda
    """
    config_dir = "output/" + config
    l = len(dir_prefix)

    directories = [x.name for x in scandir(config_dir) if x.is_dir()]
    matches = {x : search("\d*.?\d*", x[l:]) for x in directories if x[0:l] == dir_prefix}
    all_availables = [float(x[6:6+matches[x].end()]) for x in directories if x[0:l] == dir_prefix]
    all_availables.sort()

    return all_availables

def find_running():
    """
    @todo: scrivere la docstring
    """
    from os import environ
    
    if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
        ps_out = popen('ps -fu ' + environ['USER']).read().split('\n')
#        lambdas_run = [float(line.split()[-6]) \
#                       for line in ps_out[1:] if 'CDT_2D-Lambda' in line]
        lambdas_run = []
        sim_info = []
        PPID_list = []
        for line in ps_out[1:]:
            if 'CDT_2D-Lambda' in line:
                pinfos = line.split()
                Lambda = float(pinfos[-6])
                start_time = pinfos[6]
                run_id = pinfos[8]
                PID = pinfos[1]
                PPID = pinfos[2]
                lambdas_run += [[Lambda]]
                sim_info += [[start_time, run_id, PID]]
                PPID_list += [PPID]
                
        for line in ps_out[1:]:
            pinfos = line.split()
            if len(pinfos) > 0:
                try:
                    i = PPID_list.index(pinfos[1])
                except ValueError:
                    continue
                
                from re import split
                config = split('.*/output|/', pinfos[8])[2]
                lambdas_run[i] += [config]
        
    else:
        lambdas_run = []
        sim_info = []
        print("This platform is still not supported")
    
    return lambdas_run, sim_info

def show_state(configs, full_show=False):
    # @todo: add support for the other platforms
    # @todo: for clusters: add 'pending' state
    import pickle
    from os import environ
    from datetime import datetime
    from time import time
    
    if not type(configs) == list:
        configs = [configs]
    
    if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
        ps_out = popen('ps -fu ' + environ['USER']).read().split('\n')
    else:
        ps_out = []
        print("This platform is still not supported")
    
    empty = len([1 for line in ps_out if 'CDT_2D-Lambda' in line]) == 0
    if len(ps_out) > 1 and not empty:
        print('   LAMBDA\t   TIME\t     STATUS\t CONFIG', end='')
        if not full_show:
            print()
        else:
            print('\t   RUN_ID    PID')
        
        lambdas_run_all, sim_all = find_running()
        
        d = {}
        for config in configs:
            lambdas_run_list = []
            sim_list = []
            for i in range(0, len(sim_all)):
                if lambdas_run_all[i][1] == config:
                    lambdas_run_list += [lambdas_run_all[i]]
                    sim_list += [sim_all[i]]
            d[config] = lambdas_run_list, sim_list
    
    for config in configs:
        try:
            with open('output/' + config + '/pstop.pickle','rb') as stop_file:
                lambdas_stopped = pickle.load(stop_file)
        except FileNotFoundError:
            lambdas_stopped = []
        
        if len(ps_out) > 1 and not empty:
            
            lambdas_run_list, sim_list = d[config]
            
            for i in range(0,len(sim_list)):
                lambdas_run = lambdas_run_list[i]
                sim = sim_list[i]
                Lambda = lambdas_run[0]
                l_conf = lambdas_run[1]
                if Lambda in lambdas_stopped:
                    state = 'killed'
                else:
                    state = 'running'
                print(str(Lambda).rjust(9), '\t', sim[0], '  ', state, '\t',
                      l_conf, end='')
                if not full_show:
                    print()
                else:
                    print(' ', sim[1].rjust(10), '  ', sim[2])
                        
            lambdas_run = [x[0] for x in lambdas_run_list if x[1] == config]
            l_aux = []
            for Lambda in lambdas_stopped:
                if Lambda in lambdas_run:
                    l_aux += [Lambda]
            lambdas_stopped = l_aux
        else:
            lambdas_stopped = []
        
        with open('output/' + config + '/pstop.pickle','wb') as stop_file:
                pickle.dump(lambdas_stopped, stop_file)
        
    if len(ps_out) > 1 and not empty:
        clock = datetime.fromtimestamp(time()).strftime('%H:%M:%S')
        print('\n [CLOCK: ' + clock + ']')

def sim_info(Lambda, config):
    chdir('output/' + config + '/Lambda' + str(Lambda))
    
    import json
    
    with open('state.json', 'r') as state_file:
            state = json.load(state_file)
            
    print(json.dumps(state, indent=4)[1:-1])
    

def recovery_history():
    """
    assume di essere chiamata nella cartella corretta
    
    @todo: aggiungere check, se fallisce risponde che è nel posto sbagliato
    e non fa nulla
    """
    import json
    
    with open('state.json', 'r') as state_file:
            state = json.load(state_file)
    succesful = state['last_run_succesful']
    run_num = state['run_done']
    iter_done = state['iter_done']
    
    checkpoints = [x.name for x in scandir("checkpoint") \
                   if split('_|\.|run', x.name)[1] == str(run_num)]
    checkpoints.sort()
    if not succesful:
        if checkpoints[-1][-4:] == '.tmp':
            from numpy import loadtxt, savetxt
            vol_file = loadtxt('history/volumes.txt', dtype=int)
            pro_file = loadtxt('history/profiles.txt', dtype=int)
            vol_file = vol_file[vol_file[:,0] < iter_done]
            pro_file = pro_file[pro_file[:,0] < iter_done]
            savetxt('history/volumes.txt', vol_file, fmt='%d',
                    header='iteration[0] - volume[1]\n')
            savetxt('history/profiles.txt', pro_file, fmt='%d',
                    header='iteration[0] - profile[1:]\n')

def clear_data(lambdas, config='test'):
    """Remove data for a given value of lambda

    Parameters
    ----------
    Lambda : float
        the parameter of the simulation whose data you want to remove
    """
    from inspect import cleandoc
    
    for Lambda in lambdas:
        try:
            if not config == 'test':
                import readline
                print(cleandoc("""Do you really want to remove simulation
                      folder for Lambda = """) + str(Lambda) + " ? [y/n]")
                authorized = False
                ans_recog = False
                count = 0
                while not ans_recog and count < 3:
                    count += 1
                    ans = input('--> ')
                    ans_recog = True
                    if ans != 'y' and ans != 'n':
                        ans_recog = False
                        print('Answer not recognized', end='')
                        if count < 3:
                            print(', type it again [y/n]')
                        else:
                            print()
                    elif ans == 'y':
                        authorized = True
            else:
                    authorized = True
            if authorized:
                rmtree("output/" + config + "/Lambda"+str(Lambda))
        except FileNotFoundError:
            all_lambdas = find_all_availables()
            raise ValueError("A folder with the given lambda it doesn't exist"+
                             "\n\t\t\t all_lambdas: " + str(all_lambdas))

s = {-9: 'n',
     -6: 'u',
     -3: 'm',
     0: '',
     3: 'k',
     6: 'M',
     9: 'G',
     12: 'T',
     15: 'P',
     18: 'E',
     21: 'Z',
     24: 'Y'
     }

def eng_not(num):
    """Cast number in engeeniring notation

    Parameters
    ----------
    num : int
        the number to recast

    Returns
    -------
    str
        a string representing a 3-digit number,
        with engineering prefix for the exponent

    Raises
    ------
    IndexError
        - if the number is too big there are no SI prefixes
        - the function is for integers, so it not accepts numbers less than 1
    """
    if num < 0:
        num = -num
        sign = True
    else:
        sign = False

    e = int(floor(log10(num)))
    if e > 27:
        raise IndexError("Too big: there are no SI prefixes for exponents > 24")
    if e < -9:
        raise IndexError("Too small: no support for SI prefixes for exponents < -9")

    sx = s[e - (e % 3)]
    k = round(num / 10**e, 2) * 10**(e % 3)
    if k >= 100.:
        k = int(k)

    format_num = str(k) + sx
    if sign:
        format_num = '-' + format_num

    return format_num

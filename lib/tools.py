#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 18:56:03 2019

@author: alessandro
"""

def recovery_history(force=False):
    """
    assume di essere chiamata nella cartella corretta
    
    @todo: aggiungere check, se fallisce risponde che è nel posto sbagliato
    e non fa nulla
    """
    from os import scandir
    from re import split
    import json
    
    with open('state.json', 'r') as state_file:
            state = json.load(state_file)
    succesful = state['last_run_succesful']
    run_num = state['run_done']
    iter_done = state['iter_done']
    
    checkpoints = [x.name for x in scandir("checkpoint") \
                   if split('_|\.|run', x.name)[1] == str(run_num)]
    checkpoints.sort()
    recovery = False
    if not succesful:
        if checkpoints[-1][-4:] == '.tmp':
            recovery = True
    elif force:
        from lib.utils import authorization_request
        print("ATTENTION: You are trying to recovery a succesful simulation!")
        recovery = authorization_request('to do it')
            
    if recovery:
        from numpy import loadtxt, savetxt
        vol_file = loadtxt('history/volumes.txt', dtype=int)
        pro_file = loadtxt('history/profiles.txt', dtype=int)
        vol_file = vol_file[vol_file[:,0] < iter_done]
        pro_file = pro_file[pro_file[:,0] < iter_done]
        savetxt('history/volumes.txt', vol_file, fmt='%d',
                header='iteration[0] - volume[1]\n')
        savetxt('history/profiles.txt', pro_file, fmt='%d',
                header='iteration[0] - profile[1:]\n')

def sim_info(Lambda, config):
    from os import chdir
    
    chdir('output/' + config + '/Lambda' + str(Lambda))
    
    import json
    
    with open('state.json', 'r') as state_file:
            state = json.load(state_file)
            
    print(json.dumps(state, indent=4)[1:-1])
    
def therm(lambdas_old, config, is_therm, force):
    import json
    from lib.utils import find_running, authorization_request
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
    
    lambdas_av = [l for l in lambdas_old if l not in lambdas_run]
    lambdas_not_av = [l for l in lambdas_old if l in lambdas_run]
    
    if len(lambdas_not_av) > 0:
        print("Simulations for following λ were already running: ", 
              lambdas_not_av)
        if len(lambdas_av) > 0:
            print()
    
    for Lambda in lambdas_av:
        if not config == 'test' and not force:
            what_to_do = "to set thermalization flag `" + str(is_therm) + "`"
            authorized = authorization_request(what_to_do, Lambda)
        else:
            authorized = True
        if authorized:
            filename = ('output/' + config + '/Lambda' + str(Lambda) +
                        '/state.json')
            with open(filename, 'r') as state_file:
                state = json.load(state_file)
                state['is_thermalized'] = eval(is_therm)
                if state['is_thermalized']:
                    state['therm_from'] = state['iter_done']
                elif 'therm_from' in state.keys():
                    state.pop('therm_from')
                    
            if state['is_thermalized']:
                neg = ''
            else:
                neg = 'un'
                
            print('Thermalization ' + neg + 'setted for λ = ' + str(Lambda))
            if state['is_thermalized']:
                print('Iteration before therm: ' + str(state['iter_done']))
                
            with open(filename, 'w') as state_file:
                json.dump(state, state_file, indent=4)
                
def up_launch(lambdas_old, config, both, make, force):
    from os import getcwd, chdir
    from shutil import copyfile
    from lib.utils import find_running, authorization_request
    
    proj_dir = getcwd()
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
        
    for l in lambdas_old:
        if l not in lambdas_run:
            if not config == 'test' and not force:
                what_to_do = "to update launch/make scripts"
                authorized = authorization_request(what_to_do, l)
            else:
                authorized = True
            if authorized:
                chdir('output/' + config + '/Lambda' + str(l))
                if both or make:
                    make_script_name = 'make_' + str(l) + '.py'  
                    copyfile('../../../lib/make_script.py', make_script_name)
                if both or not make:
                    launch_script_name = 'launch_' + str(l) + '.py' 
                    copyfile('../../../lib/launch_script.py', launch_script_name)
                chdir(proj_dir) 
                
def remove(lambdas_old, config, force, cbin, check):
    from os import chdir, popen
    from re import split
    import readline
    
    chdir('output/' + config)
    
    if not cbin == None:
        what = 'bin'
    elif not check == None:
        what = 'checkpoint'
    else:
        print('Specify what to remove.')
        return
    
    if len(lambdas_old) > 0:
        print()
        print("In what follows: \nuse numbers '> 0' to specify last run you " + 
              "want to remove, \n'< 0' to specify distance from last " + 
              "present, 0 to skip." + 
              "\n\nOnly λ with more than one run present are shown.\n")
        
    for l in lambdas_old:
        files = popen('ls -1 Lambda' + str(l) + '/' + what).read().split('\n')
        runs = []
        for x in files[:-1]:
            y = split('run|_|\.', x)
            if what == 'bin':
                runs += [int(y[-1])]
            elif what == 'checkpoint':
                runs += [int(y[1])]
        runs = list(set(runs))
        if runs == []:
            continue
        elif max(runs) == min(runs):
            continue
        print('(λ = ' + str(l) + ') The last ' + what + 's are from the run ' + 
              str(max(runs)) + '.')
        print('Until what run do you want to remove ' + what + 's?' + 
              ' (default: 0)')
        valid = False
        count = 0
        while not valid and count < 3:
            count += 1
            try:
                ans = input('--> ')
            except EOFError:
                ans = ''
                print()
                
            valid = True
            if ans == '':
                ans = 0
            elif ans == 'q' or ans == 'quit':
                ans = 'q'
            else:
                try:
                    ans = int(ans)
                    if abs(ans) >= max(runs):
                        raise ValueError
                except ValueError:
                    valid = False
                    print('Answer not valid', end='')
                    if count < 3:
                        print(', type it a valid one')
                    else:
                        ans = 0
                        print(' (nothing done)')
        if ans == 0:
            if count < 3:
                print('Nothing done for λ = ' + str(l) + '\n')
            continue
        elif ans == 'q':
            print('Nothing done for λ = ' + str(l) + '\n')
            break
        elif ans > 0:
            last = ans
        elif ans < 0:
            last = max(runs) + ans
            
        for run in runs:
            if run <= last:
                if what == 'bin':
                    popen('rm Lambda' + str(l) + '/bin/*run' + str(run)).read()
                elif what == 'checkpoint':
                    popen('rm Lambda' + str(l) + '/checkpoint/run' +
                          str(run) + '*').read()
                print('Removed ' + what + 's for run ' + str(run))
                
        print()
                
def remote(lambdas_old, lambdas_new, config, upload, download, force, rshow):
    from os import popen
    import json
    from lib.utils import find_running, authorization_request
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
    
    lambdas_av = [l for l in lambdas_old if l not in lambdas_run]
    if download:
        action = 'download'
        lambdas_av += lambdas_new
        
    lambdas_not_av = [l for l in lambdas_old if l in lambdas_run]
    if upload:
        action = 'upload'
        lambdas_not_av += lambdas_new  
    
    if len(lambdas_not_av) > 0:
        print("Following λ not available for " + action + ": ", lambdas_not_av)
        if len(lambdas_av) > 0:
            print()
            
    with open('config.json', 'r') as config_file:
        proj_configs = json.load(config_file)    
    rclone_remote = proj_configs['rclone_remote']
    remote_path = proj_configs['rclone_path']
        
    if not rshow:
        # in upload è solo lambdas_old, mentre in download c'è anche new
        for l in lambdas_av:
            if not config == 'test' and not force and l not in lambdas_new:
                what_to_do = 'to ' + action + ' the sim folder'
                authorized = authorization_request(what_to_do, l)
                if authorized == 'quit':
                    break
            else:
                authorized = True
            if authorized:
                local_dir = 'output/' + config + '/Lambda' + str(l)
                remote_dir = (rclone_remote + ':' + remote_path + '/CDT_2D/' +
                              config + '/Lambda' + str(l))
                if upload:
                    print("(λ = " + str(l) + ") uploading...")
                    source = local_dir
                    dest = remote_dir
                elif download:
                    print("(λ = " + str(l) + ") downloading...")
                    source = remote_dir
                    dest = local_dir
                popen('rclone copy ' + source + ' ' + dest).read()
    else:
        from lib.data import show
        dirs = popen('rclone lsd ' + rclone_remote + ':' + remote_path + 
              '/CDT_2D/' + config).read().split('\n')
        lambdas = [float(x.split('Lambda')[1]) for x in dirs[:-1]]
        
        show(lambdas, config)
            
                    
def config(email=None, remote=None, path=None, show=False):
    import json
    
    try:
        config_file = open('config.json', 'r')
        configurations = json.load(config_file)
    except FileNotFoundError:
        configurations = {'receiver_email': None, 'rclone_remote': None,
                          'rclone_path': None}
    
    if not email == None:
        if email == '-':
            email = configurations['receiver_email']
            print('Enter a valid email adress to receive notifications ' + 
                  'of run endings:')
            ans = input('--> ')
            if ans != '':
                email = ans
        configurations['receiver_email'] = email
    if not remote == None:
        if remote == '-':
            remote = configurations['rclone_remote']
            print('Enter a valid remote for rclone:')
            ans = input('--> ')
            if ans != '':
                remote = ans
        configurations['rclone_remote'] = remote
    if not path == None:
        if path == '-':
            path = configurations['rclone_path']
            print('Enter a valid path in rclone remote:')
            print(' (It has to contain a folder named "CDT_2D"')
            ans = input('--> ')
            if ans != '':
                path = ans
        configurations['rclone_path'] = path
    
    if show:
        print(json.dumps(configurations, indent=4)[1:-1])
        
    with open('config.json', 'w') as config_file:
        json.dump(configurations, config_file, indent=4)
        
def new_conf(name):
    from os.path import isdir
    from os import chdir, mkdir
    
    chdir('output')
    
    if isdir(name):
        print('The requested configuration already exists.\n' + 
              'If you want to reset it, please use the specific command.'
              + '\n  (that at the present moment does not exist)')
    else:
        mkdir(name)
        
def reset_conf(name, delete=False):
    from os.path import isdir
    from os import chdir, mkdir
    from shutil import rmtree
    from lib.utils import authorization_request
    
    chdir('output')
    
    if isdir(name):
        if delete:
            action = 'delete'
        else:
            action = 'reset'
        what_to_do = 'to ' + action + ' the configuration \'' + name + '\''
        authorized = authorization_request(what_to_do)
        if authorized:
            rmtree(name)
            if not delete:
                mkdir(name)
    else:
        print('The requested configuration does not exist.\n' + 
              'If you want to create it, please use the specific command.')
        
def clear_data(lambdas, config='test', force=False):
    """Remove data for a given value of lambda

    Parameters
    ----------
    Lambda : float
        the parameter of the simulation whose data you want to remove
    """
    from shutil import rmtree
    from lib.utils import find_all_availables, find_running, authorization_request
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
    
    lambdas_req_run = [x for x in lambdas if x in lambdas_run]
    lambdas_clearable = [x for x in lambdas if x not in lambdas_run]
    if len(lambdas_req_run) > 0:
        print("Simulations for following λ are running: ", 
              lambdas_req_run, '\n so they are not clearable')
    if len(lambdas_req_run) > 0 and len(lambdas_clearable) > 0:
        print()
    
    if len(lambdas_clearable) == 0:
        print("No λ found in the requested range.")
    
    for Lambda in lambdas_clearable:
        try:
            if not config == 'test' and not force:
                what_to_do = "to remove simulation folder"
                authorized = authorization_request(what_to_do, Lambda)
            else:
                authorized = True
            if authorized:
                rmtree("output/" + config + "/Lambda"+str(Lambda))
                if force:
                    print("(λ = " + str(Lambda) + ") ", end='')
                print("Simulation folder removed.")
        except FileNotFoundError:
            all_lambdas = find_all_availables()
            raise ValueError("A folder with the given lambda doesn't exist"+
                             "\n\t\t\t all_lambdas: " + str(all_lambdas))    

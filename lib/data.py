# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 10:54:46 2019

@author: alessandro
"""

def launch(lambdas_old, lambdas_new, config, linear_history, time, steps,
           force):
    """Output analysis for CDT_2D simulation.
    attempts_str = str(attempts)

    Descrizione...
    
    Parameters
    ----------
    p1 : tipo
        descrizione del primo parametro p1
    p2 : tipo
        descrizione del secondo parametro p2
    p3 : tipo, optional
        descrizione del terzo parametro opzionale p3
    
    Returns
    -------
    tipo
        descrizione del tipo di ritorno
        
    Raises
    ------
    Exception
        descrizione dell'eccezione lanciata
    """
    from os import mkdir, chdir, system, getcwd, scandir
    from shutil import copyfile
    from re import split
    from platform import node
    import json
    from subprocess import Popen
    from lib.utils import find_running
    from lib.utils import authorization_request
    
    lambdas_run, sim_info = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
    
    lambdas_old_auth = []
    lambdas_req_run = []
    for Lambda in lambdas_old:
        if Lambda not in lambdas_run:
            if not config == 'test' and not force:
                what_to_do = "to rerun simulation"
                authorized = authorization_request(what_to_do, Lambda)
            else:
                authorized = True
            if authorized:
                lambdas_old_auth += [Lambda]
        else:
            lambdas_req_run += [Lambda]
    
    lambdas = lambdas_old_auth + lambdas_new
    
    if len(lambdas_new) > 0:
        print("New simulations will be launched for following λ: ", 
              lambdas_new)
    if len(lambdas_old_auth) > 0:
        print("Old simulations will be rerunned for following λ: ", 
              lambdas_old_auth)
    if len(lambdas_req_run) > 0:
        print("Simulations for following λ were already running: ", 
              lambdas_req_run)
    if len(lambdas) > 0:
        print()
    
    project_folder = getcwd()
    
    for Lambda in lambdas:
        chdir(project_folder + '/output/' + config)
        
        dir_name = "Lambda" + str(Lambda)
        launch_script_name = 'launch_' + str(Lambda) + '.py'
        make_script_name = 'make_' + str(Lambda) + '.py'
        
        if Lambda in lambdas_old:
            with open(dir_name + "/state.json", "r+") as state_file:
                state = json.load(state_file)
                if state['is_thermalized']:
                    print('(λ = ' + str(Lambda) + ') Ha già finito idiota!')
                    # @todo da migliorare
                    continue
                
                if state['last_run_succesful']:
                    run_num = state['run_done'] + 1
                else:
                    print('(λ = ' + str(Lambda) + ') Problem in the last run')
                    continue
                
            checkpoints = [x.name for x in scandir(dir_name + "/checkpoint") \
                           if (split('_|\.|run', x.name)[1] == str(run_num - 1)
                           and x.name[-4:] != '.tmp')]
            # nell'ordinamento devo sostituire i '.' con le '~', o in generale
            # un carattere che venga dopo '_', altrimenti 'run1.1_...' viene 
            # prima di 'run1_...'
            checkpoints.sort(key=lambda s: s.replace('.','~'))
            last_check = checkpoints[-1]
        else:
            mkdir(dir_name)
            mkdir(dir_name + "/checkpoint")
            mkdir(dir_name + "/history")
            mkdir(dir_name + "/bin")
            
            copyfile('../../lib/launch_script.py', dir_name + '/' +
                     launch_script_name)
            copyfile('../../lib/make_script.py', dir_name + '/' + 
                     make_script_name)
            
            run_num = 1
            last_check = None
        
        # devo farlo qui perché prima non sono sicuro che dir_name esista
        # ('mkdir(dir_name)')
        chdir(dir_name)
        if run_num > 1:
            recovery_history()
        
        # ricongiungo le due variabili perché è ancora facile
        # distinguerle dall'ultimo carattere
        if steps != '0':
            end_condition = steps
        else:
            end_condition = time
        
        TimeLength = 80
        debug_flag = 'false'
        arguments = [run_num, Lambda, TimeLength, end_condition, debug_flag, 
                     last_check, linear_history]
        arg_str = ''
        for x in arguments:
            arg_str += ' ' + str(x)
        
        if(node() == 'Paperopoli'):
            make_script = Popen(["python3", make_script_name, str(run_num), 
                             str(Lambda)])
            make_script.wait()
            system('nohup python3 $PWD/' + launch_script_name + arg_str + ' &')
        elif(node() == 'fis-delia.unipi.it'):
            make_script = Popen(["python36", make_script_name, str(run_num), 
                             str(Lambda)])
            make_script.wait()
            system('nohup python36 $PWD/' + launch_script_name + arg_str + ' &')
        elif(node() == 'gridui3.pi.infn.it'):
            print('support for grid still missing')
#                make_script = Popen(["python3", make_script_name, str(run_num), 
#                                 str(Lambda)])
#                make_script.wait()
#                system('bsub -q local -o stdout.txt -e stderr.txt -J ' + \
#                       dir_name + ' $PWD/' + launch_script_name + arg_str)
        elif(node()[0:4] == 'r000'):
            print('support for marconi still missing')
        else:
            raise NameError('Node not recognized (known nodes in data.py)')

def show_state(configs, full_show=False):
    # @todo: add support for the other platforms
    # @todo: for clusters: add 'pending' state
    import pickle, json
    from os import environ, popen
    from platform import node
    from datetime import datetime
    from time import time
    from lib.utils import find_running
    
    if not type(configs) == list:
        configs = [configs]
    
    if node() == 'Paperopoli' or node() == 'fis-delia.unipi.it':
        ps_out = popen('ps -fu ' + environ['USER']).read().split('\n')
    else:
        ps_out = []
        print("This platform is still not supported")
    
    empty = len([1 for line in ps_out if 'CDT_2D-Lambda' in line]) == 0
    if len(ps_out) > 1 and not empty:
        print('   LAMBDA      TIME     STATUS     CONFIG', end='')
        if full_show == '0':
            print()
        elif full_show == '1':
            print('   RUN_ID   PID      PPID')
        elif full_show == '2':                    
            print('     LIN_HIST   START     DISK US.')
        
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
    else:
        print("There are no running simulations currently.")        
    
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
                print(str(Lambda).rjust(9), sim[0].rjust(11), ' ', 
                      state.ljust(10), l_conf.ljust(11), end='')
                if full_show == '0':
                    print()
                elif full_show == '1':
                    print(sim[1].rjust(4), ' ', sim[2].ljust(8),
                          sim[3].ljust(8))
                elif full_show == '2':
                    Lambda_dir = 'output/' + config + '/Lambda' + \
                                 str(Lambda) + '/'
                    with open(Lambda_dir + 'state.json', 'r') as state_file:
                        state = json.load(state_file)
                    lin_hist = state['linear-history']
                    start = state['start_time']
                    disk_us = popen('du -hs ' + Lambda_dir).read().split()[0]
                    print(str(lin_hist).ljust(9), start[-8:].ljust(10),
                          disk_us.rjust(8))
                        
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
        
def stop(lambdas_old, config, is_all):
    # @todo: distinguere fra processi 'data' e 'test'
    # si fa con un argomento config che viene da args.is_data
    import pickle
    from lib.utils import find_running
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
        
    try:
        with open('output/' + config + '/pstop.pickle','rb') as stop_file:
            lambdas_stopped = pickle.load(stop_file)
    except FileNotFoundError:
        lambdas_stopped = []
        
    l_aux = []
    for Lambda in lambdas_stopped:
        if Lambda in lambdas_run:
            l_aux += [Lambda]
    lambdas_stopped = l_aux
            
    lambdas_stopping = []
    lambdas_notstop = []
    for Lambda in lambdas_old:
        if Lambda in lambdas_run and not Lambda in lambdas_stopped:
            lambdas_stopped += [Lambda]
            lambdas_stopping += [Lambda]
            from os import system
            from time import time
            from datetime import datetime
            sf = '%d-%m-%Y %H:%M:%S'
            system('echo ' + datetime.fromtimestamp(time()).strftime(sf) +
                   ' > output/' + config + '/Lambda' + str(Lambda) + '/stop')
            # forse '.stop' anzichè 'stop'
        else:
            lambdas_notstop += [Lambda]
            
    with open('output/' + config + '/pstop.pickle','wb') as stop_file:
            pickle.dump(lambdas_stopped, stop_file)
            
    if len(lambdas_stopping) > 0:
        print("Simulations for following λ just stopped: ", lambdas_stopping)
    if len(lambdas_notstop) > 0 and not is_all:
        print("Simulations for following λ were not running: ",
              lambdas_notstop)

def show(lambdas_old, config, disk_usage=''):
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
    from textwrap import wrap
    from numpy import histogram, median
    from lib.utils import eng_not
    
    if len(lambdas_old) == 0:
        print("There are no folders currently.")
    else:
        print('┌' + '─' * (len(config) + 9) + '┐')
        print('│ ' + config.upper() + ' CONFIG │')
        print('╰' + '─' * (len(config) + 9) + '┘\n')
        num = str(len(lambdas_old))
        print("  " + num + " λ values in the range requested:")
        for x in wrap(str(lambdas_old), width=65, initial_indent=' '*3,
                      subsequent_indent=' '*4):
            print(x)
        
        if disk_usage == '':
            hist_lambda = histogram(lambdas_old,20)
            highest = max(hist_lambda[0])
            
            print()
            for h in range(0,highest):
                for x in hist_lambda[0]:
                    if(x >= highest - h):
                        print(' X ', end='')
                    else:
                        print('   ', end='')
                print("")
            
            l_min = eng_not(min(lambdas_old))
            l_med = eng_not(median(lambdas_old))
            l_max = eng_not(max(lambdas_old))
            print(l_min, ' '*23, l_med, ' '*23, l_max)
        
        elif disk_usage=='disk':
            from os import popen, chdir
            from lib.utils import color_mem, color_lambda
            
            chdir('output/' + config)
            
            x = popen('du -hd 1').read().split('\n')
            x[:-1].sort(key=lambda x: x.split()[0])
            y = popen('du -hd 2 */checkpoint').read().split('\n')
            y[:-1].sort(key=lambda x: x.split()[0])
            z = popen('du -hd 2 */bin').read().split('\n')
            z[:-1].sort(key=lambda x: x.split()[0])
            a = popen('du -hd 2 */history').read().split('\n')
            a[:-1].sort(key=lambda x: x.split()[0])
                
            dim = []
            for i in range(len(x)-2): 
                w = x[i].split('\t./Lambda')
                v = y[i].split()
                u = z[i].split()
                t = a[i].split()
                dim += [[w[1], w[0], v[0], u[0], t[0]]]
                
            print('\n', ' '*3, '┌', '─'*49, '╮', sep='')
            print(' '*3, '│ LAMBDA  │  SIZE  │  CHECK  │  BIN.  │  HISTORY  │',
                  sep='')
            print(' '*3, '╰', '─'*9, '┼', '─'*8, '┼', '─'*9, '┼', '─'*8,
                   '┼', '─'*11, '┘', sep='')
            for l in dim:
                b = color_mem(l[1].ljust(4), size=True)
                c = color_mem(l[2].ljust(4))
                d = color_mem(l[3].ljust(4))
                e = color_mem(l[4].ljust(4))
                a = color_lambda(l[0].rjust(11), [b, c, d, e])
                print(a, ' │ ', b, ' │  ', c, ' │ ', d, ' │  ', e)
            print()        
            print('The overall disk used is: ', x[-2].split()[0])
            
        elif disk_usage=='num':
            from os import popen, chdir
            from lib.utils import color_mem, color_num, color_lambda
            
            chdir('output/' + config)
            
            x = popen('du -hd 1').read().split('\n')
                
            dim = []
            for i in range(len(x)-2): 
                w = x[i].split('\t./Lambda')
                v = str(int(popen('ls -1q Lambda' + w[1] + 
                          '/checkpoint/ | wc -l').read()))
                u = str(int(popen('ls -1q Lambda' + w[1] +
                                  '/bin/ | wc -l').read()))
                dim += [[w[1], w[0], v, u]]
            dim.sort(key=lambda x : x[0])
                
            print('\n', ' '*3, '┌', '─'*37, '╮', sep='')
            print(' '*3, '│ LAMBDA  │  SIZE  │  CHECK  │  BIN.  │',
                  sep='')
            print(' '*3, '╰', '─'*9, '┼', '─'*8, '┼', '─'*9, '┼', '─'*8,
                  '┘', sep='')
            for l in dim:
                b = color_mem(l[1].ljust(4), size=True)
                c = color_num(l[2].rjust(4))
                d = color_num(l[3].rjust(4))
                a = color_lambda(l[0].rjust(11), [b, c, d])
                print(a, ' │ ', b, ' │ ', c, '  │ ', d)
            print()        

def plot(lambdas_old, config):
    from matplotlib.pyplot import figure, show
    from numpy import loadtxt
    from lib.utils import find_running
    
    lambdas_run, _ = find_running()
    lambdas_run = [x[0] for x in lambdas_run if x[1] == config]
    color_cycle = ['xkcd:carmine', 'xkcd:teal', 'xkcd:peach', 'xkcd:mustard',
                   'xkcd:cerulean']
    n_col = len(color_cycle)
    
    canvases = []
    props = []
    i = -1
    for Lambda in lambdas_old:
        i += 1
        vol_file = ('output/' + config + '/Lambda' + str(Lambda) +
                   '/history/volumes.txt')
        indices, volumes = loadtxt(vol_file, unpack=True)
        
        fig = figure()
        ax = fig.add_subplot(111)
        props += [{'fig':fig, 'ax':ax, 'skip':len(volumes),
                  'vol_file':vol_file}]
        canvases += [fig.canvas]
        
        fig.set_size_inches(7, 5)
        ax.plot(indices, volumes, color=color_cycle[i % n_col])
        if Lambda in lambdas_run:
            run_t = ', running'
        else:
            run_t = ''
        ax.set_title('λ = ' + str(Lambda) + run_t)
        
        def on_key(event):
            i = canvases.index(event.canvas)
            p = props[i]
            if event.key == 'f5':
                try:
                    ind_aux, vol_aux = loadtxt(p['vol_file'], unpack=True, 
                                               skiprows=p['skip'])
                except ValueError:
                    ind_aux = []
                    vol_aux = []
                    
                try:
                    if len(vol_aux) > 10:
                        props[i]['skip'] += len(vol_aux)
                        p['ax'].plot(ind_aux, vol_aux, 
                                color=color_cycle[i % n_col])
                        p['fig'].canvas.draw()
                except TypeError:
                    pass
    
        fig.canvas.mpl_connect('key_press_event', on_key)
        
    show()

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
            raise ValueError("A folder with the given lambda it doesn't exist"+
                             "\n\t\t\t all_lambdas: " + str(all_lambdas))    

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
    from lib.utils import authorization_request
    
    for Lambda in lambdas_old:
        if not config == 'test' and not force:
            what_to_do = "to set thermalization flag `" + str(is_therm) + "`"
            authorized = authorization_request(what_to_do, Lambda)
        else:
            authorized = True
        if authorized:
            filename = 'output/' + config + '/Lambda' + str(Lambda) + '/state.json'
            with open(filename, 'r') as state_file:
                state = json.load(state_file)
                state['is_thermalized'] = eval(is_therm)
                
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
        print("In what follows: \nuse numbers '> 0' to specify last run you " + 
              "want to remove, \n'< 0' to specify distance from last " + 
              "present.\n\nOnly λ with more than one run present are shown.\n")
        
    for l in lambdas_old:
        files = popen('ls -1 Lambda' + str(l) + '/' + what).read().split('\n')
        runs = []
        for x in files[:-1]:
            y = split('run|_', x)
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
              ' (default: -1)')
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
                ans = -1
            elif ans == 'q' or ans == 'quit':
                ans = 'q'
            else:
                try:
                    ans = int(ans)
                    if ans == 0 or abs(ans) >= max(runs):
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
            continue
        elif ans == 'q':
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
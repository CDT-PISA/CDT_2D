# -*- coding: utf-8 -*-

"""Suporto per varie piattaforme:
attualmente serve solo per gestire i vari lanci"""

# run scripts that will manage the simulation:
# make_script: compiles and returns
# launch_script: runs the sim and keeps running until the end

def local_launch(points, arg_strs):
    from os import system, chdir
    from os.path import abspath
    from subprocess import Popen
    from lib.utils import (point_dir, launch_script_name, make_script_name,
                           project_folder)

    dirs = {Point: abspath(point_dir(Point)) for Point in points}

    for Point in points:
        chdir(dirs[Point])

        arg_str = arg_strs[Point]
        run_num = int(arg_str.split()[1])

        launch_script_n = launch_script_name(Point)
        make_script_n = make_script_name(Point)

        make_script = Popen(["python3", make_script_n, str(run_num),
                             str(Point[0]), str(Point[1]), project_folder()])
        make_script.wait()
        system('nohup python3 $PWD/' + launch_script_n + arg_str + ' &')

def lsf_launch(points, arg_strs):
    raise NotImplementedError('missing implementation for lsf')
#            make_script = Popen(["python3", make_script_name, str(run_num),
#                             str(Lambda)])
#            make_script.wait()
#            system('bsub -q local -o stdout.txt -e stderr.txt -J ' + \
#                   dir_name + ' $PWD/' + launch_script_name + arg_str)

def slurm_launch(points, arg_strs, queue, arch, file):
    from os import system, chdir, chmod, makedirs
    from os.path import realpath, basename
    from subprocess import Popen
    from time import time
    from datetime import datetime
    from lib.utils import (point_dir, launch_script_name, make_script_name,
                           project_folder)

    # raise RuntimeError('support for marconi still missing')

    if queue in ['p', 'prod']:
        queue = 'prod'
        qtime = '23:59'
    elif queue in ['d', 'dbg', 'debug']:
        queue = 'dbg'
        qtime = '00:29'
    else:
        raise RuntimeError('slurm_launch: queue not recognized')

    if arch == 'skl':
        account = 'INF19_npqcd_0'
        c_sz = 48 # chunk_size
    elif arch == 'knl':
        account = 'IscrB_TOPPSI'
        c_sz = 68 # chunk_size
    else:
        raise RuntimeError('slurm_launch: arch not recognized')

    dirs = {Point: realpath(point_dir(Point)) for Point in points}

    points_chunks = [points[c_sz*i:c_sz*(i+1)]
                     for i in range(len(points)//c_sz + 1)]
    i = 0
    for chunk in points_chunks:
        i += 1
        def make_str(p):
            run_num = int(arg_strs[p].split()[1])
            make_args = str(run_num) + ' ' + str(p[0]) + ' ' + str(p[1]) + \
                        ' ' + project_folder()
            return make_script_name(p) + ' ' + make_args
        def launch_str(p):
            return launch_script_name(p) + arg_strs[p]

        points_makers = [make_str(p) for p in chunk]
        points_launchers = [launch_str(p) for p in chunk]

        points = ['(']
        for j in range(len(chunk)):
            points += ['"point_dir=\'' + point_dir(chunk[j]) + '\' ' +
                       # 'make=\'' + points_makers[j] + '\' ' +
                       'launch=\'' + points_launchers[j] + '\'"']

            chdir(dirs[chunk[j]])
            make_script = Popen(["python3", *points_makers[j].split()])
            make_script.wait()

        points += [')']
        points = '\n'.join(points)

        file_name = basename(file)
        sbatch_dir = file_name[:-4]

        time_ = datetime.fromtimestamp(time()).strftime('%d-%m-%Y_%H:%M:%S')
        jobname = f'CDT2D_{time_}--{i}'
        scripts_dir = project_folder() + '/lib/scripts'
        with open(scripts_dir + '/sbatch.sh', 'r') as sbatch_template:
            chunk_script = eval('f"""' + sbatch_template.read() + '"""')
            # if queue == 'dbg':
            if file[-3:] != '~~~':
                chunk_script += (f'\n\npython3 {project_folder()}/launcher.py '
                                 f'run --file {file}')

        file_name = basename(file)
        try:
            sbatch_dir = file_name[:-4]
            makedirs('../' + sbatch_dir)
            chdir('../' + sbatch_dir)
        except FileExistsError:
            pass

        sbatch_file = realpath(jobname + '.sh')
        with open(sbatch_file, 'w') as sbatch_script:
            sbatch_script.write(chunk_script)
        chmod(sbatch_file, 0o777)
        system('sbatch ' + sbatch_file)
        # system('./' + sbatch_file + ' &')

local_machines = ['Paperopoli', 'fis-delia.unipi.it']
lsf = ['gridui3.pi.infn.it']
slurm = []

def is_local():
    from platform import node
    if node() in local_machines:
        return True
    else:
        return False

def is_lsf():
    from platform import node
    if node() in lsf:
        return True
    else:
        return False

def is_slurm():
    from platform import node
    if node()[0:1] == 'r':
        return True
    else:
        return False

def launch_run(points, arg_strs, config, queue, arch, file):
    from os import chdir, listdir
    from lib.utils import config_dir
    chdir(config_dir(config))

    if is_local():
        # slurm_launch(points, arg_strs, queue, arch, file)
        local_launch(points, arg_strs)
    elif is_lsf():
        lsf_launch(points, arg_strs)
    elif is_slurm():
        slurm_launch(points, arg_strs, queue, arch, file)
    else:
        raise NameError('Platform not recognized '
                        '(known platforms in platform.py)')

def ps_local():
    from os import popen

    # return popen('ps -fu' + environ['USER']).read().split('\n')
    return popen('ps -fu $USER').read().split('\n')

def ps_lsf():
    raise NotImplementedError('missing implementation for lsf')

def ps_slurm():
    from os import popen

    return popen('squeue -u $USER --format="%.10i %.12P %.40j'
                 ' %.8u %.2t %.8M %.3D %R" | grep CDT | awk \'{print $1}\'| '
                 'xargs -I pid srun --jobid pid ps -fu $USER | '
                 'grep CDT').read().split('\n')

def get_ps_out():
    if is_local():
        # slurm_launch(points, arg_strs, queue)
        return ps_local()
    elif is_lsf():
        return ps_lsf()
    elif is_slurm():
        return ps_slurm()
    else:
        raise NameError('Platform not recognized '
                        '(known platforms in platform.py)')

# -*- coding: utf-8 -*-

"""Suporto per varie piattaforme:
attualmente serve solo per gestire i vari lanci"""

# run scripts that will manage the simulation:
# make_script: compiles and returns
# launch_script: runs the sim and keeps running until the end

def local_launch(points, arg_strs):
    from os import system
    from subprocess import Popen
    from lib.utils import point_str

    for Point in points:
        arg_str = arg_strs[Point]
        print(arg_str)
        run_num = int(arg_str[1])
        launch_script_name = 'launch_' + point_str(Point) + '.py'
        make_script_name = 'make_' + point_str(Point) + '.py'
        make_script = Popen(["python3", make_script_name, str(run_num),
                            str(Point[0]), str(Point[1])])
        make_script.wait()
        system('nohup python3 $PWD/' + launch_script_name + arg_str + ' &')

def slurm_launch():
    raise RuntimeError('support for marconi still missing')
    chdir(project_folder + '/output/' + config)
    points_chunks = [points[48*i:48*(i+1)]
                     for i in range(len(points)//48 + 1)]
    i = 0
    for chunk in points_chunks:
        i += 1
        launch_name = lambda p: 'launch_' + point_str(p) + '.py'
        points_launchers = [launch_name(p) + ' ' + arg_strs[p]
                            for p in chunk]
        time = datetime.fromtimestamp(time())\
                             .strftime('%d-%m-%Y_%H:%M:%S')
        jobname = f'CDT_2D_{i}_{time}'
        with open('../../lib/cdt2d_marco.sh', 'r') as sbatch:
            chunk_script = eval('f"' + sbatch + '"')

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
    if node()[0:4] == 'r000':
        return True
    else:
        return False

def launch_run(points, arg_strs):
    if is_local():
        local_launch(points, arg_strs)
    elif is_lsf():
        print('support for grid still missing')
        #            make_script = Popen(["python3", make_script_name, str(run_num),
        #                             str(Lambda)])
        #            make_script.wait()
        #            system('bsub -q local -o stdout.txt -e stderr.txt -J ' + \
        #                   dir_name + ' $PWD/' + launch_script_name + arg_str)
    elif is_slurm():
        slurm_launch(*args)
    else:
        raise NameError('Platform not recognized '
                        '(known platforms in platform.py)')

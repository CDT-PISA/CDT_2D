# -*- coding: utf-8 -*-

#Created on Sat Mar 30 11:08:57 2019
"""
Script that compiles the single simulations of CDT_2D, each values of lambda
has its own copy in its folder.

@author: alessandro
"""

from os import system, chdir, getcwd
from sys import argv
from shutil import move

def main():
    run_num = argv[1]
    Lambda_str = argv[2]

    lambda_folder = getcwd()
    cwd_list = lambda_folder.split('/')
    project_folder = ''
    for i in range(0, len(cwd_list)-3):
        project_folder += cwd_list[i] + '/'

    # is necessary to recompile each run because on the grid the node could be different
    
    exe_name = "CDT_2D-Lambda" + Lambda_str + "_run" + run_num

    chdir(project_folder + "build")
    system("make install")
    
    chdir(lambda_folder)
    #copyfile(project_folder + '../ciao/ciao','bin/ciao')
    #system('chmod 777 bin/ciao')
	
    print('-- Moving: CDT_2D/bin/cdt_2d --> CDT_2D/output/' +
          lambda_folder.split('/')[-2] + '/Lambda' + Lambda_str + '/bin/cdt_2d')
    move(project_folder + 'bin/cdt_2d', 'bin/' + exe_name)
    system('chmod 777 bin/' + exe_name)

if __name__ == "__main__":
    main()
    

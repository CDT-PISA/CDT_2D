# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 20:27:00 2019

@author: alessandro
"""

from os import system, chdir, getcwd
from sys import argv
from subprocess import Popen
from shutil import move
from datetime import datetime
from time import time

dir_name = argv[1]
run_num = argv[2]
Lambda_str = argv[3]
arguments = argv[2:]

lambda_folder = getcwd()
cwd_list = lambda_folder.split('/')
project_folder = ''
for i in range(0,len(cwd_list)-3):
    project_folder += cwd_list[i] + '/'


# is necessary to recompile each run because on the grid the node could be different
exe_name = "CDT_2D-Lambda" + Lambda_str + "_run" + run_num

chdir(project_folder + "build")
system("make -j4")
system("make -j4 install")

chdir(lambda_folder)
#copyfile(project_folder + '../ciao/ciao','bin/ciao')
#system('chmod 777 bin/ciao')

move(project_folder + 'bin/cdt_2d', 'bin/' + exe_name)
system('chmod 777 bin/' + exe_name)


log_file = open("runs_log.txt", "a")
log_file.write("#---------------- RUN " + str(run_num) + " ----------------#")
log_file.close()


out = open('stdout.txt', 'a')
err = open('stderr.txt', 'a')

#out_f = open('stdout.txt', 'w')
#sim = Popen(["bin/ciao"] + arguments)

# todo: pass runs_log.txt to the C++ so it can store the log:
# - each time that begins a checkpoint prints something like CHECKPOINT on the log
#   and when end it prints COMPLETED
# -
sim = Popen(["bin/" + exe_name] + arguments, stdout = out)
#sim = Popen(["bin/" + exe_name] + arguments, stdout = out, stderr = err)
sim.wait()

log_file = open("runs_log.txt", "a")
timestamp = datetime.fromtimestamp(time()).strftime('%d-%m-%Y %H:%M:%S')
log_file.write("\n" + timestamp + "\t run COMPLETED" )
log_file.write("\n#-------------- END RUN " + str(run_num) + " --------------#\n\n")
log_file.close()

out.close()
err.close()

print("ho finito il run " + run_num + "\n")

#import smtplib
#
#server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#   quando uno c'ha sbatta sarebbe carino trovare il modo di criptare la password
#server.login("cdt2d.email", "ciao_ciao")
#server.sendmail(
#  "cdt2d.email@gmail.com", 
#  "candido.ale@gmail.com", 
#  dir_name + " e' finito")
#server.quit()
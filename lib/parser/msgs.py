"""
Help messages for CDT_2D parser.
"""

from inspect import cleandoc

# GLOBAL

lamda = """λ value. It also accepts a list as input. If --range is available the
meaning of the list depend on its presence and value (default: it is interpreted
barely as a list)."""

beta = """β value. It also accepts a list as input. If --range is available the
meaning of the list depend on its presence and value (default: it is interpreted
barely as a list)."""

range = """it controls the meaning of parameters' lists. If the letter
corresponding is present in its argument the list is interpreted as range: a
list of 3 elements will be read as (start, stop, num), one with 2 elements
as (start, stop), and it will search for existing simulations in this
interval"""

config = """select the configuration for all simulations. Each simulation
belongs to a configuration even if it was not specified (the default one is
called 'test')"""

data = """data configuration flag (the '-' in front is not needed). It's a
shortcut for '--config data'."""

force = """force the command to do what is requested for, without asking for
confirmation, or making less controls"""

is_all = """all (the '-' in front is not needed). Select all the existing
simulations."""

# RUN

run_h = """launch single or multiple simulations"""

run = cleandoc("""
┌───────────┐
│RUN COMMAND│
└───────────┘
Used to launch CDT simulations:
    - λ is approximately the cosmological constant, and can be any real
      number
    - β is $ N/g_ym^2 $, and it must be strictly positive

If more than one λ or β are given the simulations who will be launched
correspond to the grid with those projections.

Example:
    cdt2d run -l -1. -b .5""")

timelength = """set timelength of the triangulation (it is meaningful only for
the first run, from the second on the same of the first is used)"""

fake_run = """if toggled prevents the simulation to start and instead prints
the command that would be run otherwise"""

linear_history = """it takes an integer argument, that if set greater then
zero let data points be saved at regular intervals, instead of at increasing
ones (units: {k,M,G}) | ex: --linear-history 2k"""

time = """if set it specifies the duration of the run (default: 30 minutes,
units: {s,m,h}) | ex: --time 2h"""

steps = """if set it specifies the length of the run in MC steps (is not the
default, units: | ex: --steps 200M"""

file = """launch simulation from config file: launch with '?' to show the help,
else give the relative path of a valid CDT_2D valid from your PWD"""

# STATE

state_h = """show the state of running simulations"""

state = cleandoc("""
┌─────────────┐
│STATE COMMAND│
└─────────────┘
Used to control the status of the running simulations.

Example:
    cdt2d state""")

full_show = """shows more infos about simulations. The value specifies which
supplement infos to show (default is 1)."""

# STOP

stop_h = """stops running simulations"""

stop = cleandoc("""
┌────────────┐
│STOP COMMAND│
└────────────┘
Used to stop a running simulations.

Example:
    cdt2d stop -l -1. -b .5
to stop all running simulations in the chosen config:
    cdt2d stop °""")

pid = """hard kill with PID"""

# PLOT

plot_h = """plots the volume history"""

plot = cleandoc("""
┌────────────┐
│PLOT COMMAND│
└────────────┘
Used to plot the volume history of a simulation.

Example:
    cdt2d plot -l -1. -b .5""")

# SHOW

show_h = """shows the existing simulations and basic infos"""

show = cleandoc("""
┌────────────┐
│SHOW COMMAND│
└────────────┘
...

Example:
    ...""")

disk_usage = """show disk usage"""

disk_number = """show number of files"""

# --------------
#     TOOLS
# --------------

tools = """further tools for simulations' management"""

# RECOVERY

recovery = cleandoc("""
┌────────────────┐
│RECOVERY COMMAND│
└────────────────┘
...

Example:
    ...""")

very_force = """very forced"""

# INFO

info = cleandoc("""
┌────────────┐
│INFO COMMAND│
└────────────┘
...

Example:
    ...""")

# THERM

therm = cleandoc("""
┌─────────────┐
│THERM COMMAND│
└─────────────┘
...

Example:
    ...""")

is_therm = """thermalization"""

# UPDATE LAUNCHER

up_launch = cleandoc("""
┌───────────────────────┐
│UPDATE LAUNCHER COMMAND│
└───────────────────────┘
...

Example:
    ...""")

make = """update make_script instead"""

both = """update both launch_script and make_script"""

# AUTOREMOVE

autoremove = cleandoc("""
┌──────────────────┐
│AUTOREMOVE COMMAND│
└──────────────────┘
...

Example:
    ...""")

bin = """remove older bins"""

check = """remove older checkpoints"""

# REMOTE

remote = cleandoc("""
┌──────────────┐
│REMOTE COMMAND│
└──────────────┘
...

Example:
    ...""")

upload = """update make_script instead"""

download = """update both launch_script and make_script"""

remote_show = """'show list of sims on remote'"""

# CONFIG

config_cmd = cleandoc("""
┌──────────────┐
│CONFIG COMMAND│
└──────────────┘
...

Example:
    ...""")

email = """set receiver email"""

rclone_remote = """set rclone remote"""

rclone_path = """set rclone path"""

node = """set node name"""

show_config = """show config file"""

# NEW_CONF

new_conf = cleandoc("""
┌────────────────┐
│NEW CONF COMMAND│
└────────────────┘
...

Example:
    ...""")

# RESET

reset = cleandoc("""
┌─────────────┐
│RESET COMMAND│
└─────────────┘
...

Example:
    ...""")

delete = """defintely delete config"""

# CLEAR

clear = cleandoc("""
┌─────────────┐
│CLEAR COMMAND│
└─────────────┘
...

Example:
    ...""")

# ----------------
#     ANALYSIS
# ----------------

analysis = """analysis tools"""

# FIT

fit = cleandoc("""
┌───────────┐
│FIT COMMAND│
└───────────┘
...

Example:
    ...""")

skip = """skip"""
"""
Help messages for CDT_2D parser.
"""

from inspect import cleandoc

# GLOBAL

lamda = """λ values"""

beta = """β values"""

range = """range"""

config = """config"""

data = """data configuration flag (the '-' in front is not needed)"""

force = """force"""

is_all = """all (the '-' in front is not needed)"""

# RUN

run = cleandoc("""
┌───────────┐
│RUN COMMAND│
└───────────┘
Used to launch CDT simulations:
    - λ is approximately the cosmological constant, and can be any real
      number
    - β is $ N/g_ym^2 $, and it must be strictly positive

Example:
    cdt2d run -l -1. -b .5""")

timelength = """set timelength"""

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

state = cleandoc("""
┌─────────────┐
│STATE COMMAND│
└─────────────┘
Used to control the status of the running simulations.

Example:
    cdt2d state""")

full_show = """full-show"""

# STOP

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

plot = cleandoc("""
┌────────────┐
│PLOT COMMAND│
└────────────┘
Used to plot the volume history of a simulation.

Example:
    cdt2d plot -l -1. -b .5""")

# SHOW

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

tools = """tools for simulation management"""

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

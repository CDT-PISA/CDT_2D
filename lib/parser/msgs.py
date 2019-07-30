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

config = """Select the configuration for all simulations. Each simulation
belongs to a configuration even if it was not specified (the default one is
called 'test').
To show all the available configs use the command 'cdt2d tools show-confs'"""

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

queue = """ only for marconi
"""

linear_history = """it takes an integer argument, that if set greater then
zero let data points be saved at regular intervals, instead of at increasing
ones (units: {k,M,G}) | ex: --linear-history 2k"""

time = """if set it specifies the duration of the run (default: 30 minutes,
units: {s,m,h}) | ex: --time 2h"""

steps = """if set it specifies the length of the run in MC steps (is not the
default, units: | ex: --steps 200M"""

file = """launch simulation from config file: launch with '?' to show the help,
else give the relative path of a valid CDT_2D valid from your PWD"""

adjacencies = """if set save periodically the infos about adjacencies in the
Triangulation, together with other local infos"""

maxvol = """set the maximum volume reachable for the running Triangulation; if
the volume is reached the simulation stops, and no further sub_run is submitted,
so that is like freezed and not runnable anymore (even if it doesn't prevent
further empty run)"""

moves_weights = """set the weights with which the moves are extracted;
only two are admissable: the third is set to complete the sum to 1"""

move22 = """half self-dual move rate (its half because of
            implementations' details, that provide two 22 moves)"""
move24 = """volume creation-destruction moves rate (it is the rate of each one
            not the rate of both together)"""
moveg = "gauge move rate (heatbath)"

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

path = "path"

# SHOW_CONFS

show_confs = cleandoc("""
┌──────────────────┐
│SHOW_CONFS COMMAND│
└──────────────────┘
...

Example:
    ...""")

show_paths = "show paths too"

# RESET

reset = cleandoc("""
┌─────────────┐
│RESET COMMAND│
└─────────────┘
...

Example:
    ...""")

# RM_CONF

rm_conf = cleandoc("""
┌───────────────┐
│RM CONF COMMAND│
└───────────────┘
...

Example:
    ...""")

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

#-------#
fits = """list of fits currently available"""
#-------#

# PRELIMINARY

ana_pre = cleandoc("""
┌───────────┐
│PRE COMMAND│
└───────────┘
...

Example:
    ...""")

conf_plot = """Used to plot more config with the same beta splitted.
"""

pre_kind = """Kind of plot.
"""

config_pattern = """Select the configuration for all simulations. Each simulation
belongs to a configuration even if it was not specified (the default one is
called 'test').
To show all the available configs use the command 'cdt2d tools show-confs.
Patterns are also available as regex, starting with '§'.
"""

save_path = """path to store data."""
load_path = """path to load data."""

# NEW_FIT

new_fit = cleandoc("""
┌───────────────┐
│NEW FIT COMMAND│
└───────────────┘
...

Example:
    ...""")

fit_path = "relative paths are allowed"

# SHOW_FITS

show_fits = cleandoc("""
┌─────────────────┐
│SHOW_FITS COMMAND│
└─────────────────┘
...

Example:
    ...""")

show_fit_paths = "show paths too"

# FIT RESET

reset_fit = cleandoc("""
┌─────────────────┐
│FIT RESET COMMAND│
└─────────────────┘
...

Example:
    ...""")

fit_names = """patterns available, they begin with '§'"""
delete_fit = """defintely delete fit"""

# RM_FIT

# rm_fit = cleandoc("""
# ┌──────────────┐
# │RM FIT COMMAND│
# └──────────────┘
# ...
#
# Example:
#     ...""")

# SET_FIT

set_fit = cleandoc("""
┌───────────────┐
│SET FIT COMMAND│
└───────────────┘
...

Example:
    ...""")

fit_remove = """Remove one or more sims from the selected fit."""

# INFO_FIT

info_fit = cleandoc("""
┌───────────────┐
│SET FIT COMMAND│
└───────────────┘
...

Example:
    ...""")

# SIM_OBS

sim_obs = cleandoc("""
┌───────────────┐
│SIM OBS COMMAND│
└───────────────┘
...

Example:
    ...""")

plot_obs = """Plot observables during setting."""
fit_obs = """Fit observables, such as corr. lengths."""
excl_tor = """Exlude torelons from observables calculation."""

# EXPORT_DATA

export_data = cleandoc("""
┌───────────────────┐
│EXPORT_DATA COMMAND│
└───────────────────┘
...

Example:
    ...""")

unpack = """unpack data exported in json to csv"""

# FIT

fit = cleandoc("""
┌───────────┐
│FIT COMMAND│
└───────────┘
...

Example:
    ...""")

skip = """skip"""
reload_data = """reload [T/F]"""
fit_kinds = """kinds"""

# CDT_2D
My own implementation of CDT in 1+1 dimension

## TODO

- ~~Write the moves~~
- Insert save methods for simulation results (volume, spatial_profile, ...)
- Write python script for graphical elaboration
    - and maybe a bash script to coordinate python and simulation

### Python
In the Python script would be nice if the following things were done:

- explores the directory "output/" and finds the last one in sequential (maybe they will be called "output/results1","output/results2",... or "output/out1",... or "output/run1",... or something else)
- creates a new directory for the current simulation
- launch the simulation with a parameter for the path (and maybe the cosmological constant lambda, so that all the interactions are through Python, and there will be no need to touch again the C++ code once it works)
- loads the data produced by the simulation
- creates the plots

would be interesting if the last two step could be done simultaneously with the simulation (for long runs)

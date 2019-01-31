# CDT_2D
My own implementation of CDT in 1+1 dimension

## TODO

- ~~Write the moves~~
- ~~Write python script for graphical elaboration~~
    - ~~and maybe include in the script simulation launching and results collecting~~
- New observables
    - Insert save methods for simulation results
- Simulation stop

### Simulation
This is the real missing thing: DEBUG

**Devo stampare sulle mosse le informazioni relative a ogni elemento in modo da poter cercare successivamente in stdout.txt le mosse in cui è stato coinvolto (magari stampando "t184" per i triangoli e "v76" per i vertici, in modo da poterli distinguere nell'output)**

### Python
The only things really remain to do is:

- find new observables for new plots
- manage condition for simulation stop

and one more:
- for long run and/or long TimeLength is very difficult and meaningless for the python script to draw all points on the plot, so I have to set two cutoffs (one for TimeLength and one for attempts) above which I coarse-grain the information before plotting

the rest is:

- find meaningful names for objects in the script
- find meaningful name for THE script
- write docs and docstrings

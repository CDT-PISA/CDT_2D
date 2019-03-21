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

**utils.h:** funzione per decifrare i bool (così posso vedere anche il bool `test`)

Se non sono in `test` argomenti sul file con cui leggere se è termalizzato (interazioni col Python)

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


kjkigugbj:
- aggiungere state & stop
- aggiungere a find_lambdas la possibilità di specificare tuple lunghe 3: (start,stop,step)
- aggiungere gestione delle misure esistenti, in corso, nuove:	
	- quando chiedi di lanciarle ti prompta indietro lo specchietto e ti chiede conferma
	- specificando che ovviamente quelle in corso non le tocca
- aggiungere lancio di processi su grid (e magari anche la configurazione sul mio computer: se rileva il mio pc è comunque in grado di lanciarlo)
- aggiungere cazzi con log2 16,2^14,... nel codice C++

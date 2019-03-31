# CDT_2D
My own implementation of CDT in 1+1 dimension

## TODO:

- Aggiustare `~` con il path alla home su `grid`
- Aggiustare `modules` su `marconi` con Giuseppe

#### Simulazione

- **MEMORY LEAKS**
- sistemare gli intervalli di salvataggio a un tempo sensato (`1m`?)

*DEBUG: Devo stampare sulle mosse le informazioni relative a ogni elemento in modo da poter cercare successivamente in stdout.txt le mosse in cui è stato coinvolto (magari stampando "t184" per i triangoli e "v76" per i vertici, in modo da poterli distinguere nell'output)*

DEBUG: devo sostituire la flag di debug con le direttive del preprocessor
(e capire come settare debug mode a livello del comando `gcc`)

#### Script

- **documentazione**
	- magari scrivo anche un README decente, con una sezione sviluppo, ma anche una descrizione vera
		- (e magari sposto i commenti e TODO in un altro file, così in README rimangono solo la descrizione e la descrizione degli sviluppi futuri)
		- magari faccio un file vX.md per ogni major version X che intendo fare (v1.md, v2.md, v3.md)
	- oltre a documentare il C++ (doxygen) e Python (docstring) sarebbe utile scrivere subito una guida al contenuto del project folder e a tutta l'alberatura, quindi strutturata a ipertesto:
		- guida al progetto
			- --> guida alla simulazione (C++)
			- --> guida all'interfaccia (Python)
- gestione misure esistenti
	- se con un checkpoint arriva fino a un certa iterazione le misure prima sono da buttare, o almeno da buttare prima del prossimo run
	- salvare sul json il numero di iterazione e manipolare i file delle misure subito prima di lanciare un nuovo run
- gestione run *falliti*
- aggiungere state & **stop**
	- il problema non è fare kill (cerca il PID dei processi e lancia la kill) ma fare in modo che C++ la gestisca in modo sensato, e non muoia male
		- controllare come fa Giuseppe a chiudere bene una simulazione
		- quando parte la kill inserisce in una lista (salvata e caricata da un oggetto)
		- ogni volta che viene chiamato state o stop controlla se sono morti, se sì vengono eliminati dalla lista
- aggiungere i plot, almeno uno stupido
	- opzione `-p/--plot` con un suo subparser
	- prende come argomenti `volumes` o `profiles`
	- implementare intanto `volumes`
	- in seguito anche `profiles`
- **TERMALIZZAZIONE**  
	progetto (per il momento lo realizzo semplice, così almeno lo posso lanciare subito automatico):
	- :smile:

*Le modifiche elencate fin qui devono essere presenti **prima di** rilasciare la **versione 1.0**.*
Quelle dopo possono anche aspettare, perché non danno problemi di compatibilità con l'output dei run, ma sono solo migliorie alla simulazione/script, che possono proseguire i risultati ottenuti fino a quel momento.

### New features
Raccolta di feature nuove non strettamente necessarie:

In realtà queste possono essere implementate dopo la v1.0, ma è necessario farle:

- gestire i plot (cioè ripensare `analysis.py`) alla luce dei salvataggi logaritmici
- nomi sensati per gli oggetti negli script

queste quelle davvero opzionali:

- pensare a cosa farsene dell'output (`nohup.out`)
- aggiungere funzione per vedere il numero di **binari** in ogni cartella
	- in modo da cancellarli a mano
		- la funzione fa una lista in verticale dei Lambda, e stampa accanto a ognuno tante x quanti i binari
		- poiché le Lambda hanno lunghezza variabile devono essere allineate a destra con la più lunga (nessun troncamento)
		- magari ogni 5 X stampo una V per contare meglio
	- inserire un limite automatico oltre il quale cancella da solo quelli più vecchi (tipo 10, all'undicesimo cancella il più vecchio)
- stesso di cui sopra per i **checkpoint**
- aggiungere un generatore in scope globale così da poterlo inizializzare con un certo **seed**
- `argomplete` e gli alias
	- [make-completion-wrapper.sh](https://ubuntuforums.org/showthread.php?t=733397)
	- [Issue sul progetto](https://github.com/kislyuk/argcomplete/issues/222)
- aggungere warning nell'autocomplete per comandi assurdi (esempio: `-s` con `--linear-history`)
- aggiungere gestione delle misure esistenti, in corso, nuove:	
	- quando chiedi di lanciarle ti prompta indietro lo specchietto e ti chiede conferma
	- specificando che ovviamente quelle in corso non le tocca
- aggiungere richiesta di conferma per eliminare cartelle
	- prima stampa tutti i lambda e poi ti chiede: sei davvero sicuro?
	- aggiungere opzione `-f` per evitare interazione (magari che funzioni genericamente per ogni comando, esempio: anche quando --data dovrebbe chiederti come agire per i processi attivi o comunque promptarti con `-f` evita)
- aggiungere checkpoint da cui si parte su `state.json`
- exit_condition: iterazioni o tempo
		---> c'è da mettere anche un limite gigante in volume
				per evitare che quelle che divergono esplodano, così
				posso liberamente imporre anche limiti di tempo non
				piccoli e uguali per tutti

### Done

~~ALIAS SU GRID: `cdt2d='python3 ~\projects\CDT_2D\launcher.py`~~

- ~~trovare un nome sensato per il launcher~~
- ~~far funzionare `argcomplete`~~
- ~~aggiungere a find_lambdas la possibilità di specificare tuple lunghe 3: (start,stop,step)~~
- ~~aggiungere lancio di processi su grid (e magari anche la configurazione sul mio computer: se rileva il mio pc è comunque in grado di lanciarlo)~~
- ~~aggiungere cazzi con log2 16,2^14,... nel codice C++~~
- ~~supporto grid~~
- ~~data: $ per prendere dati~~
		---> la configurazione test dev'essere uguale a quella dati
				magari si aggiorna più liberamente, per cui ha senso
				che rimangano due file differenti
- ~~subparser (*implementato in altro modo*) per `-d`~~:
	- ~~modificare `cdt2d -d/--data` in `cdt2d -r/--run` o `cdt2d -l/--launch`?~~
	- ~~aggiungere `--linear-history` come flag nel subparser (e `--log-history`, che in realtà è il default)~~
		- ~~anziché avanzare logaritmicamente lo step di salvataggio salva a intervalli regolari~~
			- ~~utile per prendere dati su una configurazione già termalizzata~~
		- ~~implementare anche nel C++~~
		- ~~aggiungere `--step-size`, ogni quanti step salvare (*implementato in altro modo*)~~
	- ~~aggiungere `--time` e `--steps` (i limiti sulla lunghezza del run)~~
		- ~~ci metto un default sensato così non allungo necessariamente i comandi~~
		 ~~ altrimenti è in unità di 1~~

## Versions
Non appena il bug sui salvataggi è risolto diventerà utilizzabile e sarà la versione 0.1, ma finché non saranno pronte tutte le feature davvero utili alla presa dati non verrà rilasciata la prima versione.
Quando sarà pronta e 'bella' per prendere dati rilascerò la versione 1.0, nel frattempo sviluppo anche le seguenti.

Quando comincerò a sviluppare le cose seguenti lo farò in dei nuovi `branch`, quando saranno pronti verranno reinseriti in `master` come 2.0 e 3.0.

Ogni nuova versione viene rilasciata con un `tag`, e sarebbe bello che per ogni tag fosse anche pronta la documentazione.

### Termalizzazione

### Campi di materia

Una volta che ci sarà un nuovo parametro da esplorare ($g_{YM}$) si può imporre un volume fissato, rinunciando a $\lambda$.

**COPIARE QUELLO CHE SI E' DETTO CON GIUSEPPE E D'ELIA E FINIRE DI CONTROLLARE COME IMPLEMENTARE BILANCIO DETTAGLIATO**


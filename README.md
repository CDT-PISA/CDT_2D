# CDT_2D
My own implementation of CDT in 1+1 dimension

## TODO:

**ALIAS SU GRID: `cdt2d='python3 ~\projects\CDT_2D\launcher.py`**

#### Simulazione
This is the real missing thing: DEBUG

**Devo stampare sulle mosse le informazioni relative a ogni elemento in modo da poter cercare successivamente in stdout.txt le mosse in cui è stato coinvolto (magari stampando "t184" per i triangoli e "v76" per i vertici, in modo da poterli distinguere nell'output)**

**utils.h:** funzione per decifrare i bool (così posso vedere anche il bool `test`)

Se non sono in `test` argomenti sul file con cui leggere se è termalizzato (interazioni col Python)

#### Script

- **documentazione**
	- magari scrivo anche un README decente, con una sezione sviluppo, ma anche una descrizione vera
		(e magari sposto i commenti e TODO in un altro file, così in README rimangono solo la descrizione e la descrizione degli sviluppi futuri)
- nomi sensati per gli oggetti negli script
- gestione misure esistenti
- gestione run falliti
- gestire i plot (cioè ripensare `analysis.py`) alla luce dei salvataggi logaritmici

*Le modifiche elencate fin qui devono essere presenti **prima di** rilasciare la **versione 1.0**.*
Quelle dopo possono anche aspettare, perché non danno problemi di compatibilità con l'output dei run, ma sono solo migliorie alla simulazione/script, che possono proseguire i risultati ottenuti fino a quel momento.

### New features
Raccolta di feature nuove non strettamente necessarie:


- aggiungere state & stop
- aggiungere gestione delle misure esistenti, in corso, nuove:	
	- quando chiedi di lanciarle ti prompta indietro lo specchietto e ti chiede conferma
	- specificando che ovviamente quelle in corso non le tocca
- aggiungere richiesta di conferma per eliminare cartelle
	- prima stampa tutti i lambda e poi ti chiede: sei davvero sicuro?
	- aggiungere opzione `-f` per evitare interazione (magari che funzioni genericamente per ogni comando, esempio: anche quando --data dovrebbe chiederti come agire per i processi attivi o comunque promptarti con `-f` evita)
- aggiungere checkpoint da cui si parte su `state.json`
- modificare `cdt2d -d/--data` in `cdt2d -r/--run` o `cdt2d -l/--launch`?
- exit_condition: iterazioni o tempo
		---> c'è da mettere anche un limite gigante in volume
				per evitare che quelle che divergono esplodano, così
				posso liberamente imporre anche limiti di tempo non
				piccoli e uguali per tutti

### Done

- ~~find meaningful name for THE script~~
- ~~aggiungere a find_lambdas la possibilità di specificare tuple lunghe 3: (start,stop,step)~~
- ~~aggiungere lancio di processi su grid (e magari anche la configurazione sul mio computer: se rileva il mio pc è comunque in grado di lanciarlo)~~
- ~~aggiungere cazzi con log2 16,2^14,... nel codice C++~~
- ~~supporto grid~~
- ~~data: $ per prendere dati~~
		---> la configurazione test dev'essere uguale a quella dati
				magari si aggiorna più liberamente, per cui ha senso
				che rimangano due file differenti

## Versions
Non appena il bug sui salvataggi è risolto diventerà utilizzabile e sarà la versione 0.1, ma finché non saranno pronte tutte le feature davvero utili alla presa dati non verrà rilasciata la prima versione.
Quando sarà pronta e 'bella' per prendere dati rilascerò la versione 1.0, nel frattempo sviluppo anche le seguenti.

Quando comincerò a sviluppare le cose seguenti lo farò in dei nuovi `branch`, quando saranno pronti verranno reinseriti in `master` come 2.0 e 3.0.

Ogni nuova versione viene rilasciata con un `tag`, e sarebbe bello che per ogni tag fosse anche pronta la documentazione.

### Termalizzazione

### Campi di materia


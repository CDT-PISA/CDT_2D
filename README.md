# CDT_2D
My own implementation of CDT in 1+1 dimension

## TODO:

- Aggiustare `~` con il path alla home su `grid`
- Aggiustare `modules` su `marconi` con Giuseppe

#### Simulazione

- **MEMORY LEAKS**
- aggiungere un generatore in scope globale così da poterlo inizializzare con un certo **seed**
- riferimenti circolari di `shared_ptr`
	- testare se sono un problema
	- ~~mettere a `nullptr` prima di rimuovere~~
	- testare con i `nullptr` sul long run

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
- scrivere la funzione di termalizzazione
	- prima finire i test sul funzionamento del resto

*Le modifiche elencate fin qui devono essere presenti **prima di** rilasciare la **versione 1.0**.*
Quelle dopo possono anche aspettare, perché non danno problemi di compatibilità con l'output dei run, ma sono solo migliorie alla simulazione/script, che possono proseguire i risultati ottenuti fino a quel momento.

### New features
Raccolta di feature nuove non strettamente necessarie:

In realtà queste possono essere implementate dopo la v1.0, ma è necessario farle:

- nomi sensati per gli oggetti negli script

queste quelle davvero opzionali:

- *richieste e prompt per qualunque cosa*
- aggiungere gestione delle misure esistenti, in corso e nuove:
	- quando chiedi di lanciarle ti prompta indietro lo specchietto e ti chiede conferma
		- per ora sono gestite in modo sensato ma è tutto silenziato
		- la cosa importante da aggiungere sarebbe il feedback all'utente
	- specificando che ovviamente quelle in corso non le tocca
- aggiungere richiesta di conferma per eliminare cartelle
	- prima stampa tutti i lambda e poi ti chiede: sei davvero sicuro?
	- aggiungere opzione `-f` per evitare interazione (magari che funzioni genericamente per ogni comando, esempio: anche quando --data dovrebbe chiederti come agire per i processi attivi o comunque promptarti, con `-f` evita)

- comando per ricaricare i launch_script
	- forse inserirlo sotto `run`, forse indipendente, e forse entrambi
- aggiungere funzione per vedere il numero di **binari** in ogni cartella
	- in modo da cancellarli a mano
		- la funzione fa una lista in verticale dei Lambda, e stampa accanto a ognuno tante x quanti i binari
		- poiché le Lambda hanno lunghezza variabile devono essere allineate a destra con la più lunga (nessun troncamento)
		- magari ogni 5 X stampo una V per contare meglio
	- inserire un limite automatico oltre il quale cancella da solo quelli più vecchi (tipo 10, all'undicesimo cancella il più vecchio)
- stesso di cui sopra per i **checkpoint**
- visualizzazione della **dimensione delle cartelle**

- reset di log step
	- inserire un comando che di default resetti a un valore non enorme, ma nemmeno quello iniziale
	- inserire l'opzione per specificare il valore a cui resettare (come esponente di una potenza di 2)
- localizzare gli import che servono in uno o pochi casi in modo da non importare quando non serve
- aggiungere in setup.sh il supporto per modificare la 'home/project/CDT_2D/' in '$PWD'
- pensare a cosa farsene dell'output (`nohup.out`)

- ragionare se ha senso salvare info più frequentemente, tipo ad ogni sottorun (pezzi di json ad esempio)
- migliorare `--plot`
	- prende come argomenti `volumes` o `profiles`
	- implementare `profiles`
	- aggiungere l'opzione `-color` (quando sarà disponibili il subparser)
		- specificando `choices`
	- gestire i plot (cioè ripensare `analysis.py`) alla luce dei salvataggi logaritmici
- `argomplete` e gli alias
	- [make-completion-wrapper.sh](https://ubuntuforums.org/showthread.php?t=733397)
	- [Issue sul progetto](https://github.com/kislyuk/argcomplete/issues/222)
	- usare per migliorare `--clear` e `--stop`: suggerisce i Lambda delle simulazioni opportune
- aggungere warning nell'autocomplete per comandi assurdi (esempio: `-s` con `--linear-history`)

### Done

~~ALIAS SU GRID: `cdt2d='python3 ~\projects\CDT_2D\launcher.py`~~

- ~~trovare un nome sensato per il launcher~~
- ~~far funzionare `argcomplete`~~
- ~~aggiungere a find_lambdas la possibilità di specificare tuple lunghe 3: (start,stop,step)~~
- ~~aggiungere lancio di processi su grid (e magari anche la configurazione sul mio computer: se rileva il mio pc è comunque in grado di lanciarlo)~~
- ~~aggiungere cazzi con log2 16,2^14,... nel codice C++~~
- ~~supporto grid~~
- ~~aggiungere state~~
- ~~migliorare `--state` (vedi `launcher.py`)~~
	- ~~opzione nel subparser (quando ne avrà uno): mostra il PID del processo per consentire l'hard kill~~
	- ~~aggiungere `full-show` per `--state` (sotto il subparser)~~
- ~~migliorare `state.json`~~
	- ~~aggiungere checkpoint da cui si parte~~
	- ~~aggiungere numero di iterazioni?~~
- ~~risolvere il problema di `state` su ssh (che poi è un problema anche per `run` e `stop`)~~
- ~~data: $ per prendere dati~~
		---> la configurazione test dev'essere uguale a quella dati
				magari si aggiorna più liberamente, per cui ha senso
				che rimangano due file differenti
- ~~aggiungere **stop**~~
	- ~~quando parte la kill inserisce in una lista (salvata e caricata da un oggetto, pickle)~~
	- ~~ogni volta che viene chiamato state o stop controlla se sono morti, se sì vengono eliminati dalla lista~~
	- ~~aggiungere supporto nella simulazione~~
		- ~~cerca ogni tot iterazioni se esiste 'stop' e nella sua cartella e se sì esce dal while e chiude normalmente~~
- ~~assicurarsi che un processo quando viene stoppato si rimuova dalla lista di quelli stoppati prima di finire~~
	- ~~altrimenti al run successivo non sarà più killabile~~
- ~~migliorare `--stop`~~
	- ~~aggiungere supporto per le altre piattaforme (**controllare se funziona su Pierino**)~~
	- ~~decidere se ha senso fare i check ogni tot iterazioni (attualmente 2e5) oppure ogni tot tempo (forse meglio) *irrilevante*~~
- ~~comando `--info` che stampi le informazioni relative a un Lambda, tipo quelle contenute nel json~~
- ~~aggiungere i plot, almeno uno stupido~~
	- ~~opzione `-p/--plot`~~
	- ~~implementare intanto `volumes`~~
	- ~~plot interattivi~~
- ~~gestione run *falliti*~~
	- ~~se la simulazione C++ fallisce, in fondo a launch_script:~~
		- ~~sceglie qual'è l'ultimo checkpoint utile~~
		- ~~cancella i successivi~~
		- ~~cancella i dati successivi~~
	- ~~se fallisce tutto il processo:~~
		- ~~implementare la funzione `recovery`, che fa quello che dovrebbe essere fatto in fondo a launch_script~~
- ~~subparser (*implementato in altro modo* --> *... e invece no*) per `-d`~~:
	- ~~modificare `cdt2d -d/--data` in `cdt2d -r/--run` o `cdt2d -l/--launch`?~~
	- ~~aggiungere `--linear-history` come flag nel subparser (e `--log-history`, che in realtà è il default)~~
		- ~~anziché avanzare logaritmicamente lo step di salvataggio salva a intervalli regolari~~
			- ~~utile per prendere dati su una configurazione già termalizzata~~
		- ~~implementare anche nel C++~~
		- ~~aggiungere `--step-size`, ogni quanti step salvare (*implementato in altro modo*)~~
	- ~~aggiungere `--time` e `--steps` (i limiti sulla lunghezza del run)~~
		- ~~ci metto un default sensato così non allungo necessariamente i comandi~~
		 ~~ altrimenti è in unità di 1~~
- ~~riimplementare i comandi principali come subparser (a costo di moltiplicare per ogni subparser le opzioni come `°`, `@` e `--range`)~~
	- ~~a questo punto `--run` diventerà `run`, quindi `--range` può riacquisire il `-r`~~
- ~~aggiungere le opzioni `config`~~
	- ~~attualmente tutte le nuove funzioni sono implementate solo in `test`~~
	- ~~rimpiazzare `data.py`~~
- ~~exit_condition: iterazioni o tempo~~
		---> ~~c'è da mettere anche un limite gigante in volume~~
				~~per evitare che quelle che divergono esplodano, così~~
				~~posso liberamente imporre anche limiti di tempo non~~
				~~piccoli e uguali per tutti~~
- ~~TERMALIZZAZIONE~~  
	~~progetto (per il momento lo realizzo semplice, così almeno lo posso lanciare subito automatico):~~
	- :smile:
	- ~~launch_script intercetta `end-condition` e divide in blocchi la simulazione (se `time` magari blocchi da 15-30m, se `steps` blocchi corrispondenti in unità di step)~~
		- ~~i blocchi potrebbero anche essere proporzionali alla complessiva (quindi un numero fisso di blocchi)~~
	- ~~controlla se è termalizzato, se lo è conclude il run, altrimenti rilancia la simulazione~~
- ~~comando per settare a mano se un processo è già termalizzato~~
	- ~~così non devo aprire a mano il json e sono sicuro che sia modificato correttamente~~
- ~~se `--linear-history` è settato non ridistribuisce la `end_condition` su `end_partial`~~
	- ~~così quando è termalizzato fa tutto il run nel primo `Popen` e salta il loop `while`~~
	- ~~se termalizzato già al run precedente setta `--linear-history` (o equivalente) di default~~
		- ~~lo fa subito all'inizio di `launch_script`~~
	- ~~salvare l'informazione su quali run vengono fatti con `--linear-history` e da che iterazione parte ogni run~~

## Versions
Non appena il bug sui salvataggi è risolto diventerà utilizzabile e sarà la versione 0.1, ma finché non saranno pronte tutte le feature davvero utili alla presa dati non verrà rilasciata la prima versione.
Quando sarà pronta e 'bella' per prendere dati rilascerò la versione 1.0, nel frattempo sviluppo anche le seguenti.

Quando comincerò a sviluppare le cose seguenti lo farò in dei nuovi `branch`, quando saranno pronti verranno reinseriti in `master` come 2.0 e 3.0.

Ogni nuova versione viene rilasciata con un `tag`, e sarebbe bello che per ogni tag fosse anche pronta la documentazione.

### Termalizzazione

### Campi di materia

Una volta che ci sarà un nuovo parametro da esplorare ($g_{YM}$) si può imporre un volume fissato, rinunciando a $\lambda$.

**COPIARE QUELLO CHE SI E' DETTO CON GIUSEPPE E D'ELIA E FINIRE DI CONTROLLARE COME IMPLEMENTARE BILANCIO DETTAGLIATO**


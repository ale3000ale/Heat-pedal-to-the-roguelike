# Draft e preparazione della gara

Data: 2026-10-25. Specifica ricavata dalle richieste e conferme dell'autore nella conversazione. Ramo di lavoro: draft. Stato: requisiti concordati; implementazione e verifiche non ancora eseguite. Questa specifica aggiorna le regole precedenti solo per il flusso qui descritto.

## Metodo

Lavorare soltanto su Heat-pedal-to-the-roguelike e sul ramo draft, senza creare altri rami. Leggere i file prima di modificarli. Aggiornare la documentazione all'inizio e alla fine della modifica, non negli incrementi intermedi. Aprire una PR di lavoro per la CI; non attendere la CI dei commit esclusivamente documentali. Affidare alla CI test backend, migrazioni e controlli frontend; non dichiarare esiti prima di averli letti. Nessun merge implicito. Nessuna modifica al database reale senza autorizzazione e backup.

## Apertura e annullamento

Nuova gara apre una procedura modale prima di creare la gara. La chiusura volontaria avviene esclusivamente con X in alto a sinistra, disponibile al creatore, con conferma testuale: annullare la gara? Esc e clic esterno non chiudono. Confermare annulla l'intera procedura e non crea alcuna gara. Ripristinare pool, inventari e mazzi da gioco allo stato precedente alla procedura, anche se alcune carte erano gia state scelte o i mazzi modificati.

Il modal iniziale offre draft e Gara già disputata. Il secondo chiude il modal e crea direttamente una gara normale, senza draft, preparazione READY o controllo preliminare dei mazzi; i risultati vengono inseriti successivamente.

## Presenti e assenti

Elencare i piloti iscritti al campionato in Presenti, ciascuno con Escludi. Escludi sposta il pilota in Assenti in fondo, con Includi per riportarlo tra i presenti. Avanti in basso a destra porta alla fase successiva. La partecipazione e il conteggio N riguardano i piloti presenti, non gli account. Uno stesso account puo avere piu piloti presenti.

## Ordine

Con pool sufficiente, mostrare i presenti nell'ordine inverso di arrivo della gara precedente. Chi non ha un risultato nella gara precedente viene aggiunto in fondo in ordine casuale. Senza gara precedente, disporre tutti casualmente e mostrare Prima gara in grassetto, in alto al centro. Il creatore puo riordinare trascinando i nomi. Avanti avvia la scelta delle carte e allarga il modal.

## Pool insufficiente

Servono N+3 copie nella pool modifiche del campionato. Se non bastano, mantenere la selezione Presenti/Assenti e poi passare direttamente alla modifica dei mazzi, saltando ordine e scelta carte. Non creare subito la gara.

## Scelta delle carte

Estrarre N+3 copie dalla pool modifiche del campionato; sono ammesse piu copie della stessa carta. Ogni pilota presente sceglie una sola copia, nell'ordine confermato. Le tre copie non scelte tornano nella pool.

All'avvio della scelta aprire automaticamente il modal grande agli utenti proprietari dei piloti presenti, da qualunque pagina dell'app; il creatore lo ha gia aperto. I partecipanti non possono chiuderlo. Persistenza e recupero devono consentire a chi si riconnette o ricarica la pagina di ritrovare fase e turno correnti.

Per il proprietario del pilota di turno il modal ha sfondo verde e scritta lampeggiante tocca a te. Gli altri vedono sfondo rosso e Tocca a NOME DEL PILOTA CHE DEVE SCEGLIERE.

Chiunque puo ingrandire una carta premendola e riportarla alle dimensioni normali ripremendola. Solo durante il proprio turno, ingrandire una carta mostra agli altri un alone giallo sotto quella copia e il nome del pilota; al proprietario compare scegli. Scegli richiede conferma, rimuove la copia dalle carte disponibili e la aggiunge all'inventario modifiche del pilota. Le copie scelte compaiono nella sezione carte scelte con il nome del pilota.

Dopo l'ultima scelta non creare ancora la gara: passare alla preparazione dei mazzi.

## Preparazione mazzi e READY

Aprire la modifica del mazzo per i piloti presenti. Il controllo preliminare dei mazzi riguarda soltanto i presenti e non viene eseguito alla prima gara. Dalla seconda gara il pulsante pronto richiede esattamente 15 carte nel mazzo; alla prima gara non impone questa condizione. Gli altri vincoli del mazzo restano validi.

La disponibilita e per pilota. Un utente con piu piloti presenti puo passare tra i propri piloti e confermarli singolarmente. La schermata READY completamente bloccata compare quando ha confermato tutti i propri piloti presenti.

Nello stato pronto mostrare tutto in penombra con READY grande al centro, diagonale, contornato e a scacchi, animato con ingrandimento e riduzione del 5%. L'unico comando utilizzabile e non Pronto, che riporta alla modifica. Anche il creatore pronto deve premere non Pronto prima di poter accedere alla X di annullamento.

Quando tutti i piloti presenti sono pronti, creare la gara e chiudere i modal a tutti. Prima di questo momento non deve esistere la gara.

## Criteri di verifica

Verificare: selezione presenti/assenti; ordine inverso e nuovi presenti in coda; ordine casuale prima gara; trascinamento; pool insufficiente senza scelta carte; copie duplicate; turni e autorizzazioni per pilota; anteprima locale e indicazione condivisa; conferma scelta e inventario; restituzione delle copie residue; recupero su riconnessione e ricaricamento da qualsiasi pagina; account con piu piloti; prima gara senza requisito esatto delle 15 carte; gare successive con tale requisito; pronto/non Pronto; creazione soltanto quando tutti sono pronti; annullamento con ripristino completo anche durante la preparazione; percorso Gara già disputata.

## Stato delle verifiche

Nessuna implementazione, migrazione, esecuzione di test o verifica browser della nuova funzione e attestata da questo documento. Nomi di nuovi moduli, rotte e tabelle saranno definiti soltanto dopo la lettura del codice e dello schema esistenti.

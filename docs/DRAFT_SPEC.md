# Draft e preparazione della gara

<!-- draft-validation-current:start -->

## Draft - stato verificato del 26 ottobre 2026

Questa sezione prevale esclusivamente sulle precedenti note di stato e verifica del flusso draft. Regole, specifiche delle altre fasi e contenuti storici restano conservati.

Base funzionale: commit 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a, ramo draft, PR #18 ancora in bozza e senza merge in main. Correzione delle chiavi del flusso e della proprieta delle risorse UI, non una nuova modifica di regole o API.

Verifiche lette: frontend (check, lint, test, build), runtime, backend pytest e migrazioni su database di test tutti success. Run CI 40269135082 e runtime 40269135447. I due job documentali di fase 16 sono skipped, non falliti.

Collaudo manuale positivo riferito dall autore il 26 ottobre alle 05:31: ora funziona tutto senza errori. Il riscontro segue i reset di presenze, zoom e mazzi e la correzione lifecycle. Non e un test browser automatizzato o una certificazione di tutti i dispositivi.

Le regole funzionali della specifica restano invariate; vengono aggiornate soltanto le note di stato e verifica.

Questo riallineamento non cambia codice applicativo, dipendenze, lockfile o dati e non esegue nuovi test dell applicazione. Nessun rilascio, ZIP finale o merge implicito. Interventi grafici successivi sospesi fino alla scelta dell autore.

[Evidenze, cronologia e limiti della validazione](DRAFT_VALIDATION.md).
<!-- draft-validation-current:end -->

## Precisazione del 25 ottobre 2026: controllo dopo la modifica dei mazzi

Richiesta dell'autore alle 13:55: il controllo di idoneita del mazzo deve avvenire alla fine, dopo la modifica dei mazzi, non dopo la selezione dei presenti. Questa precisazione prevale su precedenti riferimenti al controllo preliminare.

Alla conferma Presenti/Assenti si verificano partecipazione, numero dei presenti, autorizzazioni, riferimenti e disponibilita della pool, senza richiedere mazzi gia da 15 carte. Si prosegue con ordine/scelta oppure direttamente alla modifica mazzi se la pool e insufficiente. Il requisito delle 15 copie si applica al mazzo modificato quando il pilota conferma pronto, dalle gare successive alla prima. Prima di creare la gara si ricontrollano i mazzi di tutti i presenti sotto lock. Restano il massimo di 15, l'eccezione della prima gara e gli altri vincoli esistenti.

La correzione e successiva al consolidamento storico seguente: il manifesto descrive i sorgenti dell'artefatto originario, non gli hash della patch attuale. I risultati CI precedenti non attestano questa modifica. Nuovi test predisposti, nessuna nuova esecuzione locale o lettura CI per questa correzione.

<!-- draft-backend-current:start -->
## Provenienza storica del backend consolidato

Consolidamento del 25 ottobre 2026, ramo draft e PR 18. Questa sezione documenta la provenienza originaria e non sostituisce le precisazioni funzionali successive.

Sorgenti recuperati dall artefatto draft-backend-materialized della run 40152061495, job materialize-and-check concluso con success sul commit tecnico 1052e5d. Gli hash SHA-256 di quei sorgenti sono conservati in docs/DRAFT_BACKEND_MANIFEST.json.

Prima della pubblicazione quel workflow verifica pytest backend, upgrade/downgrade/upgrade con controlli dello schema e frontend check, lint, test e build. Esecuzione di pubblicazione: https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40153346360. Il controllo dedicato sul commit risultante documenta quelle verifiche pre-push; non e una nuova esecuzione dei job ordinari della PR o una verifica delle correzioni successive.

Nessun conteggio di test o warning inventato, nessun test locale o collaudo browser attestato dal consolidamento. Nessun merge, rilascio, ZIP finale o intervento sul database reale. Il frontend draft non era implementato da quel consolidamento ed e stato integrato successivamente.
<!-- draft-backend-current:end -->

Data della specifica: 2026-10-25. Aggiornamento dello stato: 2026-10-26. Specifica ricavata dalle richieste e conferme dell'autore. Ramo: draft. Implementazione integrata e correzione lifecycle verificata dalla CI sul commit 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a, con collaudo manuale positivo riferito dall'autore. Questa specifica aggiorna le regole precedenti solo per il flusso qui descritto.

## Metodo

Lavorare soltanto su Heat-pedal-to-the-roguelike e sul ramo draft, senza creare altri rami. Leggere i file prima di modificarli. Aggiornare la documentazione all'inizio e alla fine della modifica, non negli incrementi intermedi. Usare la PR di lavoro per la CI; non attendere la CI dei soli commit documentali. Affidare alla CI test backend, migrazioni e controlli frontend; non dichiarare esiti prima di averli letti. Nessun merge implicito. Nessuna modifica al database reale senza autorizzazione e backup.

## Apertura e annullamento

Nuova gara apre una procedura modale prima di creare la gara. La chiusura volontaria avviene esclusivamente con X in alto a sinistra, disponibile al creatore, con conferma testuale: annullare la gara? Esc e clic esterno non chiudono. Confermare annulla l'intera procedura e non crea alcuna gara. Ripristinare pool, inventari e mazzi da gioco allo stato precedente alla procedura, anche se alcune carte erano gia state scelte o i mazzi modificati.

Il modal iniziale offre draft e Gara già disputata. Il secondo chiude il modal e crea direttamente una gara normale, senza draft, preparazione READY o controllo preliminare dei mazzi; i risultati vengono inseriti successivamente.

## Presenti e assenti

Elencare i piloti iscritti al campionato in Presenti, ciascuno con Escludi. Escludi sposta il pilota in Assenti in fondo, con Includi per riportarlo tra i presenti. Avanti in basso a destra porta alla fase successiva senza richiedere che i mazzi siano gia da 15 carte. La partecipazione e il conteggio N riguardano i piloti presenti, non gli account. Uno stesso account puo avere piu piloti presenti.

## Ordine

Con pool sufficiente, mostrare i presenti nell'ordine inverso di arrivo della gara precedente. Chi non ha un risultato nella gara precedente viene aggiunto in fondo in ordine casuale. Senza gara precedente, disporre tutti casualmente e mostrare Prima gara in grassetto, in alto al centro. Il creatore puo riordinare trascinando i nomi. Avanti avvia la scelta delle carte e allarga il modal.

## Pool insufficiente

Servono N+3 copie nella pool modifiche del campionato. Se non bastano, mantenere la selezione Presenti/Assenti e poi passare direttamente alla modifica dei mazzi, saltando ordine e scelta carte. Non creare subito la gara e non bloccare il passaggio per mazzi ancora incompleti.

## Scelta delle carte

Estrarre N+3 copie dalla pool modifiche del campionato; sono ammesse piu copie della stessa carta. Ogni pilota presente sceglie una sola copia, nell'ordine confermato. Le tre copie non scelte tornano nella pool.

All'avvio della scelta aprire automaticamente il modal grande agli utenti proprietari dei piloti presenti, da qualunque pagina dell'app; il creatore lo ha gia aperto. I partecipanti non possono chiuderlo. Persistenza e recupero devono consentire a chi si riconnette o ricarica la pagina di ritrovare fase e turno correnti.

Per il proprietario del pilota di turno il modal ha sfondo verde e scritta lampeggiante tocca a te. Gli altri vedono sfondo rosso e Tocca a NOME DEL PILOTA CHE DEVE SCEGLIERE.

Chiunque puo ingrandire una carta premendola e riportarla alle dimensioni normali ripremendola. Solo durante il proprio turno, ingrandire una carta mostra agli altri un alone giallo sotto quella copia e il nome del pilota; al proprietario compare scegli. Scegli richiede conferma, rimuove la copia dalle carte disponibili e la aggiunge all'inventario modifiche del pilota. Le copie scelte compaiono nella sezione carte scelte con il nome del pilota.

Dopo l'ultima scelta non creare ancora la gara: passare alla preparazione dei mazzi.

## Preparazione mazzi e READY

Aprire la modifica del mazzo per i piloti presenti anche se i loro mazzi non soddisfano ancora il requisito delle 15 carte. Il controllo di idoneita si applica dopo la modifica, quando ciascun pilota conferma pronto, non alla conferma delle presenze. Dalla seconda gara pronto richiede esattamente 15 carte nel mazzo; alla prima gara non impone questa condizione. Il massimo di 15 e gli altri vincoli del mazzo restano validi.

La disponibilita e per pilota. Un utente con piu piloti presenti puo passare tra i propri piloti e confermarli singolarmente. La schermata READY completamente bloccata compare quando ha confermato tutti i propri piloti presenti.

Nello stato pronto mostrare tutto in penombra con READY grande al centro, diagonale, contornato e a scacchi, animato con ingrandimento e riduzione del 5%. L'unico comando utilizzabile e non Pronto, che riporta alla modifica. Anche il creatore pronto deve premere non Pronto prima di poter accedere alla X di annullamento.

Quando tutti i piloti presenti sono pronti, ricontrollare sotto lock i loro mazzi modificati, creare la gara e chiudere i modal a tutti. Prima di questo momento non deve esistere la nuova gara.

## Criteri di verifica

Verificare: selezione presenti/assenti senza requisito anticipato delle 15 carte; gare successive con mazzo vuoto o incompleto che raggiungono ordine/modifica; pool insufficiente senza blocco dei mazzi incompleti; ordine inverso e nuovi presenti in coda; ordine casuale prima gara; trascinamento; copie duplicate; turni e autorizzazioni per pilota; anteprima locale e indicazione condivisa; conferma scelta e inventario; restituzione delle copie residue; recupero su riconnessione/reload da qualsiasi pagina; account con piu piloti; prima gara senza requisito esatto delle 15 carte; pronto rifiutato con 14 carte nelle gare successive e accettato dopo modifica a 15; pronto/non Pronto; creazione soltanto a tutti pronti con ricontrollo finale; annullamento con ripristino completo anche durante la preparazione; percorso Gara già disputata.

## Stato delle verifiche

Sul commit 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a sono stati letti con successo frontend (check, lint, test, build), runtime, backend pytest e migrazioni su database di test. Il 26 ottobre alle 05:31 l autore ha riferito che ora funziona tutto senza errori, dopo il collaudo negativo delle 05:09 e la correzione del lifecycle. Non sono attestati test locali dell assistente, conteggi o una matrice completa di browser/dispositivi. Evidenze e limiti in DRAFT_VALIDATION.md. Il manifesto backend resta la provenienza storica del consolidamento, non un manifesto degli hash del codice corrente.

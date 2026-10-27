# Fase 16 - Riallineamento e lettura tecnica iniziale

Data: 2026-10-22. Solo phase-16-admin-pilot-inventory.
Stato: documenti riallineati in questo commit automatico; dominio puro aggiunto, integrazione ancora da eseguire.
Specifica approvata f87a759; base main 6dcdc836dba33a506bd954cd27eda3d212ba84ad,
merge PR 14. Questo blocco non implementa la funzionalita'.

## Documenti

Workflow vincola le versioni lette di PROJECT_SPEC.md, PROJECT_STATUS.md,
PROJECT_NOTES.md, PHASE_16_SPEC.md e PHASE_16_STATUS.md. Conserva tutto il resto dei
documenti generali lunghi e copia le sezioni operative della specifica gia' approvata
in una nuova appendice del master. Non ricostruisce il testo da risposte troncate.
Registra il merge reale della fase 15, avvio documentale della 16 e approvazione
senza dichiarare backend/frontend completati. Corregge solo l'intestazione/formula
di approvazione dei documenti 16, senza cambiare regole gia' concordate.

Git diff --check, titoli e perimetro prima del commit dei sei .md. Arresto su basi
o testa cambiate, niente force push. Il primo commit prepara workflow e nota;
leggere esito e bot per confermare il riallineamento. Nessun npm/pytest eseguito
in questo blocco solo documentale, nessun esito applicativo attribuito alla sua CI.

## Evidenze tecniche

Modello Pilot letto: tre Deck distinti. Modello Deck letto: cards persistito come
stringa e version con version_id_col di SQLAlchemy. Nessuna modifica a colonna,
formato JSON, schema o immagini proposta da questo riallineamento. Non e' un'analisi
del file SQLite originale: nessun DB originale aperto o modificato.

shop_purchase._lock_database letto: su SQLite prende BEGIN IMMEDIATE prima delle
letture quando non c'e' gia' una transazione nativa aperta; altrimenti non aggiunge
un nuovo blocco. create_race lo usa gia' ma non verifica la dimensione dei mazzi.
move_card legge stato e mazzi e usa versioni/retry, ma non prende quel blocco prima
delle letture. Per la nuova regola da 15 copie non basta aggiungere un controllo
frontend o un confronto versioni ai soli salvataggi admin: il blocco backend dovra'
coordinare avvio e modifica mazzo del giocatore per evitare decisioni su letture vecchie.
Questa esigenza e' analizzata, non gia' implementata o verificata in concorrenza.

## Blocco applicativo successivo

Definire e mostrare file, API/DTO e test prima della pubblicazione: elenco piloti
admin con username, snapshot dei cinque contenitori, salvataggio unico e validato,
lettura/aggiornamento con versioni e controllo di ruolo/iscrizione/gara/revisione.
Mantenere le cinque direzioni concordate e le copie fisicamente separate; nessuna
aggiunta diretta dalla pool al mazzo e nessuna doppia sottrazione. Salva confermato
con riepilogo testuale, immagini nelle altre sezioni. Backend primo, poi frontend.

Controllo esatto di 15 copie all'avvio per tutti gli iscritti, senza cambiare
l'inventario iniziale o rendere obbligatori 15 durante la preparazione. Aggiornare
fixture di prova, non dati di produzione. Live tramite client condiviso e REST
autorizzate, senza nuova esposizione di carte private o notifiche regalo inventate.
Non estendere altri CRUD o diritti del giudice. Nessun endpoint/evento nuovo gia'
introdotto da questi documenti e nessuna nuova dipendenza/migrazione dichiarata.

Nessuna modifica a main, applicazione, dati, immagini, dipendenze o lockfile.
Nessun setup, avvio, reset, backup o migrazione sul DB reale autorizzato. Tutti i
nuovi test, controlli automatici e prove browser della fase 16 restano da eseguire.

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/cards/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.

## Fase 16 - Incremento API admin di lettura

Data: 2026-10-22. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento espone letture, non il salvataggio o la gestione frontend.

## Contratto

- GET /api/admin/championships/{championship_id}/pilots: iscritti visibili,
  con pilot_id, name, user_id e username. Solo admin, mai password o sessioni.
- GET /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards:
  metadati del pilota, read_only, blocked_reason e cinque contenitori distinti.
- Ogni contenitore espone available, id, version e cards nel formato corrente
  name/path/copies. Le pool assenti hanno available=false, id/version null e
  cards vuoto; una pool esistente ma vuota e' disponibile. Nessuna pool creata.
- Tutti i Deck presenti vengono letti con una sola query. Riferimenti duplicati
  o mancanti e JSON corrotto danno 409, non carte inventate o svuotate.
- Campionato chiuso, gara o revisione non confermata sono leggibili ma indicati
  in sola lettura. Nessuna conferma automatica della revisione dentro queste GET.
- Il servizio ricontrolla il ruolo oltre alla dipendenza HTTP AdminUser.
  Pilota nascosto o non iscritto: 404. Giudice e giocatore: 403; anonimo: 401.

## File e verifiche

Nuovi schemas/admin_pilot_cards.py, services/admin_pilot_cards.py e
api/admin_pilot_cards.py; main.py registra il router senza alterare lifespan.
Test HTTP in backend/tests/test_admin_pilot_cards_api.py: 13 casi, inclusi i
parametri per ruoli e revisione. Verificano anche assenza di modifiche a Deck
ed EventLog, immagini/versioni, pool assenti o vuote, dati corrotti e privacy.
Alla preparazione: parsing Python e git diff --check riusciti. Test HTTP non
eseguiti localmente: vanno eseguiti nel repository completo, senza dichiararli
PASS sulla sola analisi sintattica. Il workflow documentale li esegue prima di
riallineare i dieci documenti generali e di fase. La CI completa resta separata.

## Limiti e seguito

Nessuna POST/PUT di gestione carte, transazione di salvataggio, evento nuovo,
regola di avvio da 15, modifica ai movimenti del giocatore o interfaccia ancora
aggiunta da questo incremento. Quelle parti restano da implementare e testare.
Le versioni lette non autorizzano una futura scrittura: il salvataggio dovra'
ricontrollare ruolo, iscrizione, stato gara/revisione e tutti i contenitori.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al DB reale. Restano
il formato confermato name/path/copies e i percorsi relativi ai media correnti.
Un messaggio vuoto o solo @GitHub approva la proposta pendente; le sole modifiche
documentali non richiedono attesa della CI applicativa. Nessun merge implicito.

<!-- phase16-admin-save:start -->
## Fase 16 - Salvataggio admin atomico

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Stato sintetico fase 16: Perimetro funzionale implementato, incluso live e riepilogo effettivo; CI 40026443509 riuscita su 2366d1d; riscontro manuale complessivamente positivo dell'autore, senza protocollo caso per caso; riallineamento finale documentale; nessun merge autorizzato.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del workflow.
Il titolo deve restare esattamente quello corrente; la riga di stato e' unica e
senza pipe. Questo documento consolida lo stato corrente; le note incrementali
precedenti restano nello storico Git. Non costituisce merge o rilascio in main.

### Contratto backend e conservazione delle copie

GET /api/admin/championships/{championship_id}/pilots restituisce iscritti visibili
con nome e username. GET e PUT sul percorso
/api/admin/championships/{championship_id}/pilots/{pilot_id}/cards leggono o
salvano il contesto del pilota. Accesso solo admin; nessun diritto ampliato al
giudice e nessuna modifica a utenti, team, ruoli, saldi o punteggi.

Il PUT riceve versions di tutti i cinque contenitori e transfers con soli
source/path. ID/version interi positivi; solo le due pool possono essere null.
Campi extra, destinazioni client e sostituzioni arbitrarie sono rifiutati.
Pool assente distinta da pool vuota, mai creata automaticamente. Riferimenti
Deck incoerenti o JSON corrotto non diventano contenitori validi o vuoti.

Ogni clic sposta una copia nelle sole direzioni approvate:
- game_deck verso modification_pool;
- modification_inventory verso modification_pool;
- sponsor_inventory verso sponsor_pool;
- modification_pool verso modification_inventory;
- sponsor_pool verso sponsor_inventory.

Nessun movimento diretto pool/mazzo, sponsor/mazzo o inventario/mazzo nella
schermata admin. Una rimozione dal mazzo non sottrae anche dall'inventario.
Il pianificatore clona gli input e rifiuta copie non valide, percorsi ambigui
e nomi associati a immagini discordanti, senza mutazioni parziali su errore.

Il backend ricontrolla ruolo, pilota visibile/iscritto, campionato chiuso, gara
aperta, revisione non confermata e tutte le versioni nella transazione. 409 per
conflitto, 422 per movimento non applicabile, senza retry automatici. Commit
unico di Deck/eventi e rollback anche su errore eventi. Differenze effettive
soltanto: versioni ed eventi non cambiano per un salvataggio senza differenze.
Dopo commit: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio con mazzi da 15

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli. Invalida identita' ORM precedenti e
rifiuta modifiche pendenti; promuove una transazione nativa gia' aperta tramite
UPDATE senza righe, senza cambiare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di tutti gli
iscritti, inclusi i nascosti, sotto lo stesso lock. Non 15 nomi o il totale degli
inventari; nessun nuovo minimo di iscritti. race_deck_snapshot.py riusa il
dominio race_deck_readiness.py. Mancanza mazzo o JSON corrotto non sono sanati.
Tra le gare un mazzo puo' restare incompleto, anche dopo un salvataggio admin.

Rifiuto di avvio: nessuna nuova gara o race.started, rollback e 409 con nomi e
conteggi dei non pronti, senza carte. BUSY/LOCKED diventano RaceStartConflictError
e 409; altri errori SQL non sono mascherati. Restano blocchi di chiusura e
gara/revisione non confermata; gestione precedente delle revisioni scadute invariata.

### UI, richiesta e riepilogo effettivo

Nelle impostazioni campionato l'admin apre Piloti, vede nome/username e un
pulsante Carte accessibile. Cinque sezioni apribili con immagini e quantita':
mazzo N/15 per copie, due inventari distinti e due pool. Su mobile le aree
restano in sequenza. Modal e CardTile riusati, senza nuovo scaffold o risorse.

Il piano costruisce versions dalla baseline, anche per contenitori non toccati,
e ricalcola la sequenza senza fidarsi di un'anteprima alterata. Percorsi entro
255 code point, identita' nomi coerente con strip().casefold() del backend.
Nessun arrotondamento di ID/version e nessuna destinazione/copertura di copie
arbitraria nella richiesta. Tutti gli output sono indipendenti dalla sessione.

Salva in fondo a destra apre un modal solo testuale con pilota, username, nome
carta, quantita', sorgente/destinazione e nuovo conteggio del mazzo. Il riepilogo
accorpa copie e compensa i versi opposti inventario/pool della stessa carta,
senza inventare un verso inverso verso il mazzo. Non cambia il registro PUT:
il server riceve i clic originali validati in ordine. Nessuna proposta di PUT
quando non restano variazioni effettive. Annulla, X, Escape e sfondo non inviano
e conservano la bozza. Solo Conferma e salva consuma una proposta una volta.

Durante conferme e operazioni sono protetti clic, ripristino, ritorno, chiusura
ordinaria e navigazione. Successo: nuova sessione da snapshot PUT e versioni
server. Errori conservano la bozza; 422 consente azioni manuali, altri errori
bloccano nuovi invii fino a rilettura. Esito di rete o risposta inutilizzabile
non provano un rollback. Rileggi dal server e' esplicito: con bozza pendente
richiede conferma e la sostituisce soltanto dopo risposta utilizzabile.
Ripristina bozza e' locale e conserva i blocchi, non equivale a una rilettura.
Il client controlla contesto e la creazione della sessione controlla carte:
non e' una validazione runtime completa di ogni campo del DTO.

### Live e lifecycle

Il pannello usa eventClient condiviso e riletture REST autorizzate tramite il
coordinatore createRefreshCoalescer. Nessun secondo EventSource, polling o
autosalvataggio. I segnali non trasferiscono carte e non autorizzano scritture.
Eventi pertinenti di carte, iscrizioni, gara/revisione, resync e riapertura del
trasporto invalidano il contesto; gli altri campionati sono filtrati. Lo stato
della connessione non viene presentato come prova della freschezza dei dati.

Riletture accorpate e risultati obsoleti scartati. Una bozza non viene
sovrascritta: aggiornamenti incompatibili la bloccano conservando i dati.
Le conferme aperte sono distinte dalle richieste HTTP effettivamente in corso:
un evento puo' invalidare la proposta prima dell'invio; durante PUT/GET viene
rinviato, evitando di scartare il successo del proprio salvataggio. Una GET
live puo' seguire un evento pendente dopo il PUT: non e' un retry della scrittura.
Solo l'accettazione di uno snapshot server utilizzabile libera il blocco delle
riletture, non un reset locale o un cambio di stato del trasporto.

Cambio utente/ruolo, campionato, pilota o smontaggio invalidano il contesto;
risposte e callback tardive non ripopolano un contesto successivo. I cleanup
rimuovono i soli listener propri, senza chiudere lo stream condiviso. Una
chiusura forzata del browser non annulla una scrittura gia' inviata.

### Esiti finali verificati e collaudo dell'autore

Codice candidato: 2366d1de37cf1cf638b45c55313a3e31601eebff. CI 40026443509
riuscita per Frontend (check, lint, test, build), job 120664599995, Backend
(pytest), job 120664600371, Migrazioni (database di test), job 120664600375,
e Documenti fase 16 dopo backend, job 120665715224. Non sono nuove esecuzioni
locali. I conteggi complessivi di test e warning non sono stati letti dai log.

Dopo il via libera e la checklist in conversazione sul candidato 2366d1d,
il 2026-10-23 alle 23:59 CEST l'autore riferisce: «sembra funzionare tutto».
E' un riscontro manuale complessivamente positivo, non un verbale con esito
per ogni caso. Non sono stati forniti browser/dispositivo, log o risultati
individuali; non si marca automaticamente ogni voce OK. Non e' un collaudo
browser eseguito dall'assistente ne' prova di tutte le condizioni concorrenti.

Restano non attestati singolarmente i casi avanzati della checklist: doppio
invio, rete interrotta/esito incerto, conflitti tra sessioni, risposte tardive,
permessi e scadenza durante rete, rollback/concorrenza reale e privacy dei
payload. Le coperture automatiche e il riscontro qualitativo non vanno confusi.

### Tracciabilita' delle verifiche precedenti

Storico: dominio 934333c; sessione eedd729; chiusura modal d9ee662; UI c950510;
trasporto PUT 549e83e/f95c915; piano 024d47a/ad377d4; salvataggio 9769dd5/7d449cb;
adattatore eventi ecbf684/e725ba4; riletture 914ee47; collegamento live
fbcbd89/dc06e29; rimozione import 78661d8; prefer-const nei test 283c0ac;
riepilogo effettivo e posizione Salva 6d1b7cd/2366d1d. I controlli finali
sopra sostituiscono come stato corrente le letture incrementali in coda.

Il precedente riepilogo dell'autore era 748 passed, 14 warnings e 14 subtests
passed prima della pulizia 4514348; 27 asserzioni snapshot conservate tramite
AST. La regressione 72 failed/676 passed, poi un fallimento, era stata corretta
senza saltare test o allentare il dominio. Non sono i conteggi della CI finale.
Dieci casi di readiness includevano lock simulato, non tutta la concorrenza reale.

Identita' Unicode 15.0 verificata con confronto Node/Python su 1.112.064 scalari
e nove casi composti, senza NFC/rimozione accenti; non era type-check. Controlli
Node senza tipi: dodici scenari politica modal, venticinque adattatore eventi
e nove coordinatore riletture; non equivalgono a Vitest o browser. Sette test
Python della trasformazione documentale su fixture temporanee erano riusciti,
non il workflow GitHub completo. Le esecuzioni npm locali non sono inventate.

### Riallineamento documentale e consegna

Il titolo stabile e' stato ripristinato in f8a94e4; la tabella PROJECT_STATUS
deriva dalla riga Stato sintetico fase 16, senza stato hardcoded su vecchi commit.
Il pin CI aggiornato usa il blob 6858f05d89072cca488efeeb46166a2770383545 del
workflow approvato. Restano controlli su titolo, stato unico e marcatori anche
invertiti/adiacenti, protezioni di ramo e percorsi e nessun force-push.

Questo commit aggiorna soltanto i documenti sorgente e dedicati, dopo codice e
verifiche come richiesto dall'autore. La propagazione ai dieci documenti generali
va verificata dopo la pubblicazione, senza attendere nuovi test applicativi
per i soli docs. Il successo del job documentale sul codice precedente non
dimostra gia' propagato questo nuovo testo. Nessun merge, rilascio o ZIP finale
creato implicitamente; la PR resta in bozza.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato il 2026-10-22. Nessuna conversione a path/value o /images/cards,
migrazione, dipendenza, modifica di setup/avvio o accesso al database reale
da parte dell'assistente. Perimetro funzionale fase 16 distinto dal resto
delle istruzioni generali del progetto e da una consegna ZIP complessiva.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

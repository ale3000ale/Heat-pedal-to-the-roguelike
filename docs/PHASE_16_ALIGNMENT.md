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

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
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
Stato sintetico fase 16: Backend, client PUT, piano e salvataggio UI implementati; controlli applicativi riusciti su 7d449cb; live e collaudo browser da completare; fase non conclusa.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del processo
di riallineamento. Non rinominare il titolo senza aggiornare e verificare i suoi
consumatori. Questo documento consolida le note precedenti, conservate in Git.
Nessun merge, migrazione o prova sul database reale impliciti.

### Contratto backend

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions include tutti i cinque contenitori, con id/version
interi positivi; solo le due pool possono essere null. Ogni trasferimento contiene
solo source/path e sposta una copia, con destinazione imposta dal dominio. Campi
extra, destinazioni client e sostituzioni arbitrarie delle carte sono rifiutati.

Il backend ricontrolla admin, pilota visibile/iscritto, chiusura campionato, gara
aperta e revisione non confermata nella transazione. Confronta id e versione
anche dei contenitori non toccati. Pool assenti non create e non utilizzabili
come sorgente o destinazione. Conflitto 409 senza retry automatico; movimento
non applicabile 422. Commit unico Deck/eventi, rollback anche su errore eventi.

Il mazzo puo' restare incompleto tra le gare. Nessuna aggiunta pool/mazzo o
sponsor/mazzo e nessuna doppia sottrazione. Solo differenze effettive cambiano
versioni ed eventi. La risposta contiene snapshot e versioni server. Dopo
variazioni: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock e avvio gara

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli; invalida identita' ORM precedenti e
rifiuta modifiche pendenti. La transazione nativa gia' aperta viene promossa con
UPDATE senza righe, senza modificare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di ogni iscritto
sotto lo stesso lock, non 15 nomi o il totale degli inventari. Include iscritti
nascosti, senza nuovo minimo di iscritti. race_deck_snapshot.py riusa il dominio
race_deck_readiness.py. Mazzo mancante o JSON corrotto non diventano validi.

Iscritto non pronto: niente nuova gara o race.started, rollback e 409 con nomi e
conteggi, senza carte. BUSY/LOCKED diventano RaceStartConflictError e 409; altri
errori SQL non mascherati. Restano chiusura e gara/revisione non confermata; la
gestione preesistente delle revisioni scadute prima dell'avvio non cambia.

### Verifiche e incrementi precedenti

La CI 39917281059 su 4514348 e align-docs-pr 39917281153 risultavano riusciti.
L'autore aveva fornito prima della pulizia 748 passed, 14 warnings e 14 subtests
passed. 4514348 rimuove Result.tuples() da due snapshot eventi mantenendo 27
asserzioni verificate tramite AST. I warning successivi non sono stati contati
dai log. La regressione iniziale di 72 failed/676 passed, poi un fallimento, e'
stata corretta in fixture e aspettative senza saltare test o allentare il dominio.
Dieci casi in test_race_start_readiness.py includono conteggi, JSON corrotto,
admin/giudice, non iscritti, rollback eventi e lock simulato: non provano tutte
le interazioni concorrenti reali o il browser.

Client GET e tipi c01b486, correzione Prettier 822a85a e consultazione bb7f0f7,
corretta in 89cab3d/72e4274, hanno riscontri frontend nelle CI 39976945581 e
39986696961. Quattro test di conteggio coprono copie, vuoto e 14/16 senza
correzioni artificiali, non interazioni Svelte.

934333c aggiunge il pianificatore: game_deck e modification_inventory verso
modification_pool; sponsor_inventory verso sponsor_pool; modification_pool verso
modification_inventory; sponsor_pool verso sponsor_inventory. Una copia per
clic, input immutati anche su errore tardivo, ID/versioni invariati; percorsi
ambigui e immagini discordanti rifiutati. admin-card-identity.ts conserva
strip().casefold() con Unicode 15.0, senza NFC o rimozione accenti: confronto
Node/Python su 1.112.064 scalari e nove casi composti, non un type-check.
Prettier locale era indisponibile, con ENOTCACHED e comando globale assente.
b54cc84 mantiene le aspettative e aggiunge commenti dei code point; f2dc492
formatta il test. La lettura delle 19:21 della CI 39994183218 in coda e' storica,
non un successo; successivamente la CI 39995224182 e' risultata riuscita.

eedd729 aggiunge sessione e otto test: baseline, anteprima e registro separati,
blocco senza perdita, ripristino locale che conserva il blocco. Nessun retry,
rebase o scrittura automatici. d9ee662 aggiunge onrequestclose e politica modal
con dodici casi parametrizzati; dodici scenari Node senza tipi erano riusciti
prima della CI 39997899845. Senza callback resta la chiusura precedente; con
callback nessun open=false automatico, X disponibile ed Escape/sfondo rispettano
closeOnOutside. Non sono prove browser.

### Bozza, client PUT e piano

c950510 collega le carte alla sessione: cinque sezioni con immagini, tre
contenitori del pilota separati dalle due pool, mazzo N/15 per copie e pool
assente distinta da vuota. Modal/CardTile riusati, nessuno scaffold, dipendenza
o risorsa nuova. Le risposte tardive vengono ignorate, non annullate in rete.
Ripristino, ritorno, chiusura e navigazione sono protetti prima dello scarto.
Il ripristino usa la baseline e conserva il blocco, senza rileggere il server.

2cf25fd separa pubblicazione dello stile e controlli successivi; ceb12b1 formatta
i quattro componenti. 788e6f5 aggiunge una sola eccezione ESLint alla chiamata
goto che riusa navigation.to.url.href, senza modifica della logica o esclusione
globale. La CI 40003767478 e align-docs-pr 40003767471 erano riusciti.

549e83e aggiunge tipi e trasporto PUT, f95c915 ne formatta il test. Il client
verifica ID e contesto della risposta, non l'intero DTO runtime; propaga ApiError
e segnala risposte inutilizzabili con AdminCardSaveResponseError. Nessun retry
o GET automatica e nessuna interpretazione di errore rete come rollback certo.
024d47a aggiunge il piano, formattato in ad377d4: tutte le versioni della baseline,
trasferimenti source/path, anteprima ricalcolata e riepilogo ordinato per clic,
non differenze nette. Pool assenti null, metadati incoerenti rifiutati e percorsi
entro 255 code point. La CI frontend 40009944027 era riuscita su ad377d4.

### Salvataggio UI implementato

9769dd5 collega riepilogo e conferma unica al PUT; 7d449cb formatta i quattro
componenti. admin-pilot-cards-save-controls.svelte prepara la proposta senza
rete; Annulla, X, Escape e sfondo non inviano. Conferma e salva consuma la
proposta e blocca prima del primo await: nessun secondo invio dalla stessa
proposta. Sessione cambiata: nuovo riepilogo richiesto.

Durante conferme, PUT e rilettura, lo stato occupato raggiunge elenco piloti e
impostazioni e blocca clic, ripristino, ritorno e chiusura ordinaria. La navigazione
normale e' annullata; una chiusura forzata del browser non annulla una scrittura
gia' inviata. Risposte di componenti dismessi/sessioni sostituite ignorate.

Successo: nuova sessione dallo snapshot PUT e versioni server, senza GET.
Errori: bozza conservata; 422 consente una nuova azione manuale. Altri errori
bloccano nuovi invii: 401/403/404/409 come rifiuti/conflitti, gli altri come esiti
incerti che potrebbero essere gia' applicati. Rileggi dal server e' esplicito e
conferma lo scarto se ci sono operazioni; la bozza viene sostituita soltanto dopo
una lettura utilizzabile. Lettura fallita: baseline, anteprima e registro conservati.
Ripristinare localmente non sblocca un conflitto e non sostituisce tale rilettura.

### Ultima verifica e guasto documentale

CI 40012639610 sul codice formattato 7d449cb: Frontend (check, lint, test, build),
job 120622516434, Backend (pytest) e Migrazioni (database di test) riusciti.
Il job Documenti fase 16 dopo backend, 120623536970, e' invece fallito: il titolo
era stato rinominato aggiungendo e bozza UI e non rispettava il startswith esatto.
Non dichiarare questa CI interamente verde o il browser collaudato. Nessuna nuova
esecuzione npm locale o conteggio complessivo di test/warning dai singoli log.

Questa correzione ripristina il titolo stabile e fa derivare la riga della tabella
di PROJECT_STATUS dalla riga Stato sintetico fase 16 del sorgente. Mantiene
validazione esatta del titolo, unicita' dello stato e marcatori; corregge anche
il riconoscimento di marcatori invertiti adiacenti. Sette test Python eseguiti
su fixture temporanee della trasformazione sono riusciti: aggiornamento dei
dieci file, idempotenza, preservazione del testo esterno, rifiuto degli input
invalidi e nessuna scrittura parziale. Non sono esecuzioni del workflow GitHub,
dell'installazione dipendenze, di pytest o del push. Propagazione ancora da verificare.

### Limiti e seguito

Restano integrazione live tramite client SSE condiviso e collaudo browser di
annullamento, doppi clic, successo, 409, rete incerta, 422, rilettura fallita,
Escape, chiusura/ritorno durante rete e risposte tardive. I test di client, piano
e sessione non sono test DOM del nuovo flusso. Nessun polling, autosalvataggio
o stream SSE aggiuntivo. Fase non completa e nessun merge.

Dopo controlli applicativi riusciti, riallineare i documenti e verificare la
propagazione nei dieci file generali, senza attendere altri test applicativi per
i soli docs. format-review-ui.yml resta circoscritto ai quattro componenti di
salvataggio, con npm ci, Prettier dal lockfile, SHA controllata, protezioni del
ramo e dei percorsi estranei; un commit del bot non prova il verde globale.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato dall'autore il 2026-10-22. Nessuna conversione a path/value,
migrazione, modifica di setup/avvio o accesso al database reale.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

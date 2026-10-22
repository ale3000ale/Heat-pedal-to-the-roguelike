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

# Script — Heat

Ultimo aggiornamento: 2026-10-13

Descrizione dei comandi di `heat.py` (letto il 2026-10-13). Si eseguono dalla radice del repository. Senza argomenti `python heat.py` apre un menu interattivo.

## Comandi

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Menu con sei voci (setup, migrazioni, avvio completo, solo backend, test backend, controlli frontend) e `0` per uscire. Mostra il sistema operativo e la versione di Python rilevati. |
| `python heat.py setup` | Ambiente virtuale, dipendenze, migrazioni, prototipo del mazzo, utente admin, dipendenze frontend. Opzioni: `--skip-admin`, `--skip-seed`. |
| `python heat.py migrate` | Esegue `alembic upgrade head` nell'ambiente `backend/.venv`. |
| `python heat.py start` | Applica le migrazioni, poi avvia backend (127.0.0.1:8000) e frontend (127.0.0.1:5173). Opzione: `--backend-only`. |
| `python heat.py test` | Esegue `python -m pytest -q` in `backend/`. |
| `python heat.py check` | Esegue `node tools/check-frontend.mjs` (format, check, lint e test del frontend, come indicato nel commento dello script). |

## Comportamento comune

- Gli errori fermano il comando con un messaggio che inizia con "ERRORE"; dal menu l'errore viene mostrato e il menu resta aperto.
- `test` e `check` non fermano lo script se falliscono: il codice di uscita dei test non viene propagato come errore di `heat.py`.
- I comandi che usano il backend richiedono `backend/.venv`; se manca indicano di scegliere prima "Setup".
- Su Windows i processi si fermano con `taskkill`, su macOS e Linux con un segnale al gruppo di processi.

## Non verificato

Non ho letto il contenuto di `tools/` (oltre al nome `check-frontend.mjs`), né gli script `app.scripts.seed_prototype`, `app.scripts.create_admin` e `app.scripts.resize_cards`. Non ci sono backup, ripristino, reset o build del frontend: nel ramo non esiste una cartella `scripts` né i file `setup.bat` e `setup.sh`.

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
Questa versione consolida le precedenti note incrementali: il backend di lettura,
salvataggio e avvio con mazzi da 15 e' implementato. La cronologia delle versioni
precedenti resta nello storico Git. Nessun merge o completamento della fase implicito.

### Contratto di scrittura admin

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions descrive tutti i cinque contenitori con id/version
interi positivi, oppure null per le sole pool assenti. Ogni trasferimento contiene
solo source e path: una copia per elemento, destinazione imposta dal dominio.
Campi extra, destinazioni client e sostituzioni arbitrarie delle carte sono rifiutati.

Il backend ricontrolla ruolo admin, pilota visibile/iscritto, campionato chiuso,
gara aperta e revisione non confermata nella transazione. Confronta id e versione
anche dei contenitori non toccati. Le pool assenti non vengono create e non possono
fornire o ricevere copie. Conflitto: 409 senza retry automatico; movimento non
applicabile: 422. Un solo commit per Deck ed eventi, rollback anche su errore eventi.

Il mazzo puo' restare incompleto tra le gare. Nessuna aggiunta diretta pool/mazzo
o sponsor/mazzo e nessuna doppia sottrazione. Solo differenze effettive cambiano
le versioni; senza differenze non vengono prodotti eventi. La risposta restituisce
snapshot e versioni aggiornate. Dopo variazioni: cards.changed pubblico vuoto e
privato al proprietario con solo pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio gara

services/sqlite_write_lock.py e' usato da salvataggio admin, pilot_deck.move_card
e races.create_race prima delle letture autorevoli. Invalida le identita' ORM
precedenti e rifiuta modifiche pendenti. Una transazione nativa gia' aperta viene
promossa con UPDATE senza righe: nessuna carta o versione viene modificata dal lock.
Il retry preesistente di move_card resta limitato a StaleDataError; il salvataggio
admin e l'avvio gara non ritentano automaticamente i conflitti di lock.

create_race legge i mazzi da gioco di tutti gli iscritti sotto lo stesso lock e
richiede esattamente 15 copie totali, non 15 nomi o il totale degli inventari.
La lettura DB in race_deck_snapshot.py riusa il dominio race_deck_readiness.py;
include gli iscritti nascosti e non aggiunge un nuovo minimo di iscritti.
Mazzo mancante o JSON corrotto non vengono trasformati in un mazzo valido.

Se un iscritto non e' pronto: nessuna nuova gara o race.started, rollback e HTTP
409 con riepilogo testuale di nomi e conteggi, senza carte. I conflitti SQLite
BUSY/LOCKED vengono tradotti in RaceStartConflictError e HTTP 409; gli altri
errori SQL non sono mascherati. Restano chiusura e gara/revisione non confermata.
La gestione preesistente delle revisioni scadute prima dell'avvio non e' cambiata.

### Verifiche effettive

Il 2026-10-23 e' stata letta la CI 39917281059 sul codice 4514348: successo per
Backend (pytest), Frontend (check, lint, test, build), Migrazioni (database di test)
e Documenti fase 16 dopo backend. Anche align-docs-pr, esecuzione 39917281153,
risulta riuscito. Questi sono riscontri GitHub, non nuove esecuzioni locali.

L'autore ha fornito il riepilogo precedente alla pulizia dei warning: 748 passed,
14 warnings e 14 subtests passed. Il commit 4514348 rimuove soltanto Result.tuples()
dai due snapshot dei test eventi, conservando le 27 asserzioni verificate tramite
AST. La CI successiva e' verde; il conteggio esatto dei warning di quella nuova
esecuzione non e' stato letto e non viene dichiarato zero sulla sola conclusione.

La regressione iniziale mostrava 72 failed e 676 passed, poi un solo fallimento.
Le fixture residue del giudice e del secondo campionato, l'aspettativa sul nuovo
errore di conflitto e la preparazione dei mazzi nel test della classifica congelata
sono state corrette senza saltare test o allentare il vincolo di produzione.

I test dedicati comprendono dominio puro, letture e salvataggi admin, snapshot DB,
lock e avvio: dieci casi in test_race_start_readiness.py coprono conteggi errati,
JSON corrotto, accesso admin/giudice, esclusione dei non iscritti, rollback eventi
e traduzione di un lock occupato simulato. Non equivalgono a un collaudo browser
o a una nuova prova reale di tutte le interazioni concorrenti avvio/admin/giocatore.

### Primo frontend: client verificato e UI di consultazione

I tipi e il client GET admin sono stati aggiunti in c01b486. La CI frontend si
e' fermata inizialmente su Prettier; 822a85a corregge soltanto la formattazione
della condizione. Il job Frontend (check, lint, test, build) 120493926882 della
CI 39976945581 risulta riuscito ed e' stato letto il 2026-10-23. Nessuna nuova
esecuzione npm locale e nessun collaudo browser dichiarati.

Questo incremento aggiunge la UI di consultazione, ancora da verificare in CI
e nel browser: Piloti nelle impostazioni campionato solo admin, nome e username,
pulsante Carte con etichetta accessibile e cinque sezioni apribili con immagini.
I tre contenitori del pilota restano separati dalle due pool. Il mazzo mostra
N/15 contando copie; pool assente e pool vuota restano distinte. Modal e CardTile
esistenti vengono riusati; nessun nuovo scaffold, dipendenza o copia di immagini.

Le letture ignorano risposte tardive dopo cambio contesto o smontaggio del pannello;
non annullano la richiesta di rete gia' inviata. Caricamento, errori e rilettura
manuale sono espliciti. Nessun trasferimento, PUT, autosalvataggio, polling o
nuovo stream SSE. Gli errori di permesso rimangono controllati dal backend.
Quattro casi Vitest preparati verificano il conteggio delle copie senza mutazioni,
contenitore vuoto e conteggi 14/16 non corretti artificialmente. Non sono test
del rendering Svelte o di interazione browser e non sono ancora dichiarati PASS.

### Limiti, dati e prossimo passo

Restano da verificare UI di consultazione e relativi controlli, poi implementare
trasferimenti in bozza, conferma testuale, protezione della bozza e collegamento
live tramite il client SSE condiviso, con verifiche dedicate e collaudo browser.
Non dichiarare la fase 16 completa sulla sola CI del backend o del client GET.
Verificare la propagazione di questo stato nei dieci documenti gestiti dal processo
esistente. Nessuna attesa CI applicativa per i soli commit documentali e nessuna
chiusura/riapertura abituale della PR.

Deck.cards resta TEXT con array JSON name/path/copies e i percorsi correnti relativi
ai media, come confermato dall'autore il 2026-10-22. Nessuna conversione al vecchio
esempio path/value, migrazione, dipendenza nuova, modifica a setup/avvio o accesso
al database reale. Nessun nuovo scaffold o modifica delle risorse.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

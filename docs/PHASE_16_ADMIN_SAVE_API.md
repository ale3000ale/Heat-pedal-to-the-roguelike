# Fase 16 - Salvataggio admin atomico

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Il backend di lettura, salvataggio e avvio con mazzi da 15 e' implementato.
Questa versione consolida le note precedenti, conservate nello storico Git.
Nessun merge o completamento della fase implicito.

## Contratto di scrittura admin

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

## Lock condiviso e avvio gara

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

## Verifiche effettive del backend

La CI 39917281059 sul codice 4514348 e align-docs-pr 39917281153 sono stati
letti il 2026-10-23: successo per backend, frontend, migrazioni e documenti.
L'autore aveva fornito prima della pulizia dei warning: 748 passed, 14 warnings
e 14 subtests passed. 4514348 rimuove soltanto Result.tuples() dai due snapshot
dei test eventi, conservando le 27 asserzioni verificate tramite AST. Il numero
esatto dei warning della successiva CI non e' stato letto e non viene assunto zero.

La regressione iniziale mostrava 72 failed e 676 passed, poi un solo fallimento.
Le fixture residue del giudice e del secondo campionato, l'aspettativa sul nuovo
errore di conflitto e la preparazione dei mazzi nel test della classifica congelata
sono state corrette senza saltare test o allentare il vincolo di produzione.

I test dedicati comprendono dominio puro, letture e salvataggi admin, snapshot DB,
lock e avvio: dieci casi in test_race_start_readiness.py coprono conteggi errati,
JSON corrotto, accesso admin/giudice, esclusione dei non iscritti, rollback eventi
e traduzione di un lock occupato simulato. Non equivalgono a un collaudo browser
o a una nuova prova reale di tutte le interazioni concorrenti avvio/admin/giocatore.

## Primo frontend: client e UI di consultazione verificati in CI

Tipi e client GET admin sono stati aggiunti in c01b486. 822a85a corregge il primo
stop Prettier; il job frontend 120493926882 della CI 39976945581 risulta riuscito.
La UI e' stata aggiunta in bb7f0f7, con correzioni di formattazione in 89cab3d
e 72e4274. La CI 39986696961 su 72e4274 e align-docs-pr 39986696945 risultano
riusciti. Non sono esecuzioni locali ne' conteggi complessivi letti dai log.

La schermata presenta Piloti nelle impostazioni campionato solo admin, nome e
username, pulsante Carte con etichetta accessibile e cinque sezioni apribili con
immagini. I tre contenitori del pilota restano separati dalle due pool. Il mazzo
mostra N/15 contando copie; pool assente e pool vuota restano distinte. Modal e
CardTile esistenti vengono riusati; nessun nuovo scaffold, dipendenza o copia
di immagini. Il rendering e le interazioni nel browser restano da collaudare.

Le letture ignorano risposte tardive dopo cambio contesto o smontaggio del pannello;
non annullano la richiesta di rete gia' inviata. Caricamento, errori e rilettura
manuale sono espliciti. Nessun trasferimento, PUT, autosalvataggio, polling o
nuovo stream SSE nella UI. Gli errori di permesso rimangono controllati dal backend.
I quattro casi del modulo Vitest sul conteggio coprono copie senza mutazioni,
contenitore vuoto e conteggi 14/16 non corretti artificialmente. Non sono test
del rendering Svelte o del browser.

## Dominio e sessione locale della bozza

934333c aggiunge admin-pilot-cards-draft.ts e i test: una copia per operazione,
destinazioni imposte dal dominio nelle cinque direzioni approvate, nessuna doppia
sottrazione, pool assenti non create, percorsi ambigui e immagini discordanti
rifiutati. Snapshot originale, ID e versioni non vengono modificati. Un errore
tardivo non applica parzialmente la sequenza agli input. Nessuna rete o PUT.

admin-card-identity.ts usa dati casefold Unicode 15.0 per conservare l'identita'
strip().casefold() del backend senza aggiungere NFC o rimozione degli accenti.
Il modello dei dati e' stato verificato in Python; una copia JavaScript con le
sole annotazioni di tipo rimosse e' stata eseguita in Node e confrontata con Python
su 1.112.064 valori scalari e nove casi composti. Non e' un type-check TypeScript.
Il formatter locale non era disponibile: tentativo offline ENOTCACHED e comando
globale assente. Nessun successo locale di Prettier o Vitest viene inventato.

b54cc84 aggiunge commenti dei code point e callback di verifica errori a blocco,
mantenendo operazioni e aspettative. eedd729 aggiunge admin-pilot-cards-session.ts
e otto test dedicati. La sessione separa baseline, anteprima e registro; blocca
ulteriori clic senza perdere la bozza e offre un ripristino esplicito che conserva
il blocco corrente. Non esegue rebase automatico, retry, scarto implicito o scritture.

Il bot f2dc492 ha formattato soltanto admin-pilot-cards-draft.spec.ts disponendo
su piu' righe l'array della chiamata con sorgente constructor. La precedente
lettura delle 19:21 CEST mostrava la CI 39994183218 in coda: era un riscontro
storico, non una prova di successo. Successivamente sono stati letti come riusciti
frontend, backend, migrazioni e documenti nella CI 39995224182. Il bot 08f3443
ha propagato lo stato di dominio e sessione nei dieci documenti generali gestiti.

## Chiusura intercettabile del modal verificata in CI

d9ee662 aggiunge modal-close.ts e modal-close.spec.ts e modifica modal.svelte.
La nuova prop onrequestclose e' opzionale: senza callback rimane la chiusura
preesistente; con callback viene delegata la decisione senza open=false automatico.
La X resta disponibile con closeOnOutside falso; Escape e sfondo rispettano quel
flag anche quando e' presente l'intercettore. Un errore del callback non autorizza
la chiusura predefinita. Non sono introdotti dialog nativi o nuove dipendenze.

Sono stati preparati dodici casi parametrizzati Vitest. Prima del commit, dodici
scenari sul corpo JavaScript della politica, con i soli tipi rimossi, sono riusciti
in Node con assert. Questo controllo locale non era una compilazione TypeScript
o una prova browser. La lettura del 2026-10-23 della CI 39997899845 su d9ee662
mostra successo per Frontend (check, lint, test, build), job 120566109552,
Backend (pytest), Migrazioni (database di test) e Documenti fase 16 dopo backend.
Anche align-docs-pr 39997899981 e format 39997890111 risultano riusciti.
Non sono stati letti conteggi complessivi o warning dai singoli log.

Il ramo osservato resta su d9ee662: nessun ulteriore commit del formatter e' stato
osservato. format-review-ui.yml rimane limitato al ramo fase 16 e ai tre file
modal-close.ts, modal-close.spec.ts e modal.svelte; esegue Prettier dal lockfile,
check, lint, test e build prima dell'eventuale pubblicazione. La CI ordinaria non
e' stata modificata. Dettagli del sottoincremento in PHASE_16_DRAFT_UI.md.

## Limiti, dati e prossimo passo

I componenti admin non passano ancora onrequestclose. La sessione e il
pianificatore non sono ancora collegati ai clic: la UI resta in consultazione.
Restano integrazione della bozza, conferma prima di ripristino, ritorno all'elenco,
chiusura e navigazione, riepilogo testuale, conferma unica del salvataggio e live
tramite il client SSE condiviso, oltre a verifiche dedicate e collaudo browser.
Il ripristino della sessione non rilegge il server: distinguere lo scarto confermato
da una rilettura o da un conflitto da preservare. Non dichiarare la fase completa.

Dopo le modifiche applicative riuscite riallineare questi documenti e verificarne
la propagazione nei dieci documenti generali. Per i soli commit documentali non
attendere nuovi test applicativi. Nessuna chiusura/riapertura abituale della PR.

Deck.cards resta TEXT con array JSON name/path/copies e percorsi relativi ai media,
come confermato dall'autore il 2026-10-22. Nessuna conversione al vecchio esempio
path/value, migrazione, modifica a setup/avvio o accesso al database reale.
Nessun nuovo scaffold o modifica delle risorse.

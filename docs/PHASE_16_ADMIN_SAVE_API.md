# Fase 16 - Salvataggio admin atomico

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questa versione consolida le precedenti note incrementali: il backend di lettura,
salvataggio e avvio con mazzi da 15 e' implementato. La cronologia delle versioni
precedenti resta nello storico Git. Nessun merge o completamento della fase implicito.

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

## Verifiche effettive

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

## Primo frontend: client e UI di consultazione verificati in CI

I tipi e il client GET admin sono stati aggiunti in c01b486. La CI frontend si
e' fermata inizialmente su Prettier; 822a85a corregge soltanto la formattazione
della condizione. Il job Frontend (check, lint, test, build) 120493926882 della
CI 39976945581 risulta riuscito ed e' stato letto il 2026-10-23. Nessuna nuova
esecuzione npm locale e nessun collaudo browser dichiarati.

La UI di consultazione e' stata aggiunta in bb7f0f7; 89cab3d corregge gli a capo
nei componenti e 72e4274 rimuove la riga vuota duplicata rimasta nel test. La CI
39986696961 su 72e4274 e' stata letta il 2026-10-23: successo per Frontend
(check, lint, test, build), job 120527608290, Backend (pytest), Migrazioni
(database di test) e Documenti fase 16 dopo backend. Anche align-docs-pr della
CI 39986696945 risulta riuscito. Non sono nuove esecuzioni locali e non viene
inventato un conteggio complessivo di test o warning dai soli stati dei job.

La schermata presenta Piloti nelle impostazioni campionato solo admin, nome e
username, pulsante Carte con etichetta accessibile e cinque sezioni apribili con
immagini. I tre contenitori del pilota restano separati dalle due pool. Il mazzo
mostra N/15 contando copie; pool assente e pool vuota restano distinte. Modal e
CardTile esistenti vengono riusati; nessun nuovo scaffold, dipendenza o copia
di immagini. Il rendering e le interazioni nel browser restano da collaudare.

Le letture ignorano risposte tardive dopo cambio contesto o smontaggio del pannello;
non annullano la richiesta di rete gia' inviata. Caricamento, errori e rilettura
manuale sono espliciti. Nessun trasferimento, PUT, autosalvataggio, polling o
nuovo stream SSE. Gli errori di permesso rimangono controllati dal backend.
I quattro casi del modulo Vitest sul conteggio sono inclusi nella suite frontend
risultata riuscita: copie senza mutazioni, contenitore vuoto e conteggi 14/16
non corretti artificialmente. Non sono test del rendering Svelte o del browser.

## Limiti, dati e prossimo passo

Restano il collaudo browser della UI di consultazione e le verifiche specifiche
delle interazioni. Il prossimo blocco da proporre e' la logica dei trasferimenti
in bozza, senza scritture, poi conferma testuale, protezione della bozza e
collegamento live tramite il client SSE condiviso, con verifiche dedicate.
Non dichiarare la fase 16 completa sulla sola CI del backend o del frontend.
Verificare la propagazione di questo stato nei dieci documenti gestiti dal processo
esistente. Nessuna attesa CI applicativa per i soli commit documentali e nessuna
chiusura/riapertura abituale della PR.

Deck.cards resta TEXT con array JSON name/path/copies e i percorsi correnti relativi
ai media, come confermato dall'autore il 2026-10-22. Nessuna conversione al vecchio
esempio path/value, migrazione, dipendenza nuova, modifica a setup/avvio o accesso
al database reale. Nessun nuovo scaffold o modifica delle risorse.

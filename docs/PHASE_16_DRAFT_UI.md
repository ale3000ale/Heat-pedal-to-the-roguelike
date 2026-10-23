# Fase 16 - Bozza e salvataggio UI admin

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Sorgente generale: PHASE_16_ADMIN_SAVE_API.md. Nessun merge.

## Stato implementato

c950510 collega carte e sessione locale. Cinque sezioni, tre contenitori del
pilota separati dalle due pool, mazzo N/15 per copie e pool assente distinta da
vuota. Le operazioni ricalcolano dalla baseline e non la mutano; errori locali
separati da quelli REST. Ripristino locale, ritorno, chiusura e navigazione
richiedono protezione prima dello scarto.

Client PUT 549e83e/f95c915 e piano 024d47a/ad377d4 sono collegati alla UI da
9769dd5, formattato in 7d449cb. Riepilogo per clic, conferma unica e consumo
della proposta prima della rete; durante conferme o richieste sono bloccati
modifica carte, ritorno e chiusura ordinaria. Su successo nuova baseline dallo
snapshot PUT senza GET. Errori conservano la bozza; conflitti/esiti incerti
bloccano altri invii. Rilettura esplicita con scarto solo dopo risposta utilizzabile.

## Riscontri e limite documentale

CI 40012639610 su 7d449cb: frontend (check, lint, test, build), backend e
migrazioni riusciti. Il job documentale e' fallito per il titolo incompatibile
del sorgente, non per il codice applicativo. La correzione ripristina il titolo
stabile e ricava la riga di stato dal sorgente. Propagazione ancora da verificare.
Nessuna esecuzione npm o browser locale in questo riallineamento.

## Da completare

Live tramite SSE condiviso e collaudo browser: annullamento, doppi clic, 409,
rete incerta, 422, rilettura fallita, Escape, chiusura/ritorno durante rete e
risposte tardive. Test di client, piano e sessione non equivalgono a test DOM
del flusso UI. Nessun autosalvataggio, polling, stream aggiuntivo, migrazione
o dipendenza nuova. Fase non completa. Per i soli docs non attendere nuovi
test applicativi; verificare separatamente la propagazione documentale.

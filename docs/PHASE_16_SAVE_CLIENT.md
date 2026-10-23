# Fase 16 - Salvataggio PUT nella UI admin

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Sorgente generale: PHASE_16_ADMIN_SAVE_API.md. Nessun merge.

## Contratto e collegamento

Client 549e83e, formattato in f95c915; piano 024d47a, formattato in ad377d4.
Richiesta con versioni iniziali di tutti i cinque contenitori e trasferimenti
source/path, senza destinazioni client. Solo le pool possono essere null.
Il piano ignora anteprime alterate, ricalcola dal registro e produce una riga
per clic, non differenze nette. Nessuna applicazione parziale agli input.

9769dd5 e il formatter 7d449cb collegano il flusso tramite
admin-pilot-cards-save-controls.svelte. Riepilogo senza invio; Annulla, X,
Escape e sfondo non fanno PUT. Conferma consuma la proposta e blocca prima
del primo await; sessione diversa richiede nuovo riepilogo. Nessun retry.
Conferme e richieste propagano il blocco fino alle impostazioni. Una chiusura
forzata del browser non annulla una scrittura gia' inviata. Risposte tardive
di componenti dismessi o sessioni sostituite vengono ignorate.

Successo: sessione nuova da snapshot PUT e versioni server, senza GET automatica.
Errore: bozza conservata; 422 consente azioni manuali, altri errori bloccano
nuovi invii fino a rilettura. 401/403/404/409 sono rifiuti/conflitti, gli altri
esiti non verificati. Client controlla contesto e creazione della sessione
controlla carte: non e' una validazione completa runtime del DTO.
Rilettura esplicita, con conferma se pendente: scarto solo dopo risposta
utilizzabile, non su errore. Ripristino locale conserva il blocco.

## Verifiche effettive

CI 40012639610 su 7d449cb: frontend (check, lint, test, build), job
120622516434, backend e migrazioni riusciti. Job documentale 120623536970
fallito per intestazione del sorgente diversa dal contratto; non confondere
questo errore con test applicativi falliti o dichiarare la CI tutta verde.
La correzione documentale ripristina il titolo e deriva lo stato della tabella
dal sorgente, mantenendo controlli e protezioni. Sette test Python della
trasformazione su fixture temporanee riusciti; non e' un workflow GitHub locale.
Propagazione sui dieci documenti ancora da verificare dopo il commit.

## Limiti

Non sono stati eseguiti nuovi test DOM o browser. Restano casi di annullamento,
doppi clic, successo, conflitto, rete incerta, 422, rilettura fallita, Escape,
chiusura/ritorno durante rete e risposte tardive. Restano live e collaudo della
fase; nessun autosalvataggio, polling o nuovo stream SSE. Nessuna modifica
applicativa, migrazione, dipendenza o accesso al database reale in questa
correzione documentale. Dopo pubblicazione verificare propagazione, senza
attendere nuovi test applicativi per i soli aggiornamenti docs. Fase non completa.

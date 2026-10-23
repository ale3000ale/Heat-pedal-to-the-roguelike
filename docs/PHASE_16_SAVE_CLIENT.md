# Fase 16 - Salvataggio admin: contratto, riepilogo e live

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Sorgente: PHASE_16_ADMIN_SAVE_API.md. Nessun merge autorizzato.

## Contratto e preparazione

Client saveAdminPilotCards tramite api.ts, con ID verificati e cookie del
trasporto comune. Richiesta versions per tutti i contenitori e transfers
source/path; soltanto le pool possono essere null. Validazione autorevole nel
backend, non sostituita dai tipi TypeScript. Nessun retry di scrittura.

prepareAdminCardSave usa versioni della baseline, non quelle dell'anteprima;
ricalcola tutti i trasferimenti e non muta input su errore tardivo. Il riepilogo
effettivo accorpa quantita' e compensa versi opposti inventario/pool con la
stessa identita' e immagine. Non cambia la sequenza PUT o inventa un movimento
diretto mazzo/inventario. Il modal include pilota, username e nuovo N/15.
Nessuna proposta di invio se non restano variazioni effettive.

Conferma consuma una proposta una sola volta, prima dell'await; proposta
invalidata richiede nuovo riepilogo. Successo: nuova sessione dallo snapshot
PUT e versioni server. Errori conservano la bozza; 422 consente nuove azioni
manuali, altri errori bloccano nuovi invii fino a rilettura. Errore di rete o
AdminCardSaveResponseError non provano rollback. Il client controlla contesto
e la creazione della sessione valida carte, non ogni campo runtime del DTO.

## Coordinamento live

Conferme aperte distinte dalle richieste HTTP: eventi prima dell'invio possono
invalidare la proposta; durante PUT/GET i segnali attendono e non sostituiscono
la sessione della richiesta. Un evento pendente puo' generare una GET live dopo
il PUT; nessuna GET di conferma incondizionata o retry di scrittura.
Il coordinatore condiviso accorpa letture e scarta risultati obsoleti. Solo uno
snapshot server utilizzabile accettato esplicitamente libera i blocchi.
Rileggi dal server conferma lo scarto se pendente e conserva la bozza su errore.
Reset locale conserva i blocchi. Cambio contesto/utente/ruolo e scadenza
inibiscono aggiornamenti tardivi; nessuna chiusura dello stream condiviso.

## Esiti e limiti

CI 40026443509 riuscita su 2366d1d: frontend (check, lint, test, build), backend,
migrazioni su DB di test e riallineamento documentale. Non sono nuovi test
locali; conteggi complessivi e warning non letti dai singoli log.
Riscontro dell'autore del 2026-10-23, 23:59 CEST: «sembra funzionare tutto»,
positivo nel complesso dopo la checklist, non un protocollo caso per caso.
Non attestare singolarmente doppi invii, rete incerta, concorrenza reale,
privacy o tutti i percorsi di errore senza risultati specifici.

Questo aggiornamento e' solo documentale, successivo al codice come richiesto.
Propagazione sui dieci documenti generali da verificare dopo pubblicazione,
senza attesa di nuovi test applicativi per i soli docs. Nessuna migrazione,
dipendenza nuova, accesso al DB reale dell'assistente, merge o ZIP finale.

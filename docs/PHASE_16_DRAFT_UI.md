# Fase 16 - UI admin, bozza e live

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Sorgente: PHASE_16_ADMIN_SAVE_API.md. Nessun merge autorizzato.

## Perimetro implementato

Piloti nelle impostazioni campionato solo admin, nome e username, pulsante Carte
accessibile. Cinque sezioni apribili con immagini: mazzo N/15, due inventari e
due pool separati. Pool assente distinta da vuota. Una copia per clic nelle sole
direzioni approvate, nessun passaggio diretto pool/mazzo o sponsor/mazzo.

Salva in fondo a destra; modal testuale con pilota, username, nuovo N/15 e
variazioni effettive accorpate. Movimenti opposti compensati nel solo riepilogo;
registro PUT originale in ordine. Senza differenze non si propone la PUT.
Annullamento senza scritture, conferma unica, protezione dai doppi invii e
dallo scarto non confermato. Errori conservano la bozza e conflitti/esiti
incerti bloccano nuovi invii fino a una rilettura esplicita utilizzabile.

Live collegato al pannello mediante client SSE e coalescer condivisi, senza
nuovo stream o polling. Conferme e richieste HTTP distinte: invalidazione
della proposta prima dell'invio e differimento dei segnali durante PUT/GET.
Bozza mai sostituita da una GET live incompatibile; reset locale non sblocca
un'invalidazione remota. Utente/ruolo e contesto sorvegliati, cleanup dei soli
listener propri, risultati obsoleti ignorati. Stato trasporto non equivale
a dati aggiornati. Nessun autosalvataggio o notifica regalo per movimenti admin.

## Verifiche finali

Candidato 2366d1de37cf1cf638b45c55313a3e31601eebff. CI 40026443509 riuscita:
frontend (check, lint, test, build), backend, migrazioni su DB di test e job
documentale. Conteggi globali e warning non letti dai singoli log; nessuna
nuova esecuzione locale o prova browser dell'assistente dichiarata.

Il 2026-10-23 alle 23:59 CEST, dopo checklist e via libera sul candidato,
l'autore riferisce «sembra funzionare tutto»: riscontro manuale complessivo
positivo, senza esiti per singolo caso, browser/dispositivo o log. I casi
avanzati non diventano automaticamente OK. Dettagli e limiti nel sorgente.

## Documenti e stato di consegna

Riallineamento conclusivo preparato dopo codice e verifiche; propagazione nei
dieci documenti generali ancora da verificare sul nuovo commit. Per i soli
docs non attendere nuovi test applicativi. Nessun nuovo codice, dato,
dipendenza, migrazione, merge o ZIP finale in questo aggiornamento. PR in bozza.

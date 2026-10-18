# Fase 14 — Sistemazione generale e miglioramenti

Ultimo aggiornamento: 2026-10-18

Documento di fase da accorpare in `PROJECT_STATUS.md`, `PROJECT_SPEC.md` e `README.md`.

## Stato

- Ramo: `phase-14`, creato da `main` (commit `55c2a9a`).
- Pull request: #13, in bozza, non unita a `main`.
- Regola: nessun merge senza richiesta esplicita dell'autore.

## Righe per PROJECT_STATUS.md

| Fase | Contenuto | Stato |
|---|---|---|
| 14 | Sistemazione generale, modifiche di vivibilità e miglioramenti | In corso nel ramo `phase-14` (pull request #13 in bozza, non unita a `main`) |
| 14a | Frontend: pagina Campionati con tre sezioni a scomparsa "Iscritto", "Attivi" e "Chiusi" | Completata nel ramo `phase-14` (commit `bed217f` e `f63510a`; CI verde, riferita dall'autore il 2026-10-18) |
| 14b | Frontend: iscrizione di un pilota dal dettaglio del campionato in una finestra a due passi (scelta e conferma) | Completata nel ramo `phase-14` (commit `8a575a7`; CI verde, riferita dall'autore il 2026-10-18) |

## 14a — Campionati con sezioni a scomparsa

Regole richieste dall'autore:

- "Iscritto": campionati attivi con almeno un pilota dell'utente loggato (anche per l'admin).
- "Attivi": gli altri campionati attivi, senza ripetere quelli già in "Iscritto".
- "Chiusi": tutti i campionati chiusi, anche quelli a cui l'utente partecipava.
- All'apertura della pagina è aperta solo "Iscritto" se c'è almeno un pilota iscritto, altrimenti solo "Attivi"; poi l'utente apre e chiude le sezioni liberamente.
- Le sezioni vuote restano visibili con il messaggio "Nessun campionato…".

File:

- `frontend/src/lib/championship-groups.ts`: logica che divide i campionati nelle tre sezioni e sceglie quella aperta.
- `frontend/src/lib/championship-groups.spec.ts`: 7 test Vitest.
- `frontend/src/routes/championships/+page.svelte`: pagina con tre elementi `<details>` e conteggio.

Dati: `GET /api/championships` e `GET /api/pilots` (solo i piloti dell'utente loggato). Backend, database, migrazioni e CI non sono stati modificati.

Commit: `bed217f` (funzione) e `f63510a` (formattazione Prettier).

Verifiche: CI verde sulla pull request #13, riferita dall'autore e non letta dall'assistente. L'assistente non ha eseguito controlli in locale.

Limite noto: `GET /api/pilots` restituisce al massimo 100 piloti per richiesta; con più piloti la sezione "Iscritto" potrebbe essere incompleta.

Da verificare a mano: apertura iniziale delle sezioni, comportamento per admin e giudice, sezioni vuote.

## 14b — Iscrizione del pilota in una finestra

Regole richieste dall'autore:

- La card "Iscrivi un tuo pilota" del dettaglio campionato diventa un pulsante "Iscrivi un pilota" nell'intestazione, accanto a "Negozio", che apre una finestra.
- Il pulsante c'è solo in un campionato attivo in cui l'utente non ha ancora piloti iscritti: sparisce nei campionati chiusi e in quelli dove ha già un pilota iscritto.
- La finestra ha due passi: prima si sceglie il pilota, poi si conferma. La conferma avvisa che l'iscrizione reimposta inventari, mazzo da gioco, oro, sponsor e punti.
- I piloti proposti hanno un team e non sono iscritti a nessun campionato attivo (anche a un altro).
- Senza piloti iscrivibili la finestra mostra "Nessun tuo pilota può essere iscritto.".
- Gli errori del backend (per esempio 409) compaiono nella finestra.
- Dopo l'iscrizione la pagina ricarica il campionato, la classifica e l'elenco dei piloti dell'utente.

File:

- `frontend/src/lib/enroll-candidates.ts`: `enrollablePilots` (piloti iscrivibili) e `canShowEnroll` (visibilità del pulsante).
- `frontend/src/lib/enroll-candidates.spec.ts`: 8 test Vitest.
- `frontend/src/lib/components/enroll-pilot-dialog.svelte`: la finestra a due passi, basata su `modal.svelte`.
- `frontend/src/routes/championships/[id]/+page.svelte`: pulsante, finestra e ricarica dei dati.

Dati: `POST /api/championships/{id}/pilots` e `GET /api/pilots`. Backend, database, migrazioni e CI non sono stati modificati.

Commit: `8a575a7`.

Verifiche: CI verde sulla pull request #13, riferita dall'autore e non letta dall'assistente. L'assistente non ha eseguito controlli in locale.

Limiti noti:

- Con un pilota già iscritto non si possono aggiungere altri piloti allo stesso campionato dalla pagina (scelta dell'autore).
- `GET /api/pilots` restituisce al massimo 100 piloti per richiesta: con più piloti l'elenco dei candidati potrebbe essere incompleto.

Da verificare a mano: i due passi della finestra, l'errore del backend, il pulsante nei campionati chiusi e in quelli con un pilota iscritto.

## Da riallineare nel weekend

- `PROJECT_STATUS.md`: righe 14, 14a e 14b e una voce nella sezione Frontend per ciascuna (il file è troppo lungo per la lettura dell'assistente).
- `PROJECT_SPEC.md`: sezioni dei campionati e dell'iscrizione dei piloti (non letto dall'assistente).
- `README.md`: da controllare se descrive la pagina Campionati (non letto dall'assistente).

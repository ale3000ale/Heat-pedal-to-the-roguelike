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

## Da riallineare nel weekend

- `PROJECT_STATUS.md`: righe 14 e 14a e una voce nella sezione Frontend (il file è troppo lungo per la lettura dell'assistente).
- `PROJECT_SPEC.md`: sezione dei campionati (non letto dall'assistente).
- `README.md`: da controllare se descrive la pagina Campionati (non letto dall'assistente).

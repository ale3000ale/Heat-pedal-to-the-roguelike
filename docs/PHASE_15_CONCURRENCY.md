# Fase 15a-3 - Test concorrenti su file SQLite

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md, PHASE_15_TIMER.md e PHASE_15_RACE_EVENTS.md.

## Base verificata

CI del commit 39572e3 tutta verde: backend, migrazioni e frontend
(run 39403393864). Il percorso Termina gara e gli eventi risultati sono pubblicati.

## Nuovo test

backend/tests/test_review_concurrency.py prepara una revisione scaduta con una
carta giocata usando lo scenario sintetico esistente. Copia il database in memoria
della fixture su un file dentro tmp_path con sqlite3.backup; non usa heat.db reale.

Due processi Python spawn hanno engine e connessioni indipendenti allo stesso
file, foreign_keys attivo e timeout SQLite. Una barriera prima del lock porta
entrambi allo stesso punto critico, senza sostituire il blocco BEGIN IMMEDIATE.

Casi: scadenza contro scadenza; scadenza contro conferma manuale admin.
Attese limitate e pulizia dei processi in finally. Un errore del figlio produce
un traceback nel risultato del test. Il test verifica una sola chiusura riuscita,
una sola copia consumata/restituita e una sola coppia di eventi dopo la baseline.

## Stato e limiti

Test scritto ma non eseguito localmente: esito CI da leggere dopo il push.
Non e' una prova di carico, di proxy o di due server HTTP reali. Verifica i servizi
in processi distinti sullo stesso file SQLite; non altri database o filesystem di rete.
Nessun codice applicativo, migrazione, dipendenza o database reale modificati.
Timer ancora non attivo; aggancio al lifespan soltanto dopo questi controlli.
Restano eventi delle carte, frontend/fallback, verifiche browser e riallineamento
finale dei documenti piccoli. PROJECT_SPEC.md e PROJECT_STATUS.md restano intatti.

# Iscrizioni live - fix e conferma autore

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Stato: implementato, verificato in CI e funzionamento confermato dall'autore.
Nessun merge o intervento sui dati reali autorizzato.

## Cronologia e verifiche

Segnalazione 22:39 CEST: nuove iscrizioni visibili alle altre sessioni solo dopo
reload. Precisazione 22:41: sia utenti iscritti sia osservatori autenticati non
iscritti gia' sulla pagina. Preparazione a442095; bot
12261725bc3439cd3e593fda152e050563b0988f alle 22:58:37 CEST del 2026-10-21.

CI ordinaria 39674942800 sulla nuova testa tutta verde:
- Migrazioni database di test: 23:00:16 CEST.
- Frontend check/lint/test/build: 23:00:48 CEST.
- Backend pytest: 23:02:07 CEST.

Letti esiti e nove file modificati; nessun log completo o totale suite inventato.
Workflow ha eseguito intera suite backend e controlli frontend prima del bot.
Nessun npm/pytest locale o DB reale usato dall'assistente.

Alle 23:24 CEST, dopo richiesta di riprova per membri e osservatori, autore:
"funziona". Riscontro positivo complessivo riferito al fix iscrizioni; non comunicati
log, commit locale, browser o risultati separati dei due scenari. Non si attribuiscono
per questo PASS ai casi precedenti non verificati.

## Implementazione e privacy

Prima enroll_pilot non emetteva eventi e la pagina rileggeva soltanto il client
del POST. Ora registra championship.pilots_changed nella stessa transazione di
iscrizione/reset, con rollback comune e nessun evento su iscrizione rifiutata.
Envelope con ID campionato, pilot_id nullo, payload vuoto e nessun destinatario
privato. Validazione Pydantic e frontend rifiuta dettagli o riferimenti aggiuntivi.

Solo questo segnale pubblico canonico raggiunge tutti gli autenticati: per gli
osservatori la query richiede anche pilot_id nullo e payload serializzato {}.
Righe malformate non allargano l'eccezione; carte, giocate, regali privati e altri
eventi conservano i filtri precedenti. Sessione HTTP verificata a ogni ciclo.
Frontend registra il nuovo tipo e rilegge tramite la coda esistente le REST gia'
autorizzate. Nessun nome/conteggio/carta nel segnale, polling di sicurezza, secondo
stream o ack automatico. Pagina e regole di iscrizione/reset invariate.
API HTTP e modello SQL invariati; contratto Pydantic/TS esteso senza migrazioni.

Test coprono membri/osservatori, frame minimo e replay, assenza accesso anonimo,
privacy e segnali malformati, rifiuti iscrizione, rollback completo, schema/parser
e aggiornamento frontend senza POST/ack. Test sintetici, non esecuzione browser
indipendente dell'assistente. La conferma browser e' il riscontro autore sopra.

## Collaudo generale e limiti

Autore alle 22:39: 1/4/5/6/7/9 PASS, 2/3 non verificabili, 8/10 non eseguiti.
Conferma del fix non estesa a questi ultimi quattro. Checklist e riepilogo
riallineati nello stesso aggiornamento solo .md, senza attesa CI documentale.

Nessun nuovo cambiamento funzionale, merge, produzione, migrazione reale o fase
15b automaticamente autorizzati. Vulnerabilita' npm e altri pendenti non risolti
qui. PROJECT_SPEC.md/PROJECT_STATUS.md intatti. Nessun dato reale modificato.

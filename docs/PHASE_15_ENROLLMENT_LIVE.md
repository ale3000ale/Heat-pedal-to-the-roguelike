# Collaudo ricevuto e iscrizioni live

Stato fix: applicato; suite backend completa e formatter/lint/check/test/build frontend riusciti prima del commit bot.
Solo phase-15-sse-sistemazione, PR 14 in bozza. Nessun merge o modifica ai dati reali.

## Riscontro autore

2026-10-21 alle 22:39 CEST: casi 1, 4, 5, 6, 7, 9 PASS; 2 e 3 non verificabili;
8 e 10 non eseguiti. Sei PASS, non dieci. Commit locale, browser e dispositivo non
comunicati: esiti dichiarati dall'autore, non riprodotti dall'assistente. Nessun
caso saltato convertito in PASS. Segnalazione aggiuntiva: pilota iscritto non
compare alle altre sessioni fino al reload. Alle 22:41 confermato sia per iscritti
sia per osservatori autenticati non iscritti che visualizzano il campionato.

## Causa e perimetro

Pagina campionato rilegge solo il proprio client dopo POST. enroll_pilot non emette
un evento; read_events limita gli altri pubblici ai membri o ad admin/giudici.
Contratto precedente non estendeva SSE alle iscrizioni: richiesta ora esplicita.

Nuovo tipo championship.pilots_changed. Envelope con ID campionato, pilot_id nullo,
payload vuoto, nessun destinatario privato. Validazione backend e frontend vieta
riferimenti pilota o payload aggiuntivi. Evento nella medesima transazione di
iscrizione/reset: rollback comune, nessuna emissione per iscrizione rifiutata.

Solo questo segnale pubblico canonico e' leggibile da tutti gli utenti autenticati,
come il dettaglio REST del campionato. Per gli osservatori la query richiede anche
pilot_id nullo e payload serializzato {}: righe malformate non aprono l'eccezione.
Carte, giocate, regali privati e altri eventi pubblici conservano i filtri precedenti.
Non e' un ampliamento generale della visibilita' SSE. Sessione HTTP sempre verificata.

Il client registra il nuovo tipo tramite il registro esistente; startChampionshipLive
invalida la coda gia' presente per il campionato e rilegge dettaglio/classifica/gare
ed esclusivamente i dati privati propri autorizzati. Nessun evento contiene nomi,
conteggi, carte o bozze; nessun polling di sicurezza, secondo stream o ack automatico.
Pagina e regole di iscrizione/reset invariate. API HTTP e modello SQL non modificati;
contratto Pydantic/TypeScript esteso, nessuna migrazione necessaria nel modello letto.

## Test e pubblicazione

Workflow vincola sette sorgenti esistenti, crea test backend e aggiorna due suite
frontend. Verifiche: consegna a iscritti e osservatori, frame minimo e replay,
assenza accesso anonimo, isolamento degli altri eventi/privati e di segnali
malformati, rifiuti di iscrizione, rollback di reset/iscrizione/evento, schema
restrittivo, parser e rilettura frontend senza POST/ack. Riutilizza fixture SQLite
sintetiche e comandi della CI corrente. Intera suite backend e lint/check/test/build
frontend prima di pubblicare gli otto codice/test e questa nota. Niente force push
se la testa cambia. Nessun comando locale o DB del gioco usato dall'assistente.

Dopo riuscita leggere bot/diff/CI ordinaria e riallineare riepilogo, nota campionato
e checklist con gli esiti sopra. Poi riprovare una nuova iscrizione con versione
corretta caricata: sessione gia' iscritta e sessione autenticata non iscritta devono
aggiornarsi senza reload manuale successivo all'iscrizione. Questi due nuovi casi
sono ancora da eseguire, non risultano PASS dal collaudo precedente.

Nessuna produzione, migrazione reale o merge autorizzati. Casi 2/3/8/10 ancora
non verificati, vulnerabilita' npm e altri pendenti non risolti da questo fix.
PROJECT_SPEC.md e PROJECT_STATUS.md intatti. Solo dopo controlli riusciti riallineare
le altre note; non attendere CI dei soli .md.

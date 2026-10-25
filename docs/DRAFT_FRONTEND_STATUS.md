# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Correzione corrente: controllo mazzi dopo la modifica

Segnalazione dell'autore alle 13:55: il requisito delle 15 carte non deve bloccare Avanti dopo Presenti/Assenti. Il controllo anticipato era in backend/app/services/draft_commands.py, confirm_attendance, tramite require_ready_game_decks per le gare successive alla prima.

La correzione rimuove soltanto quella chiamata e il relativo import. Restano verifiche di fase, creatore, versione, numero dei presenti 1-12, proprietari, riferimenti ai mazzi e pool. La conferma presenze porta a order o direttamente a decks secondo la pool, senza richiedere mazzi gia completi. Non viene modificata la validazione dei dati JSON.

Il controllo sui mazzi modificati resta nel comando READY e nel ricontrollo di tutti i presenti prima di creare Race. Dalla seconda gara servono 15 carte esatte; alla prima resta l'eccezione del conteggio esatto e il massimo di 15. Spostamenti, annullamento, snapshot, transazioni e segnali SSE restano quelli esistenti. Non vengono modificati ready_pilot, set_ready o il percorso Gara gia disputata.

File previsti: backend/app/services/draft_commands.py, nuovo backend/tests/test_draft_attendance_readiness.py, docs/DRAFT_SPEC.md e questo documento. Il precedente tentativo di conferma con segnaposto non e stato eseguito e non ha pubblicato file.

## Regressioni predisposte e verifiche

Nuove regressioni SQLite temporanee: precedente gara con risultati e revisione chiusa; presenze accettate con mazzo vuoto o da 14 copie sia con pool sufficiente sia insufficiente; nessuna modifica dei mazzi alla conferma presenze; percorso fino a decks, READY rifiutato a 14 e accettato dopo spostamento a 15; nuova gara assente fino a READY; endpoint HTTP conferma-presenze e permanenza del vincolo di almeno un presente.

Non sono stati eseguiti pytest, controlli frontend, installazioni, migrazioni o collaudo browser per questa correzione. Nessuna CI consultata o attesa in questo passaggio. Test predisposti, non dichiarati superati.

Ultima verifica CI letta nella conversazione sul commit 26c5faabd4427f790dbdab0cf367cce7466829c6: frontend check/lint/test/build, runtime e migrazioni superati; backend pytest ancora in esecuzione a quella lettura. Sono risultati precedenti, non della patch attuale. Il vecchio log 594/596 e il fix fc71aa6ce50501f8c9b18e8a9ecacf90b2b004fb restano storia del precedente errore SSR, non un risultato nuovo.

Comandi da verificare dopo il push: in backend python -m pytest -q tests/test_draft_attendance_readiness.py tests/test_draft_commands.py tests/test_draft_completion.py tests/test_draft_api.py tests/test_draft_transitions.py; poi suite backend completa, check/lint/test/build frontend e controlli migrazioni gia previsti dalla CI. Nessun risultato anticipato.

## Integrazione conservata

Registro/auth: 48d59990c538db6e4c779e557126834be722e90b. Host/layout: 2739251d889e821e39a1a407eef56232a95710ba. SSE condiviso: e8daa23d8de734abfca9b72cddf9779e190111b0. Modulo apertura/test: 131612d667d132c23f9093ae9cec1d200fc33e30. Collegamento pagina Nuova Gara: 16eb2df83e3fcca1239b70a83b8bc07d6720bb29.

Nuova Gara apre la preparazione tramite il provider del layout, non crea direttamente Race. Un solo stream SSE, draft.changed con solo preparation_id e recupero REST accodato su notifiche/resync. Busy di store/dettagli rinvia il recupero senza ritentare POST. Dettaglio gia caricato ma obsoleto: tentativo GET mirato per coordinatore/pilota/versione, poi recupero manuale. Coda locale stabile, un solo DraftFlow, modal sottostanti inert, Escape non chiude e X del creatore con conferma/vincolo READY.

Rimozione da elenco non viene etichettata automaticamente come creazione o annullamento; esiti effettivi acquisiti prima del cleanup. Nessun redirect o nuovo polling. Recupero multi-store non atomico; conteggi, versioni, permessi e blocchi restano server. Il frontend non viene modificato da questa correzione.

## Limiti e seguito

Nessuna modifica a schema, migrazioni, database reale, risorse, dipendenze, lockfile, script o workflow. Nessun merge o rilascio. Il manifesto backend descrive l'artefatto consolidato originario e non viene falsificato per rappresentare la patch attuale.

Restano verifica della correzione e collaudo reale di gare successive con mazzi incompleti, scelta/modifica, pronto/non Pronto, annullamento e riconnessione. Focus, multi-browser e consegna ZIP finale non dichiarati completati. Dopo esiti effettivi va completato il riallineamento generale della documentazione.

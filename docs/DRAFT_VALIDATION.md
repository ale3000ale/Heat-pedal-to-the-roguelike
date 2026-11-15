# Draft - validazione e chiusura del ciclo funzionale

26 ottobre 2026. Repository Heat-pedal-to-the-roguelike, ramo draft, PR #18 in bozza. Nessun merge in main.

## Base verificata

Commit applicativo: 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a. Il successivo riallineamento e documentale e non cambia il comportamento dell app.

La correzione stabilizza le chiavi del flusso per generazione autenticata e ID preparazione e corregge la proprieta delle risorse: il registro possiede lo store principale, il contesto possiede il coordinatore mazzi e la vista pulisce solo le risorse UI locali.

## Evidenze CI

- [Frontend: check, lint, test e build](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40269135082/job/121397943356): success.
- [Backend pytest](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40269135082/job/121397943569): success.
- [Migrazioni sul database di test](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40269135082/job/121397943562): success.
- [Runtime](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40269135447/job/121397944224): success.

I due job documentali di fase 16 sono skipped per questo ramo; non sono controlli falliti. Non vengono inventati conteggi di test o warning. Il workflow documentale ricontrolla gli ID, lo SHA e le conclusioni prima di aggiornare i file.

## Collaudo riferito dall autore

Alle 05:09 del 26 ottobre l autore ha segnalato ancora riduzione dello zoom, reset dei mazzi e ritorno alla scelta iniziale quando escludeva un pilota. Le precedenti patch di layout, focus e scroll non erano quindi una soluzione verificata.

Dopo la correzione lifecycle 8ba03aa1, alle 05:31 l autore ha riferito: "ok ora funziona tutto senza errori" e ha chiesto di passare alla grafica. Questo riscontro chiude positivamente il ciclo delle segnalazioni UI nel collaudo riferito. Non equivale a una prova browser eseguita dall assistente, a una matrice completa mobile/desktop o alla verifica indipendente di ogni criterio della specifica.

## Regole e dati preservati

La specifica funzionale resta [DRAFT_SPEC.md](DRAFT_SPEC.md). Il controllo delle 15 carte non torna alle presenze: si applica dopo modifica del mazzo ai READY e nel ricontrollo finale, con eccezione della prima gara e massimo gia previsti. Nessuna nuova migrazione o operazione sul DB reale eseguita da questo riallineamento.

La provenienza backend in DRAFT_BACKEND_MANIFEST.json resta storica e non descrive gli hash di tutte le correzioni successive. Gli errori precedenti di lint e tipi restano nella cronologia, non come stato corrente.

## Stato successivo

Il 26 ottobre alle 17:29 l autore ha richiesto prima il riallineamento dei documenti. Le modifiche grafiche non sono ancora definite o iniziate. Altre fasi, domande aperte, release, ZIP finale e merge non sono chiusi o autorizzati automaticamente da questo checkpoint.

Questo documento e i blocchi correnti nei documenti generali separano risultati CI, collaudo riferito e limiti residui. Nessun nuovo test locale dell applicazione eseguito per il solo riallineamento.

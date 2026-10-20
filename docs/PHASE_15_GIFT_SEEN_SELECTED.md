# Fase 15 - API di conferma selettiva delle notifiche regalo

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14 in bozza.
Prerequisito ID: aa1a4c7 e migrazione d6f0a4b8c2e7 verificati in CI 39467182291.
Riallineamento base 21136eb verificato in CI 39468896207. Nessun merge autorizzato.

## Contratto

POST /api/championships/{championship_id}/card-gifts/seen-selected
Corpo JSON: {"pilot_id": 1, "gift_ids": [10, 11]}.
Risposta 204 senza corpo. Cookie di sessione obbligatorio: 401 senza sessione.
Schema strict, campi extra vietati, ID interi positivi entro int64 SQLite.
Lista obbligatoria non vuota, massimo tecnico 100 elementi per richiesta,
per limitare dimensione delle query IN; duplicati ignorati. Input non valido: 422.
Il futuro frontend dovra' suddividere selezioni piu' grandi in batch per pilota.

Il campionato deve esistere e il pilota deve appartenere all'utente ed essere
non eliminato. Per i casi non trovati/non propri: 404 generico, anche per
admin e giudice che non possiedono il pilota. Nessun potere di conferma altrui.
La query verifica insieme pilot_id e campionato della gara di ogni notifica.
ID non presenti, annullati, gia' visti o fuori ambito sono ignorati: nessun
aggiornamento e nessuna rivelazione dell'esistenza di notifiche altrui.
Il campionato puo' essere chiuso: compatibile con la conferma di notifiche
storiche, senza richiedere iscrizione attuale o una gara in corso.

Solo seen_at delle notifiche selezionate ancora non viste viene modificato,
nella stessa transazione sotto il lock SQLite gia' usato dal progetto.
Conferme ripetute mantengono la prima data seen_at; nessun timestamp riscritto.
Nessun trasferimento di carte, evento SSE, modifica del saldo o dell'inventario.
L'endpoint precedente /card-gifts/seen e il frontend restano invariati.
L'API verifica autorizzazione e ambito, non puo' dimostrare che il browser abbia
realmente mostrato la notifica: la lista corretta e' responsabilita' del client.

## File e verifiche

Nuovi schemas/card_gift_seen.py, services/card_gift_seen.py e api/card_gift_seen.py.
main.py aggiunge soltanto import e include_router, senza cambiare il lifespan.
Nuovi test_card_gift_seen_selected.py: sottoinsieme/new gift dopo lettura,
idempotenza, annullo seguito da nuovo regalo, ambito pilota/campionato,
permessi, input strict/batch, rollback dopo flush e compatibilita' legacy.
Il caso regalo nuovo dopo lettura e' una sequenza API deterministica, non una
prova concorrente a piu' processi; non vengono dichiarate prove di carico.

Nessun test o comando locale eseguito. Test preparati, CI nuova da leggere
dopo push; la CI verde della base non certifica queste modifiche.
Nessuna nuova migrazione, dipendenza, modifica a immagini o database reale.
Il DB operativo deve gia' includere d6f0a4b8c2e7: backup verificato e prova su
copia prima di applicarla, nessuna applicazione locale da parte dell'assistente.

## Prossimo passo

Leggere la CI e correggere eventuali errori, poi riallineare documenti di fase
e DATABASE.md con disponibilita' effettiva e risultati. PROJECT_SPEC.md e
PROJECT_STATUS.md restano protetti secondo la decisione della fase.
Solo dopo collegare il frontend: inviare gli ID davvero mostrati, non tutti
i regali non visti; annullamenti remoti non devono invocare conferme automatiche.
Il commit 2 frontend non viene avviato da questo blocco.

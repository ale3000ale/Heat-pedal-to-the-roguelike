# Script — Heat

Ultimo aggiornamento: 2026-10-13

Descrizione dei comandi di `heat.py` (letto il 2026-10-13). Si eseguono dalla radice del repository. Senza argomenti `python heat.py` apre un menu interattivo.

## Comandi

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Menu con sei voci (setup, migrazioni, avvio completo, solo backend, test backend, controlli frontend) e `0` per uscire. Mostra il sistema operativo e la versione di Python rilevati. |
| `python heat.py setup` | Ambiente virtuale, dipendenze, migrazioni, prototipo del mazzo, utente admin, dipendenze frontend. Opzioni: `--skip-admin`, `--skip-seed`. |
| `python heat.py migrate` | Esegue `alembic upgrade head` nell'ambiente `backend/.venv`. |
| `python heat.py start` | Applica le migrazioni, poi avvia backend (127.0.0.1:8000) e frontend (127.0.0.1:5173). Opzione: `--backend-only`. |
| `python heat.py test` | Esegue `python -m pytest -q` in `backend/`. |
| `python heat.py check` | Esegue `node tools/check-frontend.mjs` (format, check, lint e test del frontend, come indicato nel commento dello script). |

## Comportamento comune

- Gli errori fermano il comando con un messaggio che inizia con "ERRORE"; dal menu l'errore viene mostrato e il menu resta aperto.
- `test` e `check` non fermano lo script se falliscono: il codice di uscita dei test non viene propagato come errore di `heat.py`.
- I comandi che usano il backend richiedono `backend/.venv`; se manca indicano di scegliere prima "Setup".
- Su Windows i processi si fermano con `taskkill`, su macOS e Linux con un segnale al gruppo di processi.

## Non verificato

Non ho letto il contenuto di `tools/` (oltre al nome `check-frontend.mjs`), né gli script `app.scripts.seed_prototype`, `app.scripts.create_admin` e `app.scripts.resize_cards`. Non ci sono backup, ripristino, reset o build del frontend: nel ramo non esiste una cartella `scripts` né i file `setup.bat` e `setup.sh`.

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.

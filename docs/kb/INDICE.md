# Indice della knowledge base locale di Heat

Questo indice **collega** la documentazione già esistente: non ne ripete il contenuto e non
definisce nuove regole. Le schede dei sottosistemi sono elencate nell’ultima sezione.
La copertura viene estesa progressivamente secondo i piani approvati.

## Documenti di riferimento (regole e stato corrente)

Fonte autorevole per regole di gioco, mappa del codice e avanzamento:

- [README del progetto](../../README.md) — panoramica e comandi; contiene blocchi marker protetti.
- [Specifiche di gioco](../PROJECT_SPEC.md) — fonte autorevole delle regole.
- [Mappa del codice e regole di lavoro](../PROJECT_NOTES.md) — struttura e convenzioni.
- [Stato del progetto](../PROJECT_STATUS.md) — avanzamento corrente e riferimenti successivi.
- [Domande aperte](../OPEN_QUESTIONS.md) — decisioni non ancora risolte.
- [ChangeLog](../CHANGELOG.md) — versioni e date delle release.

### Documentazione tecnica di supporto

- [Setup](../SETUP.md)
- [Backend: bootstrap](../BACKEND_BOOTSTRAP.md)
- [Backend: autenticazione](../BACKEND_AUTH.md)
- [Frontend: bootstrap](../FRONTEND_BOOTSTRAP.md)
- [Frontend: autenticazione](../FRONTEND_AUTH.md)
- [Database](../DATABASE.md)
- [Analisi del database](../DATABASE_ANALYSIS.md)
- [Schema shop](../SHOP_SCHEMA.md)
- [Progettazione shop](../SHOP_DESIGN.md)
- [Script e strumenti](../SCRIPTS.md)
- [LAN di produzione](../PRODUCTION_LAN.md)
- [Impostazioni account](../ACCOUNT_SETTINGS.md)
- [Draft: specifiche](../DRAFT_SPEC.md)
- [Draft: validazione](../DRAFT_VALIDATION.md)
- [Stato frontend draft](../DRAFT_FRONTEND_STATUS.md)

## Documenti storici (note di fase — non requisiti)

I documenti seguenti sono cronaca delle fasi di sviluppo. Vanno consultati per capire
l'evoluzione, **non** come requisiti né come stato attuale: in caso di contraddizione
prevalgono i documenti di riferimento indicati sopra.

### Fase 16

- [Stato fase 16](../PHASE_16_STATUS.md)
- [Specifiche fase 16](../PHASE_16_SPEC.md)
- [Save client fase 16](../PHASE_16_SAVE_CLIENT.md)
- [UI draft fase 16](../PHASE_16_DRAFT_UI.md)
- [Allineamento fase 16](../PHASE_16_ALIGNMENT.md)
- [Formattazione fase 16](../PHASE_16_FORMATTING.md)
- [API admin lettura fase 16](../PHASE_16_ADMIN_READ_API.md)
- [API admin salvataggio fase 16](../PHASE_16_ADMIN_SAVE_API.md)

### Fase 15

- [Panoramica fase 15](../PHASE_15.md)
- [Implementazione fase 15](../PHASE_15_IMPLEMENTATION.md)
- [Concorrenza](../PHASE_15_CONCURRENCY.md)
- [Database](../PHASE_15_DATABASE.md)
- [Chiusura](../PHASE_15_CLOSURE.md)
- [CI fix](../PHASE_15_CI_FIX.md)
- [Timer](../PHASE_15_TIMER.md)
- [Eventi di stato](../PHASE_15_STATE_EVENTS.md)
- [Correzione eventi di stato](../PHASE_15_STATE_EVENTS_FIX.md)
- [Servizio](../PHASE_15_SERVICE.md)
- [Browser checklist](../PHASE_15_BROWSER_CHECKLIST.md)
- [Carta giocata: eventi](../PHASE_15_CARD_PLAY_EVENTS.md)
- [Campionato live](../PHASE_15_CHAMPIONSHIP_LIVE.md)
- [Enrollment live](../PHASE_15_ENROLLMENT_LIVE.md)
- [Eventi legacy](../PHASE_15_LEGACY_EVENTS.md)
- [Regia: eventi](../PHASE_15_JUDGE_EVENTS.md)
- [Eventi live](../PHASE_15_RACE_EVENTS.md)
- [Gara live](../PHASE_15_RACE_LIVE.md)
- [Riconciliazione risultato gara](../PHASE_15_RACE_RESULT_RECONCILE.md)
- [Regalo: eventi](../PHASE_15_GIFT_EVENTS.md)
- [Regalo: migrazione ID](../PHASE_15_GIFT_ID_MIGRATION.md)
- [Regalo: controller popup](../PHASE_15_GIFT_POPUP_CONTROLLER.md)
- [Regalo: seen/selected](../PHASE_15_GIFT_SEEN_SELECTED.md)
- [Frontend: client](../PHASE_15_FRONTEND_CLIENT.md)
- [Frontend: formattazione](../PHASE_15_FRONTEND_FORMATTING.md)
- [Frontend: servizio regalo](../PHASE_15_FRONTEND_GIFT_SERVICE.md)
- [Frontend live](../PHASE_15_FRONTEND_LIVE.md)
- [Riconciliazione inventario review](../PHASE_15_REVIEW_INVENTORY_RECONCILE.md)
- [Review: eventi](../PHASE_15_REVIEW_EVENTS.md)
- [Review: lifecycle canvas](../PHASE_15_REVIEW_LIFECYCLE_CANVAS.md)
- [Review: connessione live](../PHASE_15_REVIEW_LIVE_CONNECT.md)
- [Review: guard sessione](../PHASE_15_REVIEW_SESSION_GUARD.md)

### Fase 14

- [Panoramica fase 14](../PHASE_14.md)
- [Validazione fase 14](../PHASE_14_VALIDATION.md)
- [API review](../PHASE_14_REVIEW_API.md)
- [Commit review](../PHASE_14_REVIEW_COMMIT.md)
- [Expiry review](../PHASE_14_REVIEW_EXPIRY.md)
- [Frontend review](../PHASE_14_REVIEW_FRONTEND.md)
- [Migrazione review](../PHASE_14_REVIEW_MIGRATION.md)
- [Piano review](../PHASE_14_REVIEW_PLAN.md)
- [UI review](../PHASE_14_REVIEW_UI.md)
- [Post-merge](../PHASE_14_POST_MERGE.md)
- [Formattazione fase 14](../PHASE_14_FORMATTING.md)
- [Automazione formattazione](../PHASE_14_FORMATTING_AUTOMATION.md)

### Fase 13 e cronologia

- [Specifiche fase 13](../PHASE_13_SPEC.md)
- [Cronologia](../HISTORY.md)

## Schede della knowledge base

- [Preparazione della prossima gara: SETUP GARA → AVVIA GARA](sottosistemi/setup-prossima-gara.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; mappa delle fonti, non requisito approvato.
- [Autenticazione, sessioni e ruoli](sottosistemi/autenticazione-e-sessioni.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; mappa delle fonti, non requisito approvato.
- [Database, migrazioni e concorrenza](sottosistemi/database-migrazioni-e-concorrenza.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; schema descritto distinto da quello SQLite reale.
- [Eventi live e SSE](sottosistemi/eventi-live-e-sse.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; contratto, registro e trasporto condivisi.
- [Team, piloti e mazzi](sottosistemi/team-piloti-e-mazzi.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; interfacce API, servizi e tre mazzi.
- [Campionati e iscrizioni](sottosistemi/campionati-e-iscrizioni.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; creazione, iscrizione, regole e classifica.
- [Gare, risultati e classifica](sottosistemi/gare-risultati-e-classifica.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; stato gara, risultati, saldi e modulo live.
- [Draft e preparazione della prima gara](sottosistemi/draft-prima-gara.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; fasi, turni, snapshot e modal host.
- [Carte sponsor in gara e revisione](sottosistemi/carte-sponsor-e-revisione.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; giocate, tasto S, conteggi e timer.
- [Negozio, pacchetti e acquisti](sottosistemi/negozio-e-pacchetti.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; acquisti, estrazione, storico e apertura.
- [Pool, caricamento carte e amministrazione](sottosistemi/pool-e-amministrazione-carte.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; ricarica, ritaglio, trasferimenti admin.
- [Interfaccia, navigazione e QR](sottosistemi/interfaccia-navigazione-e-qr.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; guscio, menu, drawer e QR di accesso.
- [Avvio, configurazione e strumenti](sottosistemi/avvio-configurazione-e-strumenti.md) —
  revisione `21e17e637b43528d7320e88f0af5623db7158ee9`; launcher, produzione LAN e strumento immagini.

Le schede non si considerano obsolete a ogni commit: verranno rivalutate quando cambiano le fonti pertinenti.

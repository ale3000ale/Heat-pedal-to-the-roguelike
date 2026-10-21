# Fase 15 - SSE e sistemazione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione; PR 14 in bozza.
Base main 2cded6d. Nessun merge autorizzato. Cronologia estesa in Git e nelle
versioni fcead0f/a36e536/cc8ba7a di questo riepilogo e nelle note dei singoli blocchi.

## Stato verificato

| Blocco recente | Commit verificato | CI ordinaria verde |
|---|---|---|
| Campionato collegato | dc97fcf | 39502927035 |
| Gara e nullable corretto | 4978f73 | 39596834057 |
| Merge inventari puro | 6aa7fe6 | 39599465230 |
| Guardie sessione | 01c567a | 39636047244 |
| Store/pannello live | 1145a9a | 39650297363 |
| Conservazione pannello e canvas | 8018d18 | 39658083388 |

Backend SSE, event_log, timer, client condiviso, coalescer/fallback, ID CardGift,
API selettiva e notifiche gia' verificati nei blocchi precedenti. Campionato usa
/seen-selected per i soli regali resi; annulli/chiusure remote non confermano.
Gara preserva ordine/assenti come assegnazione unica e sponsor per pilota, aggiorna
ufficiali/permessi, usa PUT esplicita e copia preinvio; bozza risultati in sola
lettura se perde permesso. Uscita protetta, senza annullare HTTP gia' partite.

Inventari collegati al merge e alla coda condivisa: mount GET-only, bozza propria,
chiave controllata dopo risorse e prima delle scritture, 403/409 non diventano [].
Remaining locali preservati con metadati remoti; spunte revocate sui dati cambiati.
Incompatibilita' conserva copie senza clamp e blocca editing/conferma. Recupero
che sostituisce lavoro richiede conferma e backup browser riuscito. Copie distinte
mai eliminate; storage non disponibile interrompe recupero/apertura sostitutiva.
Progresso legacy revoca spunte, progresso non applicabile resta testo. Recupero
confermato ignora solo l'esatta bozza server incompatibile nella stessa chiave;
nuovo contenuto incompatibile riblocca. Nessuna PUT di conteggi agli eventi.

## Lifecycle e canvas: applicati

Dal bot 8018d189dcef770a76093c59489566cdeccd4dc6, 21:02:09 CEST del 2026-10-21,
il pannello gia' mostrato non e' ricreato per il solo race.status. Resta nello
stesso contesto gara/utente per i gestori, passando in sola lettura quando
canReview diventa false. Cambi contesto o perdita del ruolo possono smontarlo.
enabled limita editing, apertura e recupero; riabilitazione richiede lettura nuova.
Il limite non concede permessi backend e non annulla scritture gia' inviate.

Canvas senza role img non consentito, controllo nativo con nome e focus visibile,
pointer e frecce, Maiusc fine, Invio/Spazio per esportare. Dimensioni e WebP invariati.
Tre nuovi test delle guardie del genitore; suite precedenti conservate.
CI 39658083388: migrazioni test success 21:09:09 CEST, frontend check/lint/test/build
success 21:09:40, backend pytest success 21:10:33. Diff dei sei file letto, conforme
al perimetro. Stato della nota conferma check senza diagnostica del canvas prima
del bot; nessuna certificazione di accessibilita' o DOM dalla sola CI.

## Invarianti e limiti

Un EventSource per applicazione nella scheda. Fallback/card_poll_seconds solo senza
stream open, nessun polling lento di sicurezza. Countdown con rilettura singola
alla scadenza. Replay legge REST autorizzate, non ricrea popup. Payload pubblici
senza conteggi/bozze; eventi e azioni condividono transazione backend, ID non riusati.
Timer per worker ogni 5 secondi, stop cooperativo e pulizia registro senza migrazioni
nel lifespan. Test a due processi su SQLite sintetico, non carico o multi-host.
Uso previsto a bassa affluenza con worker sullo stesso SQLite e /api same-origin;
proxy/buffering reale non collaudati. Verifica preinvio e scrittura restano distinte:
nessun nuovo ETag/lock ottimistico. 401/auth.expired fermano il contesto.

Nessun DB reale migrato, modificato o salvato in backup dall'assistente. Anche
heat.py start/setup possono migrare: nessun avvio sull'originale senza arresto,
backup verificato, prova su copia e permesso. Catena letta a2e6c0d4f8b3,
d5e9a3b7c1f6, d6f0a4b8c2e7, merge b2d6f0a4c8e1. Downgrade perde storia/garanzia
non riuso; non trasferire conferme fra backup o DB ricreati. Differenza Deck.cards
in DATABASE.md, nessun cambio formato/percorsi. CI sintetica non certifica gli originali.

## Collaudo e pendenti

Collegamenti e correzioni automatiche verificati; ora serve il collaudo browser SSE
in ambiente isolato, secondo PHASE_15_BROWSER_CHECKLIST.md. Nessun nuovo comando
locale o test manuale eseguito dall'assistente; non dichiarare conclusa la fase.
Warning canvas corretto nel codice verificato, interazioni ancora da provare.

Restano vulnerabilita' npm segnalate (6 low, 2 moderate, 2 high), non analizzate o
risolte; niente audit fix/force. Backup/setup sicuro da verificare, cookie secure
e URL SQLite fisso in config.py pendenti per online. 15b da definire dopo SSE.
PROJECT_SPEC.md/PROJECT_STATUS.md protetti: riallineamento separato da autorizzare.
Prima di aggiornamenti generali leggere SHOP_DESIGN.md e PROJECT_NOTES.md.

Note correnti: PHASE_15_CHAMPIONSHIP_LIVE.md, PHASE_15_RACE_LIVE.md,
PHASE_15_RACE_RESULT_RECONCILE.md, PHASE_15_REVIEW_INVENTORY_RECONCILE.md,
PHASE_15_REVIEW_SESSION_GUARD.md, PHASE_15_REVIEW_LIVE_CONNECT.md,
PHASE_15_REVIEW_LIFECYCLE_CANVAS.md. Questo push e' solo documentale, non modifica
codice o workflow; non attendere CI dei soli .md e non attribuirle esiti presunti.
Prossimo passo: risultati del collaudo, non altre funzionalita' o merge automatici.

# Fase 15a-4b - Collegamento gara e callback revisione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Base documentale 0709ca4 senza attesa CI, come richiesto. Implementazione
4833a8dce73dec8d6634376fdaaab67fa1d24168, fix 44bb4dd, testa formattata 4978f73
verificata in CI 39596834057. Nessun merge o intervento sui dati autorizzato.

## Comportamento corrente

Pagina championships/[id]/races/[raceId]/+page.svelte e race-review-panel.svelte
collegati; il pannello usa onchanged invece del reload. startLiveRefresh condiviso
legge gara, campionato e piloti propri senza effetti UI durante load. Eventi del
campionato/resync invalidano la lettura, anche per is_last quando parte una nuova
gara. Fallback solo senza stream open e con intervallo admin, niente altro
EventSource o polling lento di sicurezza con stream aperto.

Base server distinta da ordine/assenti/sponsor. Le REST riuscite usano il merge
puro gia' verificato su 3c860d2: assegnazione coerente, sponsor locali preservati,
conflitti senza scritture. Risultati ufficiali/permessi aggiornati comunque;
bozza in sola lettura se non piu' modificabile, solo in memoria fino all'uscita,
non autosalvata in browser o backend. Cambio utente svuota il contesto.

PUT esplicita verifica stato UI, tutti i piloti assegnati, duplicati, ID presenti
e massimo 12 partecipanti; normalizzazione sponsor preesistente. Backend autorevole
su regole/permessi. Copia preinvio come base per fondere risposta e modifiche fatte
durante richiesta. Nessun lock ottimistico introdotto, nessuna garanzia contro
sovrascritture concorrenti sul server. Letture durante PUT non applicate, nuova
lettura accorpata alla fine anche dopo errore. Risposte del vecchio contesto ignorate.

Uscita interna/unload protetti con bozza modificata o PUT in corso, anche su gare
concluse; il dialogo dice che uscire non annulla HTTP gia' partite. Sessione scaduta
non blocca autenticazione, errori refresh conservano dati, 401 svuota auth. Cleanup
invalida code/avvii tardivi. Pannello non richiama genitore dopo smontaggio e viene
ricreato per campionato/gara/utente/stato, non a ogni snapshot: semplici aggiornamenti
risultati non azzerano conteggi del pannello.

## Cronologia del type-check e verifica riuscita

Prima CI ordinaria 39593722874 su 4833a8d: frontend failure 13:41:05 CEST,
migrazioni success 13:41:13, backend pytest success 13:43:00 del 2026-10-21.
Formatter 39593716889 failure 13:41:16, nessun bot riuscito dichiarato per quel tentativo.
Log autore 13:54: race potenzialmente null nel callback unknownPilot e warning
separato canvas role img. Non presumere test/build riusciti nel tentativo fallito.

Fix 44bb4dd6a7eb90dca59299c0a09dea2795e5f6e8: knownPilotIds derivato da race?.results
o [], callback su Set sempre definito, guardia race !== null conservata. Nessun
race!, cast, soppressione TypeScript o cambio regole di salvataggio. Resta falso
prima della lettura e blocca bozza con ID non piu' presenti. Workflow riattivato
cambiando nome dello step check, senza ampliare file, trigger o comandi.

Bot 4978f7387562aea7f09d14fea05025ae01ed3025 alle 14:05:14 CEST. Diff letto:
sola formattazione di pagina gara e pannello, nessun ulteriore cambio logico.
CI ordinaria della nuova testa: 39596834057, tutti i job success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39596834057

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Migrazioni (database di test) | success | 14:06:53 |
| Frontend (check, lint, test, build) | success | 14:07:09 |
| Backend (pytest) | success | 14:08:53 |

Errore nullable risolto sulla testa formattata, non sul primo tentativo fallito.
Letti commit, diff ed esiti, non log completi formatter o conteggi dei test.
Nessun comando locale eseguito. Warning canvas non corretto: verde non significa
check privo di warning. I test puri/coordinatore e compiler non sono prove DOM.
Guardia uscita, sola lettura, callback e modifiche durante PUT da verificare
in integrazione/browser; nessuna riuscita manuale dichiarata o richiesta ora.

## Integrazione interna ancora pendente

review-counts.svelte.ts resta invariato: qui non si dichiara nuova sincronizzazione
SSE di inventari, bozze o cambio revisore a stato gara invariato. Il nuovo helper
review-inventory-reconcile.ts e' ora verificato su 6aa7fe6, CI 39599465230, ma non
ancora usato dallo store. Questa distinzione evita di dichiarare conclusa ogni
vista di revisione solo per la riuscita del collegamento gara.

Il formatter attuale e' mirato ai due file TypeScript degli inventari, non piu'
ai due componenti del blocco gara: le istruzioni di formattazione sopra sono
cronologia di 4833a8d/44bb4dd. Nessuna modifica ai componenti in questo riallineamento.
Nessuna nuova dipendenza, lockfile, API, schema, immagine o dato modificato.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Solo documenti, non attendere CI per
il seguito. Prossimo lavoro: collegare store/pannello al merge conservativo,
revoca spunte, blocchi e recupero esplicito confermato, con test lifecycle/permessi.
Nessuna prova browser finale richiesta prima del completamento e CI verde dei
collegamenti restanti. Nessun merge o intervento sul database reale autorizzato.

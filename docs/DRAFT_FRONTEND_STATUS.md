# Draft - incrementi frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Diagnostici e stato delle verifiche

L autore ha fornito alle 03:47 il log negativo di npm run check: 25 errori e 0 warning in draft-order.svelte e draft-modal.svelte. La collisione della variabile locale state con la runa $state e stata corretta con rename sessionState nel commit a854b28c9ea68444b216a45964925cad03fa6dd7. Non sono stati aggiunti subscribe, modificati store.state, port state o regole applicative.

Nessun nuovo esito di check attestato: il fix e pubblicato, non dichiarato verificato. Il log proviene dall autore, non da lettura autonoma di Actions. Nessuna installazione, formattazione, esecuzione locale di check/lint/test/build o consultazione/attesa CI per questo incremento. Il successivo ok intanto prosegui autorizza il seguito, non viene trasformato in un risultato positivo dei controlli.

## Incrementi pubblicati e incremento corrente

1. Tipi, validatori, client e test predisposti: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller e test predisposti: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store e test predisposti: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal e annullamento: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Scelta iniziale e presenze: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine locale e avvio sequenziale: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.
7. Turno, carte, zoom, anteprima e conferma della scelta con test predisposti: incremento corrente.

I componenti non sono montati nell app; Nuova gara, autenticazione, layout e SSE non collegati. Mancano schermate mazzi/READY e integrazione completa. Il flusso non e ancora disponibile agli utenti.

Il settimo aggiunge frontend/src/lib/draft-picking.ts, draft-picking.spec.ts, components/draft-picking-card.svelte, components/draft-picking.svelte e draft-picking-ui.spec.ts. CardTile.svelte e riusato senza modificarlo; ogni slot viene presentato come singola copia, con percorsi /media/ gia usati dall app. Nessuna conversione dei dati o nuove risorse.

## Fondazioni e lifecycle

DTO pubblici validati per forma, tipi, interi sicuri, nullable espliciti e ID duplicati; copie indipendenti senza campi interni. I validatori non riproducono l intero motore e non autorizzano scritture. Client autenticato condiviso, payload versionati e soli campi previsti, confronti di contesto quando disponibili. Nessun retry, polling o auto-reload dopo POST; errori di rete o DTO inutilizzabili non provano rollback.

Controller serializzato senza rete iniziale; versione dallo snapshot server, risposta obsoleta scartata. Draft/campionato fissati e versioni non decrescenti. getContext deve includere generazione autenticata e contesto, anche a nuovo login dello stesso utente. Il futuro host deve integrare syncContext/dispose a cambi e smontaggio; AuthStore non modificato e user_id da solo insufficiente. dispose definitivo, senza annullare HTTP gia inviati o garantire rollback.

409 blocca conservando snapshot non aggiornato; rete, 500 e DTO inutilizzabile durante comando sono esiti incerti; 422 permette correzione manuale; 401/403 rimuovono snapshot. Solo lettura valida libera il blocco, 404 non prova creazione/annullo. READY intermedio conserva preparazione; race_id conclude come gara creata; cancel conclude separatamente. Store a istanze con $state.raw, viste indipendenti e aggiornamento avvio/finally, senza seconda coda. busy/blocked non sono permessi.

## Modal, presenze e ordine

Modal condiviso conserva X visibile a destra e abilitata per default. Opzioni nuove per X, closeOnOutside per Escape/sfondo; confirm-dialog e modal-close invariati. DraftModal usa X a sinistra e Escape/sfondo disabilitati. X solo al creatore non completamente READY coi propri presenti; insieme vuoto non blocca per vacuita. Conferma annullare la gara? legata a store/ID/versione, ricontrollata al clic. Non annullare non scrive; contenuti montati ma nascosti/inert durante conferma; nessuna chiusura anticipata o falso ripristino. Rilettura server esplicita.

Scelta iniziale Draft invoca il futuro padre, non start o apertura preparazione. Gara gia disputata attende il comando dedicato e race_id, senza vincoli mazzi/READY o inserimento risultati. Presenti sopra Assenti con ordine ricevuto e conteggio per pilota. Escludi/Includi attendono il server; Avanti conferma presenze entro il limite esistente backend 1-12. Pool, mazzi e fase successiva restano al server.

Ordine iniziale solo server, nessun sorteggio nel browser; Prima gara centrato in strong. Trascinamento pointer e Su/Giu con bozza indipendente, baseline e versione. Interruzione del gesto ripristina l ordine locale precedente al gesto. Bozza incompatibile conservata e bloccata; scarto esplicito senza rete o sblocco del controller. Avanti salva order se necessario e solo dopo snapshot utilizzabile chiama start. Due HTTP, non transazione unica: save puo essere riuscito anche quando start fallisce; nessun rollback inventato o retry. Pool divenuta insufficiente e un errore server, non un salto client a decks.

## Scelta delle carte

La vista usa current_pilot_id, my_pilot_ids, order, picks e chosen_by. Il semplice can_manage non concede una scelta. Sono controllati i riferimenti necessari al turno, alle scelte e all anteprima, non tutta la coerenza del motore. Copie identiche restano distinte per slot_id e le scelte vengono riepilogate nell ordine del registro con il nome del pilota.

Proprietario del pilota di turno: sezione verde e tocca a te pulsante; altri: sezione rossa e nome del pilota corrente. L animazione rispetta prefers-reduced-motion. Il colore segnala la proprieta del turno, non autorizza comandi durante busy o blocchi. Il componente colora la propria sezione, non modifica globalmente lo sfondo di tutti i modal.

Ogni carta disponibile o scelta puo essere ingrandita localmente e ridotta ripremendola. Lo zoom e legato a istanza store, draft e turno e viene ignorato se quel contesto cambia. Solo il proprietario di turno con stato utilizzabile puo inviare preview; gli altri zoom non scrivono. L alone giallo e il nome riflettono solo preview_slot_id ricevuto dal server, non il solo zoom locale. Chiudere lo zoom o passare a una carta gia scelta puo revocare un anteprima condivisa precedente del proprio turno. Nessun reinvio se il valore condiviso e gia quello richiesto.

Scegli compare solo sulla copia disponibile ingrandita del proprietario autorizzato. Prima si propone la conferma testuale con nome carta e pilota; vengono catturati store, draft/campionato, versione, turno e slot con nome/percorso. Variazioni invalidano la proposta. Torna alle carte non invia choice. La conferma ricontrolla tutto e invia una sola choice; nessuna rimozione ottimistica, aggregazione di copie o aggiornamento inventato dell inventario.

Durante conferma/invio le carte non sono interattive. Errori mantengono la gestione di blocco del controller; la conferma viene consumata e non ritentata automaticamente. Le scelte visibili e la disponibilita derivano dalla risposta server. L ultima choice segue decks e non crea Race; la creazione finale appartiene al READY backend.

Il componente non apre modal da solo, non installa EventSource e non fa polling. L anteprima puo essere mostrata quando arriva un DTO aggiornato, ma la propagazione live tra dispositivi richiede ancora l integrazione SSE. Non viene dichiarato un aggiornamento simultaneo gia funzionante.

## Copertura predisposta e limiti

Test helper: turno/proprieta, copie identiche, riferimenti, anteprime, blocchi e conferme obsolete. Test SSR: colori, testo turno, immagini, copie e riepilogo; rendering della carta ingrandita con o senza Scegli. Non attivano zoom, preview, choice o eventi DOM e non provano richieste POST dei componenti. Controller e store usano trasporti simulati, non DB concorrente reale. Tutti questi test restano predisposti, non dichiarati eseguiti o superati.

Non attestati: type-check del nuovo incremento, lint, Vitest, build, trascinamento touch, focus, keyboard/stacking, navigazione, interazioni browser, sincronizzazione multiutente o flusso end-to-end. I risultati backend precedenti non attestano il frontend. Il focus trap e l accessibilita complessiva del sistema modal non sono dichiarati completi.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build; nessun comando eseguito localmente in questa preparazione. Le precedenti letture GitHub fallite con 503 erano state recuperate ritentando e non erano test applicativi falliti.

## Metodo e seguito

Push diretto degli incrementi approvati sul solo draft. Niente accumulo nei commenti o nuovi workflow. CI controllata o attesa soltanto su indicazione dell autore. Nessun merge implicito.

Questo documento aggiorna lo stato tecnico; docs/DRAFT_SPEC.md conserva le regole funzionali. Note backend e manifest sono verifiche precedenti, non nuovi verdi frontend. Setup, script, schema, risorse, dipendenze e lockfile invariati; nessun nuovo scaffold, API backend, migrazione o accesso al database reale.

Restano mazzi/READY, montaggio Nuova gara/layout, autenticazione, lifecycle e SSE, test di integrazione e collaudo browser.

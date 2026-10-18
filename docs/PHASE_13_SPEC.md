# Fase 13 — Carte sponsor e amministrazione delle carte

> STATO: DECISIONI APPROVATE DALL'AUTORE (11-13 ottobre 2026). Regole della revisione aggiornate il 13 ottobre 2026 (revisore unico, scadenza con conferma automatica, riapertura dell'admin, rimozione carte). Regole della 13e aggiunte il 13 ottobre 2026. Avanzamento della 13f aggiunto il 18 ottobre 2026.
> Quando la fase sarà conclusa, il contenuto confluisce in `PROJECT_SPEC.md` (nuova sezione 14) e questo file resta come storico.
> Regola di lavoro: ogni regola decisa dall'autore va scritta subito in questo file, così non si perde.

La fase 14 (dopo la 13) è dedicata alla sistemazione generale e ai miglioramenti di vivibilità, senza nuove regole di gioco.

## Parte A — Carte sponsor in gara

### Inventario

- Le carte sponsor non entrano nel mazzo da gioco (limite 15) e restano nell'inventario sponsor del pilota.
- Il popup dell'inventario ha due sezioni a scomparsa: **Modifiche** e **Sponsor**.

### Giocatore, durante una gara in corso

- Premendo sul campionato, il giocatore vede una sezione a scomparsa per ogni suo pilota iscritto, tutte chiuse e con solo il nome. Con un solo pilota iscritto la sua sezione è già aperta.
- Nella sezione compaiono prima le carte sponsor, poi un riepilogo con immagini del mazzo da gioco in uso.
- Toccando una carta sponsor un popup chiede conferma; alla conferma la carta sparisce dalla vista del giocatore (uso temporaneo).
- Il pulsante **Indietro** annulla l'ultima carta giocata, fino a un massimo di 5 annullamenti consecutivi. Lo stack degli annullamenti sta nel backend (sopravvive al ricaricamento della pagina).
- Le copie uguali di una stessa carta sono raggruppate con "x N", come nel riepilogo del negozio.
- Il registro completo delle carte giocate nella gara resta intero: il limite di 5 vale solo per l'annullamento, non per il riepilogo del giudice.
- Il giocatore può giocare e annullare solo per i propri piloti. Giudice e admin, quando agiscono come giocatori, valgono come tutti gli altri: non giocano mai per un pilota altrui.
- Nella sezione di gioco il giocatore aveva anche il tasto **S** sui propri piloti: dopo conferma otteneva una carta sponsor casuale per sé.
  - Aggiornamento 13d (decisione dell'autore, 12 ottobre 2026): il tasto S non sta più nella sezione del giocatore ma nella pagina della gara, visibile solo a giudice e admin.

### Stato della gara: "in revisione"

- La revisione si avvia quando il giudice o l'admin preme **termina gara** nella pagina della gara, prima dell'inserimento dei risultati. Chi la avvia diventa il **revisore**.
- In revisione i giocatori non possono più giocare, annullare carte sponsor né usare il tasto S.
- **Revisore unico**: solo il revisore vede la revisione e può agire. Qualsiasi altro utente, giudici e admin compresi, non vi accede e riceve un rifiuto (409). Nemmeno l'admin subentra durante la revisione.
- Se il revisore se ne va e rientra, riprende la propria revisione dalla pagina della gara.
- **Scadenza** (decisione dell'autore, 13 ottobre 2026): 15 minuti dall'inizio della revisione (non dall'ultima azione, valore di configurazione). Alla scadenza la revisione **si conferma così com'è**: le carte giocate e non annullate escono dall'inventario e tornano nella pool, e la gara si chiude del tutto. Non c'è nessun processo in background: la conferma avviene alla prima richiesta successiva, quando il backend legge lo stato di una revisione o crea una nuova gara. Se una carta giocata non è più nell'inventario del pilota, quella gara resta com'è e la sistema l'admin.
- Il revisore può rinunciare alla revisione in qualsiasi momento: le giocate non cambiano e la gara torna "da rivedere".
- Il revisore **conferma** la revisione quando ha finito: le carte giocate escono dall'inventario e la gara si chiude. Con la revisione scaduta o mai aperta può confermare solo l'admin.
- Azioni del revisore (solo in revisione): annullare una carta giocata, assegnare una carta bonus dalla pool, **rimuovere** una carta sponsor dall'inventario di un pilota quando è stata assegnata per errore o non è stata giocata. La carta rimossa torna nella pool, come se fosse stata giocata e il giocatore si fosse dimenticato di toglierla.
- Il riepilogo e le correzioni avvengono un attimo prima della chiusura (conferma della revisione).

### Giudice e admin

- Giudice e admin sono come giocatori: giocano solo per i propri piloti. Il loro potere in più è il tasto S sugli altri piloti e la revisione a fine gara.
- Durante la gara hanno l'elenco completo dei piloti iscritti; accanto al nome un tasto **S** assegna una carta sponsor **casuale** dalla pool sponsor del campionato, dopo conferma: il pilota di quella riga la riceve. È un regalo: non costa punti sponsor.
- Il backend ammette giudice e admin su qualsiasi pilota iscritto non eliminato (404 per pilota inesistente o eliminato, 403 per pilota non iscritto); il giocatore resta limitato ai propri piloti.
- Il tasto S funziona solo con una gara in corso. Con la pool sponsor vuota la specifica prevedeva il tasto disabilitato con un avviso.
  - Aggiornamento 13d (scelta dell'assistente, da confermare): il tasto resta sempre attivo e l'avviso arriva dal backend con un errore 409, perché il frontend non può leggere lo stato della pool senza una rotta nuova.
- La carta entra nell'inventario del pilota e l'inventario si aggiorna in tempo reale (controllo periodico ogni pochi secondi, senza canali continui).
- **Intervallo di controllo** (13c-1, decisione dell'autore, 12 ottobre 2026): è un'impostazione generale dell'admin, `card_poll_seconds`, da 1 a 10 secondi con predefinito 5, valida per tutti i campionati, anche quelli già creati. Rotte `GET /api/admin/card-poll` (ogni utente collegato) e `PUT /api/admin/card-poll` (solo admin). Il giocatore legge l'intervallo una volta all'apertura della pagina: una modifica dell'admin vale dopo il ricaricamento.
- Al giocatore compare un popup con la carta ottenuta e il testo "Hai ottenuto una carta sponsor".
- Il giudice (e l'admin) non vede quale carta è uscita: la vede solo nel riepilogo finale.
- Nel riepilogo (con immagini), visibile solo al revisore, vedono le carte sponsor giocate da tutti i piloti, possono ripristinare una carta giocata per errore, rimuovere una carta e assegnarne altre come bonus.
- Il bonus non crea notifiche e serve solo a correggere errori: la notifica "Hai ottenuto una carta sponsor" nasce solo dal tasto S.
- Ogni assegnazione o ripristino dipende dalla disponibilità della pool.

### Chiusura della gara

- Alla conferma della revisione (del revisore, o automatica alla scadenza) le carte giocate escono in modo definitivo dall'inventario dei piloti e tornano nella copia di pool sponsor del campionato.
- Una gara annullata non è prevista. Le correzioni dei risultati restano come da `PROJECT_SPEC.md` (solo admin).

### Correzioni dell'admin dopo la conferma

- L'admin può **riaprire** la revisione di una gara già confermata, ma solo se è l'**ultima gara del campionato** (numero più alto). Da quel momento l'admin è il revisore, con altri 15 minuti di tempo, e può fare le stesse correzioni del revisore (annullo, bonus, rimozione).
- Annullando una giocata già consumata la carta torna al pilota dalla pool sponsor. Il ripristino è possibile solo se la pool ha ancora una copia uguale disponibile; altrimenti viene rifiutato con un messaggio chiaro (409).
- Il giudice non può riaprire una revisione confermata (403). Una gara non ultima, o con la revisione non ancora confermata, viene rifiutata (409).

### Rotte della revisione

Tutte sotto `/api/championships/{championship_id}/races/{race_id}`.

| Metodo e percorso | Chi | Effetto |
|---|---|---|
| `GET /review` | utente autenticato | Stato della revisione. Prima conferma le revisioni scadute del campionato. Risposta con `in_review`, `reviewer_user_id`, `review_expires_at`, `review_closed_at`, `is_last_race`. |
| `POST /review` | giudice o admin | Apre la revisione o riprende la propria. |
| `DELETE /review` | revisore | Rinuncia alla revisione. |
| `POST /review/confirm` | revisore, o admin se scaduta o mai aperta | Conferma e consuma le carte giocate. |
| `POST /review/reopen` | solo admin | Riapre una revisione confermata, solo sull'ultima gara. |
| `GET /card-plays` | giudice o admin | Riepilogo delle giocate di tutti i piloti. |
| `POST /card-plays/{play_id}/cancel` | revisore | Annulla una giocata, anche già consumata. |
| `POST /card-bonus` | revisore | Una copia dalla pool al pilota. |
| `POST /card-removal` | revisore | Una copia dall'inventario del pilota alla pool. |

## Parte B — Amministrazione delle carte

### Caricamento (solo admin)

- Da smartphone: scatto di una foto, scelta dall'album o dai file. Da computer: scelta di un file.
- Formati foto accettati: JPEG, PNG e WebP (decisione dell'autore, 13 ottobre 2026). Il backend converte tutto in WebP (qualità 90, senza trasparenza) nella scatola 560x870 px (proporzione 5,6 x 8,7 cm). Il formato HEIC non è previsto, perché Pillow non lo apre senza un plugin.
- Dopo la scelta del file l'interfaccia mostra come sarà tagliata l'immagine; l'admin può spostarla e fare zoom avanti e indietro per centrarla.
- **Ritaglio nel frontend** (decisione dell'autore, 13 ottobre 2026): il frontend invia al backend un'immagine già tagliata e ridimensionata a 560x870 px. Il backend la converte in WebP e non ritaglia da solo.
  - Implementato nella 13e: il backend rifiuta con 422 le immagini di dimensioni diverse da 560x870 (costante `CARD_IMAGE_SIZE` in `config.py`) invece di ridimensionarle in silenzio.
- Dopo la conferma del ritaglio l'admin scrive il **nome**, la **quantità** e sceglie il **tipo** (modifiche o sponsor, obbligatorio). Il nome del file è `nome_quantità` e la funzione `parse_card_filename` (in `services/cards.py`) ricava da esso nome e copie.
- **Regole su nome e quantità** (implementate in `services/card_upload.py`): il nome, senza spazi ai bordi, non è vuoto, ha al massimo 64 caratteri, non comincia con un punto e non contiene `/ \ : * ? " < > |`; le copie vanno da 1 a 999. Chi le viola riceve un 422 con un messaggio leggibile.
- **Percorso e origine** (decisione dell'autore, 13 ottobre 2026): le carte caricate si riconoscono dal percorso e non da una colonna del database, quindi la 13e non ha migrazioni. Il percorso è `cards/uploads/<tipo>/nome_quantità.webp`, relativo a `backend/media`, con una cartella per tipo (`modifiche` o `sponsor`). La ricarica della pool di base (`reload_base_pool`) toglie solo le carte con percorso `cards/base/<tipo>/` e quindi non tocca le carte caricate.
- Un nome già esistente nella pool di base del tipo scelto (senza distinguere le maiuscole, stessa regola di `card_key`) viene rifiutato con un errore 409 e un avviso. Lo stesso errore vale se il file di destinazione esiste già.
- Le carte caricate entrano in fondo alla pool di base del loro tipo e si riconoscono dal **nome in arancione**, mostrato solo nelle pagine di gestione delle pool. Se la scrittura nel database fallisce, il file appena scritto viene rimosso.
- Libreria: la conversione usa Pillow, già presente (`pillow==12.3.0`). Per ricevere il file serve `python-multipart`, aggiunto a `backend/requirements.txt` alla versione stabile 0.0.32 (decisione dell'autore, 13 ottobre 2026: aggiungere le librerie necessarie).
- La dimensione massima del file è `MAX_CARD_UPLOAD_BYTES` in `backend/app/config.py`: 2 MB secondo il commento della rotta (il valore numerico in `config.py` non è stato riletto per questo aggiornamento). Oltre il limite la rotta risponde 413 se l'intestazione `content-length` lo rivela subito; altrimenti il servizio rifiuta il file con 422.

### Eliminazione

- Solo l'admin elimina le carte caricate; le carte di base e quelle di partenza non si eliminano mai (409). Si riconoscono dal percorso `cards/uploads/`.
- L'eliminazione toglie la carta dalla pool di base; le copie già presenti nelle pool dei campionati e negli inventari non cambiano.
- **Il file immagine resta finché un campionato usa la carta** (decisione dell'autore, 13 ottobre 2026): vale per ogni campionato, attivo o chiuso. Il file viene cancellato quando nessun campionato ha più la carta nella propria copia di pool (modifiche o sponsor).
- Quando un campionato viene cancellato (`delete_championship` in `services/championships.py`, rotta `DELETE /api/championships/{championship_id}`, solo admin e solo campionati chiusi) si controllano i file orfani: i file di `cards/uploads/` che nessuna pool e nessun campionato usa più vengono cancellati. Il controllo è una funzione di `services/card_delete.py` richiamata da `delete_championship`.

### Pool personalizzate

- La gestione delle pool resta quasi invariata.
- Nella creazione di una pool personalizzata ci sono due tasti: **escludi tutte le carte caricate** ed **escludi tutte le carte di base**.

### Rotte della 13e

Il router `api/card_admin.py` è registrato in `main.py` con prefisso `/api/admin/cards`, prima del router `admin`.

| Metodo e percorso | Chi | Effetto |
|---|---|---|
| `POST /api/admin/cards?kind=&name=&copies=` | solo admin | Carica una carta. Il corpo della richiesta è l'immagine già tagliata a 560x870; `kind` è `modifiche` o `sponsor`, `name` da 1 a 64 caratteri, `copies` da 1 a 999. Risponde 201 con nome, percorso, copie e tipo; 404 se manca la pool di base, 409 per nome già usato, 413 per file troppo grande, 422 per immagine o dati non validi. |
| `DELETE /api/admin/cards?kind=&name=` | solo admin | Elimina una carta caricata dalla pool di base e cancella i file rimasti senza uso. Risponde con `removed_files`; 404 se la carta non c'è, 409 se non è una carta caricata. |

## Sottofasi

| Sottofase | Contenuto |
|---|---|
| 13a | Backend carte sponsor: registro delle carte giocate, stack da 5 annullamenti, uso e annullamento, restituzione alla pool alla chiusura |
| 13b | Backend: stato "in revisione" con revisore unico e scadenza di 15 minuti con conferma automatica, riepilogo, correzione, rimozione e bonus (solo in revisione), riapertura dell'admin, tasto S, notifica di carta ottenuta |
| 13c-1 | Backend: intervallo di controllo delle notifiche (`card_poll_seconds`, da 1 a 10 secondi, predefinito 5, modificabile solo dall'admin) |
| 13c | Frontend giocatore: sezioni a scomparsa per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor", controllo periodico con l'intervallo della 13c-1 e campo nelle impostazioni generali |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, revisione nella pagina della gara con immagini, correzioni |
| — | Dopo la 13d: riallineamento di tutti i documenti (richiesta dell'autore) |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" (dal percorso `cards/uploads/`), pulizia dei file orfani alla cancellazione di un campionato |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate |
| 13g | Documenti e test finali, unione in `main` |

Ogni sottofase parte solo dopo l'approvazione dell'autore, con l'elenco dei file previsti. Tutto il lavoro della fase 13 resta nel ramo `phase-13a-card-plays`, senza rami separati per le sottofasi.

### File previsti per la 13e

- Nuovi: `backend/app/services/card_upload.py`, `backend/app/services/card_delete.py`, `backend/app/api/card_admin.py`, `backend/app/schemas/card_admin.py`, `backend/tests/test_card_upload.py`, `backend/tests/test_card_delete.py`.
- Da modificare: `backend/app/main.py` (registra il router), `backend/app/services/championships.py` (richiama la pulizia dei file orfani in `delete_championship`), `backend/app/config.py` (dimensione massima del file), `backend/requirements.txt` (`python-multipart==0.0.32`), poi i documenti a test verdi.
- Nessuna migrazione e nessuna colonna nuova.

## Avanzamento della 13b

- Fatto: colonna `race.review_started_by_user_id` (migrazione `a9c3e7b1d5f0` e modello `Race`).
- Fatto: revisore unico (`_reviewed_race` in `services/card_judge.py`: revisione attiva e aperta dall'utente che agisce, altrimenti rifiuto), annullamento della giocata (anche già consumata, con ritorno della carta dalla pool), bonus dalla pool e **rimozione di una carta dall'inventario del pilota** con ritorno alla pool (`remove_card`, rotta `POST .../card-removal`, commit `86e5893` e correzione `1bfba4b`).
- Fatto: conferma automatica delle revisioni scadute (`settle_expired_reviews` in `services/race_review.py`), riapertura dell'admin sull'ultima gara (`reopen_review`, `is_last_race`), rotte `GET .../review` e `POST .../review/reopen`, campo `is_last_race` in `RaceReviewRead`, traduzione HTTP degli errori nuovi (403 per chi non è admin, 409 per gara non ultima o revisione non confermata). Commit `76e97cf` (rotte) e `c8c5c61` (test).
- Rimozione, regole: serve la revisione attiva del revisore; 409 se il campionato non ha una pool sponsor, se la carta non è nell'inventario del pilota o se tutte le copie sono impegnate in giocate attive (il revisore deve prima annullarle); 404 per pilota inesistente o eliminato; 403 per pilota non iscritto. La copia va dall'inventario sponsor del pilota alla pool sponsor del campionato in un solo commit.
- Rimozione, nota tecnica: `_without_one_copy` (in `services/card_gift.py`) confronta le carte per identità (`is`), quindi `remove_card` le passa lo stesso oggetto presente nella lista dell'inventario e non una copia.
- Test: 13 test della rimozione in `backend/tests/test_card_judge.py`; i test di stato, scadenza e riapertura sono in `backend/tests/test_race_review_reopen.py`; 6 test dell'annullo di giocate già consumate dopo la riapertura (carta che torna dalla pool, 409 se la pool ha perso la carta, 409 senza revisione attiva o con un altro revisore, nuova conferma che consuma solo la giocata rimasta) in `backend/tests/test_card_judge_reopen.py` (commit `55fbcea`). La scadenza è provata portando la data di apertura a 20 minuti prima direttamente nel database, senza orologio finto. Esito verde della CI sulla pull request #9 (backend pytest, migrazioni, frontend) letto da GitHub il 13 ottobre 2026 sull'esecuzione partita subito dopo il commit `55fbcea`; lo SHA esatto dell'esecuzione non è riportato dall'elenco dei controlli.
- Fatto: la pull request #11 (merge `f733886`, commit dei test `2f12768`) ha aggiunto test sulla scadenza della revisione e sul secondo giudice, su bonus e annullo. L'esito della CI su quel commit non è stato letto per questo documento. L'autore ha confermato il 13 ottobre 2026 che `f733886` è nel ramo.
- Fatto: `PROJECT_SPEC.md` riallineata alla fase 13 (revisione, intervallo notifiche, tasto S, migrazioni) nel commit `bc0fbfb`.
- Fatto: riallineamento di `PROJECT_STATUS.md`, `PROJECT_NOTES.md`, `SHOP_DESIGN.md` e `README.md` il 13 ottobre 2026 (commit `b495466`, `8947c43`, `c7fbe7f`, `803b8d4`, `ddbc33e`), con 447 test del backend passati in locale.
- Fatto: frontend del revisore (13d), confermato dall'autore il 13 ottobre 2026: tasto S sull'elenco piloti, revisione nella pagina della gara con riepilogo con immagini, correzioni (annullo, bonus, rimozione) e riapertura per l'admin. L'autore ha anche verificato a mano il flusso completo e le migrazioni su una copia del database, e confermato la CI verde.

## Avanzamento della 13e

- Fatto (backend, commit del 13 ottobre 2026): dipendenza `python-multipart` (`d89f75d`), limiti del caricamento in `config.py` (`ba7a587`), servizio di caricamento (`358297a`), eliminazione delle carte caricate con pulizia dei file orfani (`cb934d8`), pulizia dei file rimasti senza uso in `delete_championship` (`3a79199`), rotte admin per caricare ed eliminare (`e26801e`), test di caricamento, eliminazione e pulizia (`14557ab`).
- Fatto: la correzione di `delete_championship`, che cancella anche giocate e regali di carte delle gare (`a5bbe26`, test `020ef6e`).
- Test: 474 test del backend passati in 60,54 secondi, esito riferito dall'autore il 13 ottobre 2026 dopo la 13e. L'esito della CI della 13e non è stato riletto.
- Verifiche rilette per questo aggiornamento: rotte e prefisso `/api/admin/cards` (`api/card_admin.py` e `main.py`), controlli su formato, misure, nome e copie (`services/card_upload.py`).
- Prossimo passo: 13f (frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate), dopo l'approvazione dell'autore e con l'elenco dei file previsti.

## Avanzamento della 13f

- Fatto (frontend, commit del 14 ottobre 2026): logica pura con test (`lib/card-crop.ts` e `card-crop.spec.ts`, `lib/card-admin-api.ts` e `card-admin-api.spec.ts`, `9261af2`), componenti di caricamento (`e5cf313`: `card-crop-editor.svelte`, `card-upload-form.svelte`, `pool-card-picker.svelte`) con elenco delle carte della pool di base, nomi in arancione per le carte caricate a mano e tasto «Elimina», e integrazione nella pagina admin delle pool (`routes/admin/pools/+page.svelte`, «Nuova pool» e «Carica una carta»).
- Correzioni: `254b015` (formattazione Prettier), `062629f`, `1391a70` e `8dbd7c2` (errori ESLint in `card-crop-editor.svelte`).
- Esiti: l'autore ha riferito il 14 ottobre 2026 che lint e funzionalità erano a posto e il 18 ottobre 2026 che test e CI sono passati tutti. La CI è stata letta il 18 ottobre 2026: verde sul commit `9f3b517` (testa del ramo, [esecuzione 38480483060](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/38480483060) partita alle 22:50:49 UTC del 2026-10-13: Backend pytest, Migrazioni e Frontend con successo). I comandi locali e la prova a mano del caricamento e dell'eliminazione non sono stati descritti uno per uno.
- Fatto (18 ottobre 2026): i due tasti di esclusione nella creazione delle pool personalizzate («Escludi tutte le carte caricate» ed «Escludi tutte le carte di base»), prima mancanti. `lib/pool-exclusion.ts` (`excludeCardGroup` con il test `pool-exclusion.spec.ts`), `isBaseCard` in `lib/card-origin.ts` (percorso `cards/base/`, come `reload_base_pool`) e i due tasti sopra l'elenco in `routes/admin/pools/+page.svelte`. Azzera le copie scelte del gruppo nel solo modulo «Nuova pool», senza toccare il database; le carte di partenza non si toccano.
- Fatto (18 ottobre 2026, 13c): la sezione di un pilota nasce già aperta quando il giocatore ha un solo pilota iscritto (proprietà `startOpen` di `PilotCardPlays`, letta in `onMount` per il solo valore iniziale) e in fondo alla sezione c'è il riepilogo con immagini del mazzo da gioco in uso (`lib/pilot-deck-api.ts`, `fetchPilotGameDeck`, con il test `pilot-deck-api.spec.ts`).
- Controlli locali (18 ottobre 2026): `npm run check` (0 errori), `npm run lint`, `npm test` (110 test passati su 110: base misurata 101, i 9 nuovi sono 7 di `pool-exclusion.spec.ts` e 2 di `pilot-deck-api.spec.ts`), `npm run build` riuscito. Backend non toccato.
- Prossimo passo: 13g (documenti e test finali, unione in `main`; l'autore ha dato l'incarico il 18 ottobre 2026).

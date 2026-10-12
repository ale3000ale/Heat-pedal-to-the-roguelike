# Fase 13 — Carte sponsor e amministrazione delle carte

> STATO: DECISIONI APPROVATE DALL'AUTORE (11-13 ottobre 2026). Regole della revisione aggiornate il 13 ottobre 2026 (revisore unico, scadenza con conferma automatica, riapertura dell'admin, rimozione carte).
> Quando la fase sarà conclusa, il contenuto confluisce in `PROJECT_SPEC.md` (nuova sezione 14) e questo file resta come storico.

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
- Nella sezione di gioco il giocatore ha anche il tasto **S** sui propri piloti: dopo conferma ottiene una carta sponsor casuale per sé.
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
- Il tasto S funziona solo con una gara in corso. Con la pool sponsor vuota è disabilitato, con un avviso.
- La carta entra nell'inventario del pilota e l'inventario si aggiorna in tempo reale (controllo periodico ogni pochi secondi, senza canali continui).
- Al giocatore compare un popup con la carta ottenuta e il testo "Hai ottenuto una carta sponsor".
- Il giudice (e l'admin) non vede quale carta è uscita: la vede solo nel riepilogo finale.
- Nel riepilogo (con immagini), visibile solo al revisore, vedono le carte sponsor giocate da tutti i piloti, possono ripristinare una carta giocata per errore, rimuovere una carta e assegnarne altre come bonus.
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
- Formati foto accettati; il backend converte tutto in WebP nella scatola 560x870 px (proporzione 5,6 x 8,7 cm).
- Dopo la scelta del file l'interfaccia mostra come sarà tagliata l'immagine; l'admin può spostarla e fare zoom avanti e indietro per centrarla.
- Dopo la conferma del ritaglio l'admin scrive il **nome**, la **quantità** e sceglie il **tipo** (modifiche o sponsor, obbligatorio). Il file è salvato come `nome_quantità` in `backend/media/cards/uploads/`.
- Un nome già esistente nella pool (senza distinguere le maiuscole) viene rifiutato con un avviso.
- Le carte caricate entrano nella pool di base del loro tipo e si riconoscono dal **nome in arancione**, mostrato solo nelle pagine di gestione delle pool.

### Eliminazione

- Solo l'admin elimina le carte caricate. L'eliminazione le toglie dalla pool di base; le copie già presenti nelle pool dei campionati e negli inventari non cambiano.

### Pool personalizzate

- La gestione delle pool resta quasi invariata.
- Nella creazione di una pool personalizzata ci sono due tasti: **escludi tutte le carte caricate** ed **escludi tutte le carte di base**.

## Sottofasi

| Sottofase | Contenuto |
|---|---|
| 13a | Backend carte sponsor: registro delle carte giocate, stack da 5 annullamenti, uso e annullamento, restituzione alla pool alla chiusura |
| 13b | Backend: stato "in revisione" con revisore unico e scadenza di 15 minuti con conferma automatica, riepilogo, correzione, rimozione e bonus (solo in revisione), riapertura dell'admin, tasto S, notifica di carta ottenuta |
| 13c | Frontend giocatore: sezioni a scomparsa per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor" |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, revisione nella pagina della gara con immagini, correzioni |
| — | Dopo la 13d: riallineamento di tutti i documenti (richiesta dell'autore) |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate |
| 13g | Documenti e test finali, unione in `main` |

Ogni sottofase parte solo dopo l'approvazione dell'autore, con l'elenco dei file previsti.

## Avanzamento della 13b

- Fatto: colonna `race.review_started_by_user_id` (migrazione `a9c3e7b1d5f0` e modello `Race`).
- Fatto: revisore unico (`_reviewed_race` in `services/card_judge.py`: revisione attiva e aperta dall'utente che agisce, altrimenti rifiuto), annullamento della giocata (anche già consumata, con ritorno della carta dalla pool), bonus dalla pool e **rimozione di una carta dall'inventario del pilota** con ritorno alla pool (`remove_card`, rotta `POST .../card-removal`, commit `86e5893` e correzione `1bfba4b`).
- Fatto: conferma automatica delle revisioni scadute (`settle_expired_reviews` in `services/race_review.py`), riapertura dell'admin sull'ultima gara (`reopen_review`, `is_last_race`), rotte `GET .../review` e `POST .../review/reopen`, campo `is_last_race` in `RaceReviewRead`, traduzione HTTP degli errori nuovi (403 per chi non è admin, 409 per gara non ultima o revisione non confermata). Commit `76e97cf` (rotte) e `c8c5c61` (test).
- Rimozione, regole: serve la revisione attiva del revisore; 409 se il campionato non ha una pool sponsor, se la carta non è nell'inventario del pilota o se tutte le copie sono impegnate in giocate attive (il revisore deve prima annullarle); 404 per pilota inesistente o eliminato; 403 per pilota non iscritto. La copia va dall'inventario sponsor del pilota alla pool sponsor del campionato in un solo commit.
- Rimozione, nota tecnica: `_without_one_copy` (in `services/card_gift.py`) confronta le carte per identità (`is`), quindi `remove_card` le passa lo stesso oggetto presente nella lista dell'inventario e non una copia.
- Test: 13 test della rimozione in `backend/tests/test_card_judge.py`; i test di stato, scadenza e riapertura sono in `backend/tests/test_race_review_reopen.py`; 6 test dell'annullo di giocate già consumate dopo la riapertura (carta che torna dalla pool, 409 se la pool ha perso la carta, 409 senza revisione attiva o con un altro revisore, nuova conferma che consuma solo la giocata rimasta) in `backend/tests/test_card_judge_reopen.py` (commit `55fbcea`). La scadenza è provata portando la data di apertura a 20 minuti prima direttamente nel database, senza orologio finto. Esito verde della CI sulla pull request #9 (backend pytest, migrazioni, frontend) letto da GitHub il 13 ottobre 2026 sull'esecuzione partita subito dopo il commit `55fbcea`; lo SHA esatto dell'esecuzione non è riportato dall'elenco dei controlli.
- Da fare: frontend del revisore (13d: riepilogo con immagini, annullo, bonus, rimozione, riapertura per l'admin con il prefisso dei percorsi `/media/cards/`); riallineamento di `PROJECT_STATUS.md` e `PROJECT_SPEC.md`.

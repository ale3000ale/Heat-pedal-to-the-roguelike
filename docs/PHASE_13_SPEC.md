# Fase 13 — Carte sponsor e amministrazione delle carte

> STATO: DECISIONI APPROVATE DALL'AUTORE (11-12 ottobre 2026). Regole della revisione aggiornate il 12 ottobre 2026 (revisore unico, scadenza, rimozione carte).
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

### Stato della gara: "in revisione"

- La revisione si avvia quando il giudice o l'admin preme **termina gara** nella pagina della gara, prima dell'inserimento dei risultati. Chi la avvia diventa il **revisore**.
- In revisione i giocatori non possono più giocare, annullare carte sponsor né usare il tasto S.
- **Revisore unico**: solo il revisore vede la revisione e può agire. Qualsiasi altro utente, giudici e admin compresi, non vi accede e riceve un rifiuto (409). Nemmeno l'admin subentra durante la revisione.
- Se il revisore se ne va e rientra, riprende la propria revisione dalla pagina della gara.
- **Scadenza**: 15 minuti dall'inizio della revisione (non dall'ultima azione, valore di configurazione). Alla prima richiesta successiva la revisione risulta scaduta: la gara torna allo stato **in corso**, revisore e data di avvio sono azzerati e si attende una nuova revisione. Nessun processo in background. Dopo la scadenza, se serve, l'admin sistema le carte.
- Il revisore può rilasciare la revisione in qualsiasi momento: la gara torna in corso.
- Azioni del revisore (solo in revisione): annullare una carta giocata, assegnare una carta bonus dalla pool, **rimuovere** una carta sponsor dall'inventario di un pilota quando è stata assegnata per errore o non è stata giocata. La carta rimossa torna nella pool, come se fosse stata giocata e il giocatore si fosse dimenticato di toglierla.
- Il riepilogo e le correzioni avvengono un attimo prima della chiusura (inserimento dei risultati).

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

- Alla chiusura le carte giocate escono in modo definitivo dall'inventario dei piloti e tornano nella copia di pool sponsor del campionato.
- Una gara annullata non è prevista. Le correzioni dei risultati restano come da `PROJECT_SPEC.md` (solo admin).

### Correzioni dell'admin dopo la chiusura

- L'admin, a gara chiusa, può sistemare le carte sponsor come faceva il giudice nella revisione.
- Il ripristino di una carta è possibile solo se la pool ha ancora una copia uguale disponibile; altrimenti viene rifiutato con un messaggio chiaro.

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
| 13b | Backend: stato "in revisione" con revisore unico e scadenza di 15 minuti, riepilogo, correzione, rimozione e bonus (solo in revisione), tasto S, notifica di carta ottenuta |
| 13c | Frontend giocatore: sezioni a scomparsa per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor" |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, revisione nella pagina della gara con immagini, correzioni |
| — | Dopo la 13d: riallineamento di tutti i documenti (richiesta dell'autore) |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate |
| 13g | Documenti e test finali, unione in `main` |

Ogni sottofase parte solo dopo l'approvazione dell'autore, con l'elenco dei file previsti.

## Avanzamento della 13b

- Fatto: colonna `race.review_started_by_user_id` (migrazione `a9c3e7b1d5f0` e modello `Race`), test verdi.
- Da fare: servizi e rotte con revisore unico, scadenza e rimozione carta; poi test e riallineamento degli altri documenti.

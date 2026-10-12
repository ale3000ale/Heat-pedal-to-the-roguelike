# Fase 13 — Carte sponsor e amministrazione delle carte

> STATO: DECISIONI APPROVATE DALL'AUTORE (11-12 ottobre 2026). Nessun codice scritto.
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

### Stato della gara: "in revisione"

- Quando il giudice o l'admin apre il riepilogo, la gara passa allo stato **in revisione**.
- In revisione i giocatori non possono più giocare né annullare carte sponsor.
- Il riepilogo e le correzioni avvengono un attimo prima della chiusura (inserimento dei risultati).

### Giudice e admin

- Durante la gara hanno l'elenco completo dei piloti iscritti; accanto al nome un tasto **S** assegna una carta sponsor **casuale** dalla pool sponsor del campionato, dopo conferma. È un regalo: non costa punti sponsor.
- Il tasto S funziona solo con una gara in corso. Con la pool sponsor vuota è disabilitato, con un avviso.
- La carta entra nell'inventario del pilota e l'inventario si aggiorna in tempo reale (controllo periodico ogni pochi secondi, senza canali continui).
- Al giocatore compare un popup con la carta ottenuta e il testo "Hai ottenuto una carta sponsor".
- Il giudice (e l'admin) non vede quale carta è uscita: la vede solo nel riepilogo finale.
- Nel riepilogo (con immagini) vedono le carte sponsor giocate da tutti i piloti, possono ripristinare una carta giocata per errore e assegnarne altre come bonus.
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
| 13b | Backend: stato "in revisione", riepilogo, correzione e bonus, tasto S, notifica di carta ottenuta |
| 13c | Frontend giocatore: sezioni a scomparsa per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor" |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, riepilogo con immagini, correzioni |
| — | Dopo la 13d: riallineamento di tutti i documenti (richiesta dell'autore) |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate |
| 13g | Documenti e test finali, unione in `main` |

Ogni sottofase parte solo dopo l'approvazione dell'autore, con l'elenco dei file previsti.

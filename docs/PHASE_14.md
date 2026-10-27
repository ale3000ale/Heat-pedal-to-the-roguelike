# Fase 14 — Sistemazione generale e miglioramenti

Ultimo aggiornamento: 2026-10-19

Documento di fase da accorpare in `PROJECT_STATUS.md`, `PROJECT_SPEC.md` e `README.md`.

## Stato

- Ramo: `phase-14`, creato da `main` (commit `55c2a9a`).
- Pull request: #13, in bozza, non unita a `main`.
- Regola: nessun merge senza richiesta esplicita dell'autore.

## Righe per PROJECT_STATUS.md

| Fase | Contenuto | Stato |
|---|---|---|
| 14 | Sistemazione generale, modifiche di vivibilità e miglioramenti | In corso nel ramo `phase-14` (pull request #13 in bozza, non unita a `main`) |
| 14a | Frontend: pagina Campionati con tre sezioni a scomparsa "Iscritto", "Attivi" e "Chiusi" | Completata nel ramo `phase-14` (commit `bed217f` e `f63510a`; CI verde, riferita dall'autore il 2026-10-18) |
| 14b | Frontend: iscrizione di un pilota dal dettaglio del campionato in una finestra a due passi (scelta e conferma) | Completata nel ramo `phase-14` (commit `8a575a7`; CI verde, riferita dall'autore il 2026-10-18) |
| 14c | Frontend: tasto "Vedi mazzo" nel dettaglio del campionato, con scelta del pilota se ne hai più di uno | Completata nel ramo `phase-14` (commit `81ceed6`; CI verde, riferita dall'autore il 2026-10-18) |
| 14d | Frontend: pagina del pilota con freccia "Indietro", mazzo fisso a destra, inventario a sinistra e carte compatte | Completata nel ramo `phase-14` (commit `548967d`, `d756715` e `178acb5`; aspetto approvato dall'autore il 2026-10-19; esito della CI non ancora riferito) |
| 14e | Frontend: sezione "Le tue carte sponsor" nel dettaglio del campionato, per giocare e annullare le carte nella gara in corso | Nel ramo `phase-14` (commit precedenti a `b58a3fe`, non elencati qui; esito della CI non ancora riferito) |
| 14f | Frontend: tasto "S" accanto ai piloti, per assegnare una carta sponsor casuale (solo giudice e admin) e banner "Hai ottenuto una carta sponsor" per il giocatore | Nel ramo `phase-14` (commit precedenti a `b58a3fe`, non elencati qui; esito della CI non ancora riferito) |
| 14g | Backend e frontend: annullo del tasto S entro 60 secondi, banner più stretto, messaggio sotto la riga del pilota | Nel ramo `phase-14` (commit `b58a3fe` backend e `3676025` frontend; CI non ancora riferita) |
| 14h | Frontend: la lista delle carte giocabili si rilegge a ogni controllo periodico | Nel ramo `phase-14` (commit `8bce344`; CI non ancora riferita) |

## 14a — Campionati con sezioni a scomparsa

Regole richieste dall'autore:

- "Iscritto": campionati attivi con almeno un pilota dell'utente loggato (anche per l'admin).
- "Attivi": gli altri campionati attivi, senza ripetere quelli già in "Iscritto".
- "Chiusi": tutti i campionati chiusi, anche quelli a cui l'utente partecipava.
- All'apertura della pagina è aperta solo "Iscritto" se c'è almeno un pilota iscritto, altrimenti solo "Attivi"; poi l'utente apre e chiude le sezioni liberamente.
- Le sezioni vuote restano visibili con il messaggio "Nessun campionato…".

File:

- `frontend/src/lib/championship/championship-groups.ts`: logica che divide i campionati nelle tre sezioni e sceglie quella aperta.
- `frontend/src/lib/championship/championship-groups.spec.ts`: 7 test Vitest.
- `frontend/src/routes/championships/+page.svelte`: pagina con tre elementi `<details>` e conteggio.

Dati: `GET /api/championships` e `GET /api/pilots` (solo i piloti dell'utente loggato). Backend, database, migrazioni e CI non sono stati modificati.

Commit: `bed217f` (funzione) e `f63510a` (formattazione Prettier).

Verifiche: CI verde sulla pull request #13, riferita dall'autore e non letta dall'assistente. L'assistente non ha eseguito controlli in locale.

Limite noto: `GET /api/pilots` restituisce al massimo 100 piloti per richiesta; con più piloti la sezione "Iscritto" potrebbe essere incompleta.

Da verificare a mano: apertura iniziale delle sezioni, comportamento per admin e giudice, sezioni vuote.

## 14b — Iscrizione del pilota in una finestra

Regole richieste dall'autore:

- La card "Iscrivi un tuo pilota" del dettaglio campionato diventa un pulsante "Iscrivi un pilota" nell'intestazione, accanto a "Negozio", che apre una finestra.
- Il pulsante c'è solo in un campionato attivo in cui l'utente non ha ancora piloti iscritti: sparisce nei campionati chiusi e in quelli dove ha già un pilota iscritto.
- La finestra ha due passi: prima si sceglie il pilota, poi si conferma. La conferma avvisa che l'iscrizione reimposta inventari, mazzo da gioco, oro, sponsor e punti.
- I piloti proposti hanno un team e non sono iscritti a nessun campionato attivo (anche a un altro).
- Senza piloti iscrivibili la finestra mostra "Nessun tuo pilota può essere iscritto.".
- Gli errori del backend (per esempio 409) compaiono nella finestra.
- Dopo l'iscrizione la pagina ricarica il campionato, la classifica e l'elenco dei piloti dell'utente.

File:

- `frontend/src/lib/championship/enroll-candidates.ts`: `enrollablePilots` (piloti iscrivibili) e `canShowEnroll` (visibilità del pulsante).
- `frontend/src/lib/championship/enroll-candidates.spec.ts`: 8 test Vitest.
- `frontend/src/lib/components/pilots/enroll-pilot-dialog.svelte`: la finestra a due passi, basata su `modal.svelte`.
- `frontend/src/routes/championships/[id]/+page.svelte`: pulsante, finestra e ricarica dei dati.

Dati: `POST /api/championships/{id}/pilots` e `GET /api/pilots`. Backend, database, migrazioni e CI non sono stati modificati.

Commit: `8a575a7`.

Verifiche: CI verde sulla pull request #13, riferita dall'autore e non letta dall'assistente. L'assistente non ha eseguito controlli in locale.

Limiti noti:

- Con un pilota già iscritto non si possono aggiungere altri piloti allo stesso campionato dalla pagina (scelta dell'autore).
- `GET /api/pilots` restituisce al massimo 100 piloti per richiesta: con più piloti l'elenco dei candidati potrebbe essere incompleto.

Da verificare a mano: i due passi della finestra, l'errore del backend, il pulsante nei campionati chiusi e in quelli con un pilota iscritto.

## 14c — Tasto per vedere il mazzo

Regole richieste dall'autore:

- Nel dettaglio del campionato c'è il pulsante "Vedi mazzo", nell'intestazione accanto a "Iscrivi un pilota" e "Negozio".
- Il pulsante c'è solo in un campionato attivo in cui l'utente ha almeno un pilota iscritto; nei campionati chiusi non c'è.
- Con un solo pilota iscritto il pulsante porta direttamente alla pagina `/pilots/[id]`.
- Con più piloti iscritti si apre la finestra "Mazzo di quale pilota?" e un clic su un nome porta alla pagina di quel pilota.
- La pagina del pilota è quella esistente (mazzo da gioco e inventario, con spostamento delle carte); la sua grafica è cambiata nella 14d.

File:

- `frontend/src/lib/draft/deck/deck-access.ts`: `deckAction`, che decide se il pulsante compare e cosa fa (`hidden`, `open`, `choose`).
- `frontend/src/lib/draft/deck/deck-access.spec.ts`: 4 test Vitest.
- `frontend/src/lib/components/pilots/pilot-picker-dialog.svelte`: finestra di scelta del pilota, basata su `modal.svelte`.
- `frontend/src/routes/championships/[id]/+page.svelte`: pulsante, finestra e navigazione.

Dati: nessuna nuova chiamata; usa l'elenco dei piloti già caricato dalla pagina. Backend, database, migrazioni e CI non sono stati modificati.

Commit: `81ceed6`.

Verifiche: CI verde sulla pull request #13, riferita dall'autore e non letta dall'assistente. L'assistente non ha eseguito controlli in locale.

Limite noto: la freccia in alto della pagina del pilota ora torna alla pagina precedente (vedi 14d).

Da verificare a mano: pulsante con un pilota e con più piloti iscritti, assenza del pulsante nei campionati chiusi e in quelli senza piloti iscritti.

## 14d — Pagina del pilota

Regole richieste dall'autore:

- La freccia in alto riporta alla pagina precedente (per esempio il campionato da cui si è aperto il mazzo), non sempre all'elenco dei piloti.
- Da `lg` in su l'inventario sta a sinistra e scorre con la pagina; il mazzo da gioco sta a destra e resta fisso, con scorrimento interno se è più alto dello schermo.
- Le carte sono più piccole di prima (circa metà); l'inventario ha 6 colonne da `sm` in su; il mazzo ha 4 colonne.
- Il mazzo è leggermente più grande: la colonna del mazzo vale 3/8 della larghezza (inventario 5/8).
- Sotto `lg` (telefono e tablet) il mazzo sta sopra e l'inventario sotto, senza blocchi fissi.

File:

- `frontend/src/routes/pilots/[id]/+page.svelte`: layout a due colonne (`lg:grid-cols-[minmax(0,5fr)_minmax(0,3fr)]`), contenitore `max-w-6xl`, freccia "← Indietro" con `goBack`.
- `frontend/src/lib/components/cards/CardTile.svelte`: nuova proprietà opzionale `compact` (nome in piccolo sotto l'immagine e copie come badge sull'immagine); senza `compact` l'aspetto non cambia.

Scelta tecnica: la freccia usa `history.back()` e, se non c'è una pagina precedente, va a Team e piloti. Il parametro `?from=` non è stato usato perché la regola di lint `svelte/no-navigation-without-resolve` vieta di aggiungere una query a `resolve()`. L'etichetta è sempre "Indietro".

Misure stimate a 1152 px di pagina: carte del mazzo circa 84 px, carte dell'inventario circa 95 px.

Dati: nessuna nuova chiamata. Backend, database, migrazioni e CI non sono stati modificati.

Commit: `548967d` (layout, carte compatte, freccia), `d756715` (pagina più larga, inventario a 6 colonne) e `178acb5` (colonna del mazzo 3/8).

Verifiche: aspetto approvato dall'autore il 2026-10-19. L'esito della CI non è ancora stato riferito. L'assistente non ha eseguito controlli in locale.

Limiti noti:

- Il menu in alto resta largo `max-w-5xl`, quindi in questa pagina il contenuto è più largo del menu.
- Le misure in pixel sono calcoli teorici.

Da verificare a mano: freccia dal campionato e dall'elenco piloti, mazzo fisso con inventario lungo, mazzo pieno (15 carte), blocco del mazzo durante una gara.

## 14e — Carte sponsor in gara

Regole:

- Nel dettaglio del campionato compare la card "Le tue carte sponsor" solo se il campionato è attivo, c'è una gara in corso (una gara senza classifica) e l'utente ha almeno un pilota iscritto.
- Ogni pilota iscritto ha una sezione a scomparsa; con un solo pilota la sezione nasce aperta.
- La sezione mostra le carte sponsor giocabili (con le copie ancora disponibili), il tasto "Annulla ultima" con il numero di annullamenti rimasti (massimo 5 consecutivi) e l'elenco delle carte giocate nella gara.
- Giocare una carta chiede conferma. Con la gara in revisione non si possono più giocare né annullare carte.
- Gli errori del backend compaiono sotto i pulsanti.

File:

- `frontend/src/lib/components/pilots/pilot-card-plays.svelte`: la sezione di un pilota.
- `frontend/src/lib/cards/card-play-api.ts`: servizio API (stato delle giocate, gioca, annulla).
- `frontend/src/lib/cards/card-play-types.ts`: tipi `CardPlayState`, `AvailableCard`, `CardPlay`, `CardGift`, `CardPollSetting`.
- `frontend/src/routes/championships/[id]/+page.svelte`: la card e il collegamento con le altre parti.

Dati: `GET /api/championships/{id}/card-plays?pilot_id=`, `POST /api/championships/{id}/card-plays` e `POST /api/championships/{id}/card-plays/undo`.

Verifiche: l'assistente non ha eseguito controlli in locale; l'esito della CI non è ancora stato riferito.

Da verificare a mano: giocare e annullare una carta, il limite di 5 annullamenti, il blocco in revisione, la sezione aperta con un solo pilota.

## 14f — Tasto S e banner della carta ottenuta

Regole:

- Giudice e admin vedono il tasto "S" accanto a ogni pilota della classifica, solo in un campionato attivo con una gara in corso. Il tasto chiede conferma e assegna una carta sponsor casuale al pilota.
- Chi preme S non vede quale carta è uscita: il banner "Hai ottenuto una carta sponsor" lo vede solo il giocatore del pilota.
- Il banner si chiude solo con la X (il clic fuori e il tasto Esc non fanno nulla) e ha lo sfondo sfocato; alla chiusura le notifiche risultano viste.
- Il giocatore riceve la notifica con un controllo periodico, attivo solo se ha piloti iscritti a un campionato attivo. L'intervallo è impostato dall'admin da 1 a 10 secondi (predefinito 5).
- Gli errori (per esempio la pool sponsor vuota) compaiono sotto il tasto.

File:

- `frontend/src/lib/components/pilots/pilot-gift-button.svelte`: tasto S e messaggio.
- `frontend/src/lib/components/cards/card-gift-popup.svelte`: banner della carta ottenuta.
- `frontend/src/lib/components/shared/modal.svelte`: opzioni `closeOnOutside`, `blur`, `wide`, `narrow`.
- `frontend/src/lib/cards/card-poll.svelte.ts`: lettura dell'intervallo e controllo periodico.
- `frontend/src/lib/cards/card-play-api.ts`: `giveRandomCard`, `fetchUnseenGifts`, `markGiftsSeen`, `fetchCardPoll`, `saveCardPoll`.

Dati: `POST /api/championships/{id}/card-gifts`, `GET /api/championships/{id}/card-gifts?pilot_id=`, `POST /api/championships/{id}/card-gifts/seen`, `GET` e `PUT /api/admin/card-poll`.

Verifiche: l'assistente non ha eseguito controlli in locale; l'esito della CI non è ancora stato riferito.

Limite noto: i test del backend esistenti mostrano che la rotta del tasto S accetta anche un giocatore sul proprio pilota; l'interfaccia lo nasconde. Una restrizione a admin e giudici nel backend non è stata decisa.

Da verificare a mano: tasto S per admin, giudice e giocatore, banner con più carte, chiusura solo con la X, errore a pool vuota.

## 14g — Annullo del tasto S e banner più stretto

Regole richieste dall'autore:

- Dopo l'assegnazione, per 60 secondi, chi ha premuto S vede il tasto "Annulla (N s)". L'annullo è visibile solo nella sessione di chi ha premuto S (scelta A).
- Il messaggio "Carta assegnata a …" va sotto la riga del pilota, a tutta larghezza, nel campionato e nella pagina della gara.
- Il banner è una finestra stretta (`max-w-xs`); la carta è larga 192 px (+25% rispetto a circa 152 px) e il nome va a capo senza troncarsi.
- Se l'annullo riesce, la carta torna dall'inventario del pilota alla pool sponsor e la notifica sparisce.

Backend:

- Nuova rotta `POST /api/championships/{id}/card-gifts/{gift_id}/undo` (risposta 204), con la funzione `undo_gift` in `services/card_gift.py`.
- Regole: solo admin o giudice (403 per gli altri); solo entro 60 secondi, altrimenti 409; non se la carta è già stata giocata (409); solo nella gara in corso; 404 se l'assegnazione non esiste.
- Test: `backend/tests/test_card_gift_undo.py`, 10 test.

Frontend:

- `frontend/src/lib/cards/gift-undo.ts`: `UNDO_SECONDS` e `secondsLeft`; `frontend/src/lib/cards/gift-undo.spec.ts`: 3 test Vitest.
- `frontend/src/lib/cards/card-play-api.ts`: `undoGift`.
- `frontend/src/lib/components/pilots/pilot-gift-button.svelte`: contatore, tasto Annulla e messaggio sotto la riga.
- `frontend/src/lib/components/shared/modal.svelte`: opzione `narrow`.
- `frontend/src/lib/components/cards/card-gift-popup.svelte`: banner stretto.

Commit: `b58a3fe` (backend) e `3676025` (frontend). Il database e le migrazioni non sono stati modificati.

Verifiche: l'assistente non ha eseguito pytest, Prettier, lint, type-check né test; l'esito della CI non è ancora stato riferito.

Limiti noti:

- Il vincolo "solo chi ha premuto S" è garantito dall'interfaccia, non dal backend, che non salva l'autore dell'assegnazione. Un altro admin o giudice che conosca l'id potrebbe annullare entro i 60 secondi.
- Il contatore dei 60 secondi vive nella pagina: ricaricandola il tasto Annulla sparisce, anche se il backend accetterebbe ancora l'annullo.

Da verificare a mano: annullo entro 60 secondi, tasto che sparisce dopo 60 secondi, annullo dopo che la carta è stata giocata (409), messaggio sotto la riga su telefono.

## 14h — Lista delle carte che si aggiorna da sola

Problema: se una assegnazione veniva annullata, la carta restava nella lista del giocatore e si poteva premere, con errore. La lista si rileggeva solo all'apertura della sezione e quando arrivava una carta nuova.

Soluzione:

- A ogni controllo periodico la pagina del campionato aumenta `giftTick`, anche con il banner aperto, e le sezioni aperte rileggono le carte giocabili. Un annullo o una carta nuova compaiono entro l'intervallo impostato dall'admin (1–10 secondi, predefinito 5).
- La rilettura `refresh()` in `pilot-card-plays.svelte` è silenziosa: non mette i pulsanti in "occupato", ignora gli errori di rete (riprova al controllo successivo), non parte mentre l'utente sta agendo e scarta la risposta se nel frattempo è successa un'azione (contatore `stateVersion`).
- Se il backend rifiuta una carta appena annullata, la lista si rilegge subito.

File modificati: `frontend/src/lib/components/pilots/pilot-card-plays.svelte` e `frontend/src/routes/championships/[id]/+page.svelte`. Backend, database e migrazioni non sono stati modificati.

Commit: `8bce344`.

Verifiche: l'assistente non ha eseguito controlli in locale; l'esito della CI non è ancora stato riferito.

Limiti noti:

- Non è un aggiornamento istantaneo: al massimo l'intervallo di controllo.
- C'è una richiesta in più (`GET card-plays`) per ogni sezione aperta a ogni controllo, solo con una gara in corso e piloti iscritti.

Da verificare a mano: annullo di un'assegnazione con la sezione del giocatore aperta, assenza di sfarfallio dei pulsanti durante il controllo, giocare una carta mentre arriva un controllo.

## Aperto

- Revisione dell'interfaccia su telefono: l'autore segnala che "molte cose non funzionano"; serve l'elenco delle pagine e dei sintomi prima di intervenire.
- Aggiornamento più reattivo senza richieste continue: l'autore sta valutando gli Server-Sent Events (SSE). Nessuna decisione presa. Prima di un eventuale piano vanno controllati il tipo di login (cookie o token), la versione di FastAPI nel `uv.lock` e il numero di worker del server. Alternativa più leggera: fermare il controllo con la scheda nascosta e usare un contatore di versione o un ETag.
- Decisione sul tasto S nel backend: restringerlo ad admin e giudici o lasciare anche i giocatori sul proprio pilota.

## Da riallineare dopo la CI verde

- `PROJECT_STATUS.md`: righe 14, 14a–14h e una voce nella sezione Frontend (e per 14g anche nel Backend) per ciascuna; il file è troppo lungo per essere riscritto dal connettore e va aggiornato a parte.
- `PROJECT_SPEC.md`: sezioni dei campionati, dell'iscrizione dei piloti, del mazzo, della pagina del pilota, delle carte sponsor in gara, del tasto S e della rotta di annullo (non letto dall'assistente).
- `README.md`, `SETUP.md`, `DATABASE.md`, `SCRIPTS.md`: da controllare; la rotta nuova non cambia lo schema del database, quindi `DATABASE.md` resta invariato salvo verifica (non letti dall'assistente).

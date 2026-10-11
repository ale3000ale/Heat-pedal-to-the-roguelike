> **STATO: AGGIORNATO L'11 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio è in `SHOP_DESIGN.md` e la sua
> traduzione tecnica in `SHOP_SCHEMA.md`.

# Domande aperte — Heat

## Negozio (fase 12)

Nessuna domanda aperta sul funzionamento. Il backend (12a-12c) è approvato; restano
il frontend del giocatore (12d), il frontend admin (12e) e i documenti finali (12f).

- **Deploy online**: un solo server con pochi worker, perché SQLite accetta una sola
  scrittura alla volta. Con un altro database servirà un blocco sulla riga del pilota
  (`SELECT ... FOR UPDATE`).
- **Template di negozio senza pacchetti**: non è utilizzabile alla creazione del
  campionato; l'avviso (triangolo giallo) va riportato in `SHOP_SCHEMA.md`.
- **Strappo della busta e riepilogo finale**: l'effetto e il riepilogo non sono ancora
  stati visti a schermo; se non convincono, si ritocca solo il CSS e il markup di
  `pack-reveal.svelte` (vedi decisioni dell'11 ottobre).
- **Copie della stessa carta nel riepilogo**: oggi una carta uscita più volte compare
  una volta per ogni estrazione; va deciso se raggrupparla con il numero di copie
  (da verificare in `CardTile.svelte`, non letto).
- **Tasto Esc**: va deciso se debba chiudere la finestra prima del riepilogo; la
  decisione dell'autore parla solo di X e di clic fuori (da verificare in
  `modal.svelte`, non letto).

Decisioni dell'11 ottobre 2026 (non più aperte):

- Nell'apertura del pacchetto la busta ha come texture l'immagine del pacchetto
  acquistato e si apre con uno strappo: la striscia superiore se ne va e la busta
  resta tagliata in alto. È solo CSS, senza test dedicati; i dettagli sono in
  `SHOP_DESIGN.md` (sezione 6) e `SHOP_SCHEMA.md`.
- Dopo la busta le carte si vedono una alla volta, già scoperte: ogni tocco fa
  scorrere la carta a sinistra mostrando la seguente (non più tutte in fila e
  coperte da girare).
- Dopo l'ultima carta un altro tocco apre il riepilogo finale, con tutte le carte
  ottenute e la loro immagine. Il tasto "Salta" porta direttamente al riepilogo da
  qualsiasi fase. Fino al riepilogo la finestra si chiude solo con la X; dal
  riepilogo anche toccando fuori. Questo chiude la questione del blocco della
  finestra durante l'apertura.

Decisioni del 10 ottobre 2026 (non più aperte):

- La ricarica delle pool di base chiede conferma prima di togliere carte: elenca ogni
  carta e dice se è nella copia di pool di un campionato attivo.
- L'elenco dei campionati con negozio per la barra di navigazione e per la scelta del
  pilota serve ed esiste: `GET /api/me/shops` (`api/shop_me.py`) restituisce i
  campionati a cui l'utente partecipa con i piloti iscritti. Una versione precedente di
  questo file lo dava per non necessario; la correzione è stata fatta dopo la lettura
  del codice.
- Nel negozio lo storico resta una pagina separata e l'inventario un solo pulsante
  (invece del popup con sezioni espandibili e del pulsante in ogni area previsti in
  `SHOP_DESIGN.md`).
- Gli acquisti si serializzano con un blocco sul database (`BEGIN IMMEDIATE` su SQLite).
- La pool sponsor è usata dai pacchetti per estrarre le carte sponsor.
- I pacchetti nuovi costano 10 oro oppure 2 sponsor.

## Fase futura (non blocca la fase 12)

- **Carte sponsor a consumo**: possono essere usate in gara e vengono cancellate
  all'uso; in gara se ne possono ottenere; a fine gara l'inventario sponsor può
  cambiare. Servono: quando e come si usano, come si registra il consumo, come
  entrano nel mazzo da gioco (limite di 15 carte) e come si assegnano in gara.

## Altre domande rinviate

- **Amministrazione carte**: quali funzioni per aggiungere nuove carte (file immagine, record in `DeckPrototype` o altra entità)?
- **Spareggio sportivo**: criterio a pari punti. L'ordine alfabetico serve solo come stabilizzatore di visualizzazione.
- **Pool reale delle carte**: il prototipo `default` ha pool vuota. Servono elenco, valori e percorsi immagini delle carte.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.

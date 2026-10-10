> **STATO: AGGIORNATO IL 10 OTTOBRE 2026 (fase 12).**
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

Decisioni del 10 ottobre 2026 (non più aperte):

- La ricarica delle pool di base chiede conferma prima di togliere carte: elenca ogni
  carta e dice se è nella copia di pool di un campionato attivo.
- L'elenco dei campionati con negozio nella barra di navigazione non serve: la pagina
  del negozio indica già i campionati del giocatore e chiede con quale pilota entrare.
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

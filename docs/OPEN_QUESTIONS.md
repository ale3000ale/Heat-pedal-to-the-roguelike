> **STATO: AGGIORNATO L'8 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio, con le risposte dell'autore,
> è in `SHOP_DESIGN.md` (bozza). Qui restano solo i punti non ancora decisi.

# Domande aperte — Heat

## Negozio (fase 12)

Tutto il resto è deciso e scritto in `SHOP_DESIGN.md`.

1. **Scelta del template di negozio**: si sceglie solo nel modulo di creazione
   del campionato, oppure anche dopo, con un pulsante "Applica template" nelle
   impostazioni del campionato? Se anche dopo, aggiunge i pacchetti a quelli già
   presenti o li sostituisce? Si propone di aggiungerli.
2. **Eliminare un template di pacchetto usato da un template di negozio**: si
   blocca con un messaggio che elenca i template di negozio che lo usano, oppure
   lo si toglie da quei template di negozio? Si propone di bloccare.
3. **Duplicati**: lo stesso template di pacchetto può comparire più volte nello
   stesso template di negozio (per avere due copie identiche)? Si propone di no.
4. **Template di negozio senza pacchetti**: si può creare un template di negozio
   vuoto? Si propone di sì, è uguale a un negozio vuoto.

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

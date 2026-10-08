> **STATO: AGGIORNATO L'8 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio, con le risposte dell'autore,
> è in `SHOP_DESIGN.md` (bozza). Qui restano solo i punti non ancora decisi.

# Domande aperte — Heat

## Negozio (fase 12)

Tutto il resto è deciso e scritto in `SHOP_DESIGN.md`.

1. **Negozio vuoto alla creazione**: ora i pacchetti si creano a mano da un
   template con "Crea pack". Questo sostituisce l'idea iniziale che i template
   generassero da soli il negozio alla creazione del campionato. Conferma: un
   nuovo campionato nasce con il negozio vuoto?
2. **Pacchetto senza template**: con "Crea pack" si può anche creare un pacchetto
   da zero, senza partire da un template?
3. **Dimensione massima del file** dell'immagine di un pacchetto: si propone 5 MB
   (le immagini vengono comunque convertite in webp e ridimensionate).

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

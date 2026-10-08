> **STATO: AGGIORNATO L'8 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio, con le risposte dell'autore,
> è in `SHOP_DESIGN.md` (bozza). Qui restano solo i punti non ancora decisi.

# Domande aperte — Heat

## Negozio (fase 12)

Tutto il resto è deciso e scritto in `SHOP_DESIGN.md`.

1. **Template di negozio con il triangolo giallo**: se un template di negozio ha
   perso tutti i suoi template di pacchetto, si può comunque sceglierlo alla
   creazione di un campionato (il negozio nasce vuoto), oppure è disattivato
   nell'elenco? Si propone di disattivarlo.

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

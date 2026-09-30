> **STATO: BOZZA NON APPROVATA.**
>
> Domande aperte residue dopo la chiusura delle decisioni di `PROJECT_SPEC.md`.
> Nessuna blocca la prima versione.

# Domande aperte — Heat

## Domande rinviate

1. **Negozio**: quali entità, prodotti, prezzi e regole? Usa `gold` (denaro) e
   `sponsor` (punti per premi). Prima versione: placeholder
   "Funzionalità in definizione".
2. **Amministrazione carte**: quali funzioni per aggiungere nuove carte (file
   immagine, record in `DeckPrototype` o altra entità)?
3. **Spareggio sportivo**: criterio a pari punti. Per ora l'ordine alfabetico
   serve solo come stabilizzatore di visualizzazione.
4. **Pacchetti di carte**: contenuto, costo e meccanica di apertura. I
   pacchetti consumano la pool del campionato selezionato.

## Da verificare nella fase backend

- Rappresentazione nel database di inventario e mazzo da gioco (due
  riferimenti a `Deck` oppure un campo tipo).
- Conferma che `Championship.deck` è la pool del campionato.
- Nomi definitivi di tabelle e colonne nelle migrazioni Alembic, compreso il
  nome `"Championship "` con lo spazio finale.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.
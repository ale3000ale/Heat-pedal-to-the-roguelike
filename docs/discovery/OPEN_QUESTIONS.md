> **STATO: BOZZA NON APPROVATA.**
>
> Domande aperte residue dopo le 16 decisioni definitive. Le questioni già definite (relazioni, Deck/DeckPrototype, formato carte, campionati multipli, classifiche, autenticazione, ruoli, pagine, migrazioni) non sono qui ripetute. Il Negozio, l'amministrazione delle carte e lo spareggio sportivo sono esplicitamente rinviati e non bloccano la prima versione.

# Domande aperte — Heat

## Domande non bloccanti o rinviate

1. **Negozio**: quali entità, prodotti, prezzi e regole saranno introdotte quando il modulo sarà implementato? (rinviato; prima versione: solo placeholder "Funzionalità in definizione").
2. **Amministrazione carte**: quali funzioni amministrative saranno previste per aggiungere nuove carte (nuovi file immagine, nuovi record in `DeckPrototype` o altra entità)? (rinviato).
3. **Spareggio sportivo**: in caso di pari punti in classifica, quale criterio di spareggio adottare (es. migliore risultato in una gara specifica, media posizioni, ecc.)? (rinviato; per ora solo ordine alfabetico come stabilizzatore di visualizzazione, non come spareggio).

## Eventuali altre domande

Al momento non emergono altre domande realmente bloccanti per la prima versione, poiché:

- relazioni User/Team/Pilot/Deck sono definite;
- formato carte e validazione sono definiti;
- gestione campionati multipli, iscrizioni e classifiche è definita;
- autenticazione, ruoli e primo admin sono definiti;
- comportamenti delle pagine principali sono specificati;
- strategia di migrazione e uso di Alembic sono definiti.

Se desideri chiarimenti aggiuntivi su dettagli non critici (es. nomi esatti di alcuni campi audit, formati data/ora precisi, messaggi di errore specifici), puoi indicarli; non sono però prerequisiti per l'approvazione di `PROJECT_SPEC.md`.
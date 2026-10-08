> **STATO: AGGIORNATO L'8 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio, con le risposte dell'autore,
> è in `SHOP_DESIGN.md` (bozza). Qui restano solo i punti non ancora decisi.

# Domande aperte — Heat

## Negozio (fase 12)

Tutto il resto è deciso e scritto in `SHOP_DESIGN.md`.

### Inventario sponsor

1. Le carte sponsor, una volta nell'inventario sponsor, servono a qualcosa nel
   gioco (ad esempio entrano nel mazzo da gioco) oppure sono solo da collezione
   per ora?
2. Il mazzo da gioco (massimo 15 carte) pesca solo dall'inventario delle
   modifiche o anche da quello sponsor?

### Acquisto

3. L'ordine di estrazione in un pacchetto con modifiche e sponsor: prima tutte le
   modifiche e poi gli sponsor, o l'ordine in cui l'admin le ha indicate? Vale
   anche per l'ordine mostrato nell'animazione.
4. Se il filtro non trova nessuna carta in una delle due pool, ma il pacchetto
   richiede carte di quel tipo: "Terminato" (conferma).
5. L'oro o i punti sponsor del pilota sono sempre sufficienti prima dell'acquisto?
   Se il saldo non basta, il pulsante è disabilitato e mostra il prezzo (conferma).
6. Un costo può essere 0 (pacchetto gratuito)? Si propone di consentirlo.

### Gestione dei pacchetti

7. Quando l'admin modifica un pacchetto (prezzo, carte, filtro), vale subito per
   tutti gli acquisti successivi; lo storico conserva i valori del momento
   dell'acquisto: conferma.
8. Il nome del pacchetto deve essere unico nel negozio di un campionato?
9. L'ordine in cui si vedono i pacchetti nel negozio: per data di creazione, per
   prezzo o scelto dall'admin?
10. I campionati attivi già esistenti prima della fase 12 non hanno pacchetti:
    l'admin li crea a mano con "Crea pack", oppure serve un pulsante "Genera
    dai template" per i campionati esistenti?

### Storico

11. Lo storico di un pilota eliminato in modo definitivo si cancella con lui o resta
    per l'admin (come la classifica congelata, senza riferimento al pilota)?

### Immagini

12. Formato accettato per il caricamento dell'immagine del pacchetto (png, jpg,
    jpeg, webp, come per le carte) e limite di dimensione del file?

## Altre domande rinviate

- **Amministrazione carte**: quali funzioni per aggiungere nuove carte (file immagine, record in `DeckPrototype` o altra entità)?
- **Spareggio sportivo**: criterio a pari punti. L'ordine alfabetico serve solo come stabilizzatore di visualizzazione.
- **Pool reale delle carte**: il prototipo `default` ha pool vuota. Servono elenco, valori e percorsi immagini delle carte.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.

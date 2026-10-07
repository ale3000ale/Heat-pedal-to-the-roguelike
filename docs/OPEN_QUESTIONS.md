> **STATO: AGGIORNATO ALL'INIZIO DELLA FASE 12.**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md` e non vengono ripetute qui. Nessuna blocca le fasi
> già completate.

# Domande aperte — Heat

## Negozio (fase 12) — in attesa di risposta

Valute disponibili: `gold` (denaro) e `sponsor` (punti per premi), entrambi sul
pilota. Ogni campionato ha due pool di carte: modifiche e sponsor.

### Cosa si vende

1. Prodotti: solo pacchetti di carte, o anche carte singole, carte Calore, altro?
2. Premi sponsor: che premi si riscattano con i punti sponsor?
3. La pool sponsor viene usata per la prima volta dal Negozio?

### Valute e prezzi

4. Quale valuta compra cosa (gold per modifiche, sponsor per sponsor, o una sola per prodotto)?
5. Prezzi fissi nel codice o regolabili dall'admin? Per campionato o generali?
6. Valori reali delle regole dell'oro, necessari per bilanciare i prezzi.

### Pacchetti

7. Contenuto: numero di carte, tipi di pacchetto e prezzi.
8. Pesca: casuale, eventualmente pesata sulle copie rimaste nella pool?
9. Pool esaurita: saltare la carta, ridurre il pacchetto o chiudere il Negozio?
10. Il pacchetto pesca sempre dalla pool del campionato del pilota?
11. Duplicati: si sommano nell'inventario? Con quale tetto?

### Tempi e permessi

12. Quando è aperto: sempre o solo tra una gara e l'altra?
13. Chi compra: solo piloti iscritti a un campionato attivo, tramite il proprietario?
14. Chi gestisce prezzi e catalogo: solo admin o anche giudice?
15. Campionato chiuso: Negozio in sola lettura? Cosa succede agli acquisti al reset?

### Aspetti tecnici

16. Serve una tabella storico acquisti (chi, cosa, quando, prezzo)?
17. Concorrenza: stessa tecnica del blocco ottimistico dei mazzi?
18. Interfaccia: pagina `/shop` con apertura animata o lista semplice?
19. Le carte Calore (senza ancora le immagini) entrano nei pacchetti?

## Altre domande rinviate

- **Amministrazione carte**: quali funzioni per aggiungere nuove carte (file immagine, record in `DeckPrototype` o altra entità)?
- **Spareggio sportivo**: criterio a pari punti. L'ordine alfabetico serve solo come stabilizzatore di visualizzazione.
- **Pool reale delle carte**: il prototipo `default` ha pool vuota. Servono elenco, valori e percorsi immagini delle carte.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.

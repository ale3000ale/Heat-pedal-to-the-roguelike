> **STATO: AGGIORNATO L'8 OTTOBRE 2026 (fase 12).**
>
> Domande aperte dopo la chiusura della fase 11. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio descritto dall'autore è in
> `SHOP_DESIGN.md` (bozza). Qui restano solo i punti non ancora decisi.

# Domande aperte — Heat

## Negozio (fase 12)

Già chiarito dall'autore (vedi `SHOP_DESIGN.md`): un negozio per campionato,
accesso dal campionato e dalla barra, due sezioni (modifiche e sponsor),
pacchetti creati dall'admin con numero di carte modifiche e sponsor, estrazione
casuale con uguale probabilità e filtri, consumo della pool, scritta
"Terminato", apertura animata, acquisto con oro o sponsor del pilota iscritto.

### Pacchetti e prezzi

1. Un pacchetto con carte sia modifiche sia sponsor in quale sezione compare?
   Oppure ogni pacchetto è di una sola sezione?
2. Il costo è un solo importo in una sola valuta (oro o sponsor) scelta per
   pacchetto, o possono servire entrambe?
3. Il collegamento è al campionato (copia del template alla creazione, modifiche
   al template che non toccano i campionati esistenti, come per le pool)?
4. Si può eliminare o disattivare un pacchetto? Che cosa succede a quelli già
   comprati?

### Estrazione e filtri

5. I filtri su che cosa si basano? Le carte hanno solo nome, immagine e copie:
   serve una categoria o etichetta per carta (esempio "freni"), oppure un filtro
   per nome o parte del nome? Come si assegna?
6. "Uguale probabilità": uguale per ogni carta distinta o per ogni copia
   rimasta (una carta con 3 copie esce 3 volte più spesso di una con 1)?
7. Nello stesso pacchetto la stessa carta può uscire più volte?
8. Un pacchetto è "Terminato" quando le copie rimaste *nel sottoinsieme dei
   filtri* sono meno delle carte da estrarre: conferma?

### Immagini dei pacchetti

9. Le cartelle sono `pack/defaultPack` (immagine predefinita) e
   `pack/illustration` (immagini scelte): conferma. Il caricamento da interfaccia
   è previsto o si riempiono a mano come le carte?

### Accesso e permessi

10. Un utente con più piloti iscritti allo stesso campionato: con quale pilota
    compra?
11. L'admin e il giudice senza pilota iscritto vedono i negozi in sola lettura?
12. La voce "Negozio" nella barra compare sempre o solo con un pilota iscritto?
13. Il negozio è sempre aperto o si blocca durante una gara in corso?
14. In un campionato chiuso il negozio è in sola lettura (coerente con la regola
    generale)?

### Aspetti tecnici

15. Storico degli acquisti (chi, cosa, quando, prezzo, carte uscite): serve una
    tabella?
16. Concorrenza: due acquisti insieme non devono consumare due volte la stessa
    copia. Si usa una transazione unica (pagamento, estrazione, assegnazione) con
    blocco sulla pool, come il blocco ottimistico dei mazzi?
17. Se l'inventario del pilota ha già la carta, le copie si sommano? C'è un tetto?
18. Le carte sponsor vanno nello stesso inventario delle modifiche? Il popup di
    riepilogo mostra solo le carte della sezione aperta?
19. Le carte Calore (ancora senza foto, parte delle modifiche) possono uscire dai
    pacchetti?

### Valori

20. Prezzi e contenuto dei pacchetti di partenza: l'autore li imposterà dal
    pannello; servono solo i template iniziali?

## Altre domande rinviate

- **Amministrazione carte**: quali funzioni per aggiungere nuove carte (file immagine, record in `DeckPrototype` o altra entità)?
- **Spareggio sportivo**: criterio a pari punti. L'ordine alfabetico serve solo come stabilizzatore di visualizzazione.
- **Pool reale delle carte**: il prototipo `default` ha pool vuota. Servono elenco, valori e percorsi immagini delle carte.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.

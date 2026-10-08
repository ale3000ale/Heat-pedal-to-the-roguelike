> **STATO: BOZZA NON APPROVATA.** Descrive il funzionamento del Negozio come
> lo ha spiegato l'autore l'8 ottobre 2026. Quando sarà approvata, le regole
> passano in `PROJECT_SPEC.md`. Le parti ancora da decidere sono in
> `OPEN_QUESTIONS.md`.

# Negozio — progetto della fase 12

## 1. Idea generale

Ogni campionato ha il proprio negozio, basato sulle due pool del campionato
(modifiche e sponsor). Si compra con l'oro e i punti sponsor del proprio pilota
iscritto; le carte ottenute vanno nell'inventario di quel pilota.

## 2. Accesso

- Dal dettaglio del campionato, solo se l'utente partecipa con un pilota: porta
  direttamente al negozio di quel campionato.
- Dalla voce "Negozio" della barra di navigazione: elenco dei soli campionati a
  cui l'utente partecipa con un pilota; il nome del campionato apre il suo
  negozio.
- Il negozio può essere usato solo da chi partecipa al campionato, spendendo
  oro e punti sponsor del proprio pilota iscritto.

## 3. Pagina del negozio

- In alto a destra: nome del pilota iscritto a quel campionato, con il suo oro e
  i suoi punti sponsor.
- Due grandi pulsanti: sezione **modifiche** e sezione **sponsor**. Da qui si
  procede all'acquisto dei pacchetti.
- Dentro ciascuna sezione:
  - un pulsante apre un popup con il riepilogo dell'inventario del pilota: carte
    in miniatura, con in basso a destra il numero di copie; le carte di default
    (Velocità 1-4) sono escluse; il popup si chiude con una X in alto a destra;
  - nel resto della pagina ci sono i singoli pacchetti.

## 4. Pacchetti

I pacchetti li crea l'admin e ogni loro caratteristica è modificabile da lui
(l'autore deve poter bilanciarli nel tempo).

- **Contenuto**: N carte modifiche (predefinito 3) e M carte sponsor, decisi
  dall'admin. Ciascun numero può essere 0, ma la somma deve essere almeno 1.
- **Estrazione**: casuale, con uguale probabilità, dalla pool modifiche o dalla
  pool sponsor del campionato a cui il pacchetto appartiene.
- **Filtri**: di base può uscire qualsiasi carta della pool. In creazione o
  modifica l'admin può impostare dei filtri che limitano l'estrazione a un
  sottoinsieme (esempio: solo i "freni", quindi "freni carbo ceramici", "freni
  sport", ma non "carrozzeria" o "alettone anteriore").
- **Consumo della pool**: ogni carta estratta riduce di 1 le copie rimaste nella
  pool del campionato, fino a 0; con 0 copie la carta non esce più.
- **Pacchetto esaurito**: se le carte disponibili sono meno di quelle da
  estrarre, il pacchetto non si può comprare e al posto del prezzo compare la
  scritta "Terminato".
- **Caratteristiche**: immagine, nome, costo in oro o in punti sponsor, collegamento
  alla pool o al campionato (da decidere cosa conviene).
- **Immagine**: quella predefinita sta in `backend/media/cards/pack/defaultPack`;
  per sceglierne un'altra si carica o si sceglie tra quelle in
  `backend/media/cards/pack/illustration`.

## 5. Dove si creano i pacchetti

- **Gestione negozio** (nuova sezione, solo admin): qui si creano i *template*
  dei pacchetti, presenti in tutti i negozi. Alla creazione di un campionato i
  template generano il suo negozio.
- **Impostazioni del campionato**: un pulsante "Crea pack" aggiunge un pacchetto
  al solo negozio di quel campionato.

## 6. Acquisto e apertura

1. Al pagamento il pacchetto viene aperto subito: le carte sono calcolate e
   assegnate all'inventario del pilota nello stesso momento.
2. A schermo il pacchetto compare in primo piano; lo sfondo si sfoca e non è
   più cliccabile.
3. Prima si vede la busta chiusa. Un clic in qualsiasi punto la fa scorrere
   verso il basso e mostra la prima carta.
4. Ogni clic successivo fa scorrere la carta verso sinistra e mostra la
   seguente, fino all'ultima.

## 7. Note di compatibilità con la specifica attuale

- Le pool del campionato sono già copie indipendenti (`pool_deck_id` e
  `sponsor_pool_deck_id`): l'estrazione consuma queste copie e non tocca le pool
  di origine.
- Le carte oggi hanno solo `name`, `path` e `copies`: i filtri per categoria
  ("freni") richiedono di decidere come si classificano le carte (vedi
  `OPEN_QUESTIONS.md`).
- Le carte Velocità 1-4 non fanno parte di nessuna pool e restano fuori dal
  riepilogo del negozio.
- Oro e punti sponsor sono già sul pilota e si azzerano a ogni iscrizione e alla
  chiusura del campionato.

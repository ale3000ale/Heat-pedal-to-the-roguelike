> **STATO: BOZZA QUASI DEFINITIVA, NON ANCORA APPROVATA.** Descrive il
> funzionamento del Negozio come lo ha spiegato l'autore l'8 ottobre 2026, con le
> risposte alle domande. Quando sarà approvata, le regole passano in
> `PROJECT_SPEC.md`. Le parti ancora da decidere sono in `OPEN_QUESTIONS.md`.

# Negozio — progetto della fase 12

## 1. Idea generale

Ogni campionato ha il proprio negozio, basato sulle due pool del campionato
(modifiche e sponsor). Si compra con l'oro o con i punti sponsor del proprio
pilota iscritto; le carte ottenute vanno nell'inventario di quel pilota.

## 2. Accesso

- Dal dettaglio del campionato, solo se l'utente partecipa con un pilota: porta
  al negozio di quel campionato.
- Dalla voce "Negozio" della barra di navigazione, che compare solo con almeno
  un pilota iscritto: elenco dei soli campionati a cui l'utente partecipa con un
  pilota; il nome del campionato apre il suo negozio.
- **Scelta del pilota**: entrando nel negozio, se l'utente ha più piloti iscritti
  a quel campionato, gli viene chiesto con quale proseguire; con un solo pilota
  si entra direttamente con quello.
- **Admin**: può entrare in ogni negozio anche senza pilota, sempre in sola
  lettura. Il giudice senza pilota iscritto non ha accesso.
- **Gara in corso**: durante una gara in corso nel campionato il negozio si
  blocca (nessun acquisto).
- **Campionato chiuso**: il negozio non è più disponibile per gli utenti;
  l'admin può aprirlo ma in sola lettura.

## 3. Pagina del negozio

- In alto a destra: nome del pilota scelto, con il suo oro e i suoi punti sponsor.
- Due grandi pulsanti: sezione **modifiche** e sezione **sponsor**. La sezione
  distingue **solo la valuta**: i pacchetti pagati in oro stanno nella sezione
  modifiche, quelli pagati in punti sponsor nella sezione sponsor. Le carte che
  escono da un pacchetto non dipendono dalla sezione.
- Dentro ciascuna sezione:
  - un pulsante apre un popup con il riepilogo dell'inventario del pilota: carte
    in miniatura, con in basso a destra il numero di copie; le carte di default
    (Velocità 1-4) sono escluse; il popup si chiude con una X in alto a destra;
  - nel resto della pagina ci sono i pacchetti di quella sezione.
- **Ordinamento e ricerca** (scelta del singolo giocatore, non salvata nel
  campionato): di default dal meno caro al più caro; si può scegliere dal più
  caro al meno caro, in ordine alfabetico o alfabetico inverso. In più c'è una
  barra di ricerca per nome.
- Un pulsante **Storico** (solo nel negozio) apre un popup con tutti gli acquisti
  dei propri piloti iscritti, divisi per pilota in sezioni espandibili.
- Un pacchetto il cui costo supera il saldo del pilota ha il pulsante
  disabilitato, con il prezzo ben visibile.

## 4. Pacchetti

I pacchetti li crea l'admin e ogni loro caratteristica è modificabile da lui,
anche per i pacchetti nati da un template (l'autore deve poter bilanciarli nel
tempo).

- **Caratteristiche**: nome, immagine, costo e valuta (oro o punti sponsor),
  numero di carte da estrarre dalla pool modifiche e numero di carte da estrarre
  dalla pool sponsor, filtro per nome (attivabile o no).
- **Costo e valuta**: li decide l'admin alla creazione (nel template o nelle
  impostazioni del pacchetto) e quando modifica il pacchetto; la valuta decide in
  quale sezione compare il pacchetto. Il costo deve essere maggiore di 0.
- **Contenuto**: l'admin sceglie quante carte estrarre da ciascuna pool. Il
  numero per le modifiche è predefinito a 3. Ciascun numero può essere 0, ma la
  somma deve essere almeno 1. Un pacchetto può quindi dare carte di entrambi i
  tipi.
- **Filtro**: unico per pacchetto, attivabile o disattivabile, applicato a
  entrambe le pool. Si basa solo sul nome della carta, senza distinguere le
  maiuscole; si possono inserire più nomi separati da virgola. Con il filtro
  disattivato può uscire qualsiasi carta della pool di riferimento. Esempio: con
  il filtro "freni" escono "freni carbo ceramici" e "freni sport", ma non
  "carrozzeria".
- **Estrazione**: casuale, **per ogni copia** rimasta con uguale probabilità (pool
  con A 3 copie, B 1 copia, C 6 copie: A 30%, B 10%, C 60%). Si estrae una carta
  alla volta e dopo ognuna la probabilità si ricalcola sulle copie rimaste. La
  stessa carta può uscire più volte nello stesso pacchetto se ha più copie.
- **Consumo della pool**: ogni carta estratta riduce di 1 le copie rimaste nella
  pool del campionato, fino a 0; con 0 copie non esce più.
- **Pacchetto esaurito**: se le copie rimaste nel sottoinsieme filtrato sono meno
  di quelle da estrarre (per una delle due pool), il pacchetto non si compra e al
  posto del prezzo compare "Terminato".
- **Modifica**: una modifica al pacchetto vale subito per gli acquisti successivi;
  lo storico conserva i valori del momento dell'acquisto.
- **Nome**: ogni pacchetto ha il suo nome; non è richiesta l'unicità.
- **Eliminazione**: si possono eliminare i pacchetti di un campionato e i
  template. Eliminare non ha effetti sui pacchetti già aperti, perché le carte sono
  già state distribuite.
- **Immagine**: quella predefinita sta in `backend/media/pack/defaultIllustration`.
  Per sceglierne un'altra si carica un file dall'interfaccia (finisce in
  `backend/media/pack/illustration`) o si sceglie tra quelle già presenti. Si
  accettano png, jpg/jpeg e webp; tutte vengono convertite in webp e
  normalizzate alle stesse dimensioni delle carte (scatola massima 560x870 px).

## 5. Dove si creano i pacchetti

- **Gestione negozio** (nuova sezione, solo admin): qui si creano e si gestiscono
  i *template* dei pacchetti. All'inizio non esiste nessun template. Un template
  non è un pacchetto in vendita: è un modello da cui l'admin parte.
- **Impostazioni del campionato**: il pulsante "Crea pack" aggiunge un pacchetto
  al negozio di quel campionato. L'admin sceglie un template e ottiene le
  impostazioni già compilate, che può modificare per intero prima di creare il
  pacchetto. Non è obbligatorio usare tutti i template: ne usa solo quelli che
  servono per quel torneo.
- Il pacchetto creato è una copia indipendente: le modifiche al template non
  cambiano i pacchetti già creati.
- Da qui l'admin modifica o elimina i pacchetti del negozio e vede lo storico di
  tutti i piloti.
- I campionati attivi esistenti prima della fase 12 hanno il negozio vuoto: i
  pacchetti si creano a mano con "Crea pack".

## 6. Acquisto e apertura

1. L'acquisto è un'unica operazione indivisibile: controllo del saldo, estrazione
   in ordine, aggiornamento della pool, assegnazione all'inventario e
   registrazione nello storico. Due acquisti contemporanei non possono consumare
   la stessa copia (la pool rimane la fonte di verità).
2. Il backend restituisce al frontend l'elenco delle carte uscite. Le due pool
   sono separate e per il backend l'ordine è indifferente.
3. A schermo, nell'animazione, si mostrano prima le carte modifiche e poi le
   carte sponsor.
4. Il pacchetto compare in primo piano; lo sfondo si sfoca e non è più
   cliccabile.
5. Prima si vede la busta chiusa. Un clic in qualsiasi punto la fa scorrere
   verso il basso e mostra la prima carta.
6. Ogni clic successivo fa scorrere la carta verso sinistra e mostra la
   seguente, fino all'ultima.

## 7. Inventario

- Le copie di una carta ottenute si **sommano** a quelle già possedute. Il tetto
  di sicurezza è 100 copie per carta; il limite reale è la pool: se una carta ha 4
  copie e due piloti ne hanno 3 e 1, nella pool ne restano 0 e non se ne possono
  ottenere altre.
- Le carte **sponsor** stanno in un inventario separato da quello delle
  modifiche, ma si vedono nella stessa pagina del pilota.
- Le carte Calore non si distinguono più: sono carte modifiche come le altre.
- **Uso delle carte sponsor (fase futura)**: sono carte a consumo. Si possono
  usare in gara e, una volta usate, vengono cancellate; in gara se ne possono
  anche ottenere. A fine gara l'inventario sponsor può quindi avere meno o più
  carte, anche tutte diverse da quelle di partenza. Come gestirlo si decide in una
  fase successiva: nella fase 12 le carte sponsor si ottengono e si vedono, ma non
  si usano.

## 8. Storico acquisti

- Ogni acquisto registra almeno: pilota, pacchetto, costo e valuta, data e ora,
  carte ottenute.
- Si vede solo dal negozio, con il pulsante "Storico": un popup con i propri
  piloti iscritti, ciascuno in una sezione espandibile.
- L'admin, dalle impostazioni del negozio, vede lo storico di tutti i piloti; nel
  negozio è come un giocatore qualsiasi.
- Alla chiusura del campionato lo storico **resta solo per l'admin** e viene
  cancellato insieme al campionato.
- Lo storico non è collegato in modo vincolante al pilota: se il pilota viene
  eliminato in modo definitivo lo storico resta visibile all'admin.

## 9. Note di compatibilità con la specifica attuale

- Le pool del campionato sono già copie indipendenti (`pool_deck_id` e
  `sponsor_pool_deck_id`): l'estrazione consuma queste copie e non tocca le pool
  di origine.
- Le carte hanno `name`, `path` e `copies`: per il filtro per nome non serve
  nessuna categoria nuova.
- Il pilota ha oggi un solo inventario (`inventory_deck_id`): per le carte
  sponsor serve un secondo mazzo di inventario, con reset all'iscrizione e alla
  chiusura come l'inventario attuale.
- Le carte Velocità 1-4 non fanno parte di nessuna pool e restano fuori dal
  riepilogo.
- Oro e punti sponsor sono già sul pilota e si azzerano a ogni iscrizione e alla
  chiusura del campionato.
- Il negozio si blocca con una gara in corso: la regola usa lo stato "in corso"
  già definito in `PROJECT_SPEC.md` (gara senza risultati).
- Lo script `resize_cards` e la preparazione delle immagini esistenti si possono
  riusare per le immagini dei pacchetti.

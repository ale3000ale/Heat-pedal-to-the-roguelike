> **STATO: AGGIORNATO IL 12 OTTOBRE 2026 (inizio fase 13).**
>
> Domande aperte dopo la chiusura della fase 12. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio è in `SHOP_DESIGN.md` e la sua
> traduzione tecnica in `SHOP_SCHEMA.md`; le decisioni della fase 13 sono in
> `PHASE_13_SPEC.md`.

# Domande aperte — Heat

## Fase 13 (carte sponsor e amministrazione delle carte)

Nessuna domanda di progettazione aperta: le decisioni sono in `PHASE_13_SPEC.md` e le
sottofasi 13a-13g attendono l'approvazione dell'autore, una alla volta.

## Fase 14 (sistemazione generale)

Dopo la 13: sistemazione del tutto e modifiche di vivibilità o miglioramenti. L'elenco
si definisce con l'autore a fine fase 13.

## Rinviato

- **Uso online**: un solo server con pochi worker, perché SQLite accetta una sola
  scrittura alla volta. Con un altro database servirà un blocco sulla riga del pilota
  (`SELECT ... FOR UPDATE`). Si affronta dopo la fase 14.
- **Strappo della busta e riepilogo del negozio**: l'effetto è stato verificato a mano
  dall'autore; il componente grafico non ha test automatici. Se in futuro non
  convince, si ritocca solo il CSS e il markup di `pack-reveal.svelte`.

## Decisioni chiuse del 12 ottobre 2026

- **Spareggio sportivo**: non serve. A pari punti l'ordine alfabetico resta solo uno
  stabilizzatore di visualizzazione.
- **Pool reali delle carte**: le pool di base esistono e funzionano.
- **Carte sponsor a consumo**: decise in `PHASE_13_SPEC.md` (uso in gara con conferma,
  annullamento fino a 5, stato "in revisione", tasto S, restituzione alla pool alla
  chiusura).
- **Amministrazione delle carte**: decisa in `PHASE_13_SPEC.md` (caricamento con
  ritaglio e zoom, nome e quantità, nomi in arancione, esclusione di caricate o di base
  nelle pool personalizzate).

## Decisioni chiuse dell'11 ottobre 2026

- Nell'apertura del pacchetto la busta ha come texture l'immagine del pacchetto
  acquistato e si apre con uno strappo. È solo CSS, senza test dedicati; i dettagli
  sono in `SHOP_DESIGN.md` (sezione 6) e `SHOP_SCHEMA.md`.
- Dopo la busta le carte si vedono una alla volta, già scoperte: ogni tocco fa
  scorrere la carta a sinistra mostrando la seguente.
- Dopo l'ultima carta un altro tocco apre il riepilogo finale. Il tasto "Salta" porta
  al riepilogo da qualsiasi fase.
- Le copie uguali (stessa sezione e stesso percorso immagine) compaiono una sola volta
  nel riepilogo, con "x N"; il raggruppamento è in `src/lib/pack-summary.ts`.
- Fino al riepilogo la finestra si chiude solo con la X; Esc e clic fuori chiudono dal
  riepilogo (`closeOnOutside` di `modal.svelte`).
- Un template di negozio senza pacchetti non è utilizzabile alla creazione del
  campionato; l'avviso è in `SHOP_DESIGN.md` (sezione 5) e in `SHOP_SCHEMA.md`.

## Decisioni chiuse del 10 ottobre 2026

- La ricarica delle pool di base chiede conferma prima di togliere carte.
- `GET /api/me/shops` (`api/shop_me.py`) esiste ed è usata dal frontend.
- Nel negozio lo storico resta una pagina separata e l'inventario un solo pulsante.
- Gli acquisti si serializzano con un blocco sul database (`BEGIN IMMEDIATE` su SQLite).
- La pool sponsor è usata dai pacchetti per estrarre le carte sponsor.
- I pacchetti nuovi costano 10 oro oppure 2 sponsor.

## Decisioni già chiuse (non ripetute)

Autenticazione, ruoli, primo admin, pagine, iscrizioni, mazzi, pool,
punteggi, classifiche, reset all'iscrizione e strategia di migrazione sono
definite in `PROJECT_SPEC.md`.

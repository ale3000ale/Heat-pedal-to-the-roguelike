> **STATO: AGGIORNATO IL 20 OTTOBRE 2026 (inizio fase 15).**
>
> Domande aperte dopo la chiusura della fase 14. Le decisioni già prese sono in
> `PROJECT_SPEC.md`; il funzionamento del Negozio è in `SHOP_DESIGN.md` e la sua
> traduzione tecnica in `SHOP_SCHEMA.md`; le decisioni della fase 13 sono in
> `PHASE_13_SPEC.md`; quelle della fase 15 in `PHASE_15.md`.

# Domande aperte — Heat

<!-- draft-backend-current:start -->
## Draft - backend consolidato e limiti correnti

Aggiornamento del 25 ottobre 2026, solo ramo draft e PR 18. Questa sezione aggiorna il solo stato del flusso draft e prevale sulle note storiche di avanzamento, senza alterare gli altri requisiti.

Sorgenti recuperati dall artefatto draft-backend-materialized della run 40152061495, job materialize-and-check concluso con success sul commit tecnico 1052e5d. Gli hash SHA-256 dei sorgenti sono conservati in docs/DRAFT_BACKEND_MANIFEST.json.

Prima della pubblicazione questo workflow verifica di nuovo pytest backend, upgrade/downgrade/upgrade con controlli dello schema e frontend check, lint, test e build. Esecuzione di pubblicazione: https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40153346360. Il controllo dedicato sul commit risultante documenta queste verifiche pre-push; non e una nuova esecuzione dei job ordinari della PR.

Nessun conteggio di test o warning inventato, nessun test locale o collaudo browser attestato. Nessun merge, rilascio, ZIP finale del progetto o intervento sul database reale. Il frontend draft non e implementato da questo consolidamento.

Questo consolidamento non aggiunge decisioni di prodotto aperte. Restano attivita implementative: frontend draft, integrazione live lato interfaccia e collaudo browser; non vanno presentate come gia completate.
<!-- draft-backend-current:end -->

## Fase 15 (SSE in tempo reale e sistemazione)

Decisioni dell'autore del 20 ottobre 2026 in `PHASE_15.md`. Restano da definire prima del codice:
schema di `event_log` e conservazione degli eventi, destinatari di ciascun evento, intervallo di
lettura delle connessioni SSE. L'elenco della sistemazione (15b) si definisce dopo la 15a.

## Rinviato

- **Rimozione del polling**: il controllo periodico delle notifiche (`card_poll_seconds`) resta come
  ripiego dell'SSE; si valuta la rimozione tra qualche versione.
- **Database diverso da SQLite**: con un altro database servirà un blocco sulla riga del pilota
  (`SELECT ... FOR UPDATE`). L'uso online con pochi worker è anticipato dalla fase 15 (vedi `PHASE_15.md`).
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

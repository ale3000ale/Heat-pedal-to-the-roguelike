# Heat — Pedal to the Roguelike

Applicazione web per giocare a **Heat: Pedal to the Metal** in modalità roguelike: i mazzi crescono gara dopo gara, tra carte modifica, carte sponsor e punti sponsor da spendere nel Negozio.

Il progetto nasce come evoluzione del gioco da tavolo, non come suo sostituto. Le partite restano al tavolo, con plancia, carte e regole originali; l'applicazione tiene insieme ciò che il tavolo da solo non ricorda: iscrizioni, draft, composizione dei mazzi, gare, classifica e punti sponsor. Sono già comprese le carte delle espansioni Heavy Rain e Tunnel Vision; Rocky Roads e Narrow Streets arriveranno in futuro.

La modalità roguelike è un'idea nostra: non fa parte del gioco originale.

L'applicazione nasce per un uso locale: un PC fa da server e gli altri dispositivi della stessa rete Wi-Fi/LAN si collegano dal browser. Non servono servizi cloud, account online o tunnel.

## Scopo del progetto

Heat è un gioco da tavolo di corse automobilistiche: ogni pilota costruisce il proprio mazzo e lo usa in gara. La modalità roguelike trasforma il campionato in una progressione: si parte dal mazzo base, il draft aggiunge carte modifica, la gara assegna i punti sponsor, e il Negozio restituisce nuove carte con cui preparare la gara successiva.

Gestire tutto questo con fogli di calcolo o note scritte è dispersivo. L'applicazione riunisce in un unico posto anagrafica di utenti, team e piloti, stato delle carte di ogni pilota, gare e revisioni, classifica, punti sponsor e acquisti.

L'app registra ciò che accade al tavolo: non gioca le partite al posto dei giocatori.

## Modalità roguelike

**Draft iniziale (solo prima gara)**

Si decide l'ordine di gioco. Si estraggono 5 carte modifica; il primo giocatore ne sceglie una e la aggiunge al proprio inventario, poi se ne pesca un'altra per riportare la pool a 5 carte, e si prosegue fino all'ultimo giocatore. Quando questi ha scelto, le carte rimanenti tornano nel mazzo modifiche, che viene mescolato; si estraggono altre 5 carte e si inizia la seconda passata, dall'ultimo al primo.

Dopo 4 passate ogni pilota ha 16 carte: 12 base (tre copie ciascuna di velocità 1, 2, 3 e 4) e 4 modifiche.

**Prima di ogni gara successiva**

Si fa la draft classica prevista dalle regole di Heat e la carta scelta entra nell'inventario. Poi si monta il mazzo di gioco: dall'inventario si scelgono 15 carte non sponsor e vi si aggiungono tutte le carte sponsor rimaste dalle gare precedenti. Le carte sponsor ottenute prima della gara dagli eventi vanno in mano come da regolamento.

**Gara**

Si gioca con le regole classiche. L'unica attenzione in più: quando un pilota riceve una carta sponsor in curva, guadagna anche un punto sponsor.

**Fine gara e punti sponsor**

Si assegnano i punti classifica consueti; i punti sponsor guadagnati in gara si sommano a quelli già posseduti (alla prima gara si parte da 0). I punti sponsor si spendono nel Negozio in pacchetti di carte che possono contenere modifiche, carte sponsor o entrambe.

**Stato attuale**

L'applicazione implementa la draft iniziale a quattro passate, con il tavolo da cinque carte e l'ordine a serpentina, la draft classica delle regole di Heat, gli inventari delle modifiche e degli sponsor, il mazzo da gioco con il controllo delle 15 carte, le gare con revisione, la classifica, la registrazione dei punti sponsor a fine gara e il Negozio. Resta da implementare l'assegnazione automatica del punto sponsor quando si riceve una carta sponsor in curva; nell'app le carte sponsor restano in un inventario separato, mentre al tavolo si aggiungono al mazzo di gioco.

## Requisiti

- **Python 3.11 o superiore**: `setup` si interrompe con un messaggio chiaro su versioni precedenti.
- **Node.js con npm**, per il frontend e per i controlli automatici.
- **Gioco reale di Heat** per giocare.

## Funzionalità

**Account e ruoli**

- Tre ruoli: amministratore, giudice e giocatore.
- Accesso con sessione e cookie; cambio password che revoca le altre sessioni dello stesso account.

**Team e piloti**

- Anagrafica di team e piloti, ricerca per nome e iscrizione ai campionati.

**Carte, mazzi e pool**

- Mazzi da gioco, inventari e pool distinti per pilota, con immagini delle carte.
- Caricamento delle immagini dall'area admin, con ritaglio e zoom; script per portare le immagini al formato dell'app.
- Controllo delle copie: una gara parte solo quando il mazzo di ogni iscritto ha esattamente 15 copie.

**Campionati e gare**

- Creazione del campionato, iscrizioni e gestione delle gare.
- Carte giocate e carte sponsor durante la gara, con revisione finale.
- Classifica e oro aggiornati con gli esiti delle gare.

**Negozio**

- Acquisti con l'oro guadagnato in classifica o punti sponsor guadagnati in pista, pacchetti di carte e carte estratte all'acquisto.

**Draft**

- Draft iniziale a quattro passate (tavolo da cinque carte, ordine a serpentina) e draft classica a una scelta; preparazione del draft, turni di scelta e mazzi che si compongono carta per carta.

**Gestione e supporto**

- Area admin per carte, pool, negozio, utenti e ruoli; trasferimenti di carte con salvataggio atomico e controllo delle versioni.
- Aggiornamenti in tempo reale delle pagine tramite Server-Sent Events, senza ricaricare.
- Produzione Wi-Fi/LAN: il server stampa a video l'indirizzo da usare dagli altri dispositivi, con QR di accesso.

## Primo avvio

Dalla radice del progetto:

```
python heat.py setup
python heat.py start
```

Il setup crea l'ambiente virtuale `backend/.venv`, installa le dipendenze Python da `backend/requirements.txt`, applica le migrazioni, popola il prototipo del mazzo, crea l'utente admin (chiede i dati) e installa le dipendenze del frontend con `npm ci` (o `npm install` se manca `package-lock.json`). Si può ripetere senza danni.

Dopo l'avvio:

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

`Ctrl+C` ferma entrambi.

## Comandi

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Apre il menu interattivo. |
| `python heat.py setup [--skip-admin] [--skip-seed]` | Installa tutto; le opzioni saltano la creazione dell'admin o il prototipo del mazzo. |
| `python heat.py start [--backend-only] [--public-url URL]` | Applica le migrazioni e avvia backend e frontend (o solo il backend); `--public-url` imposta l'origine pubblica usata dagli accessi esterni. |
| `python heat.py migrate` | Applica le migrazioni del database (`alembic upgrade head`). |
| `python heat.py test` | Esegue i test del backend con pytest. |
| `python heat.py check` | Formattazione, controlli, lint e test del frontend (`tools/check-frontend.mjs`). |
| `python heat.py production [--public-url URL]` | Compila il frontend e lo pubblica sulla rete Wi-Fi/LAN, scegliendo l'IPv4 del PC; non applica migrazioni. |

Dopo un `git pull` o un cambio di ramo l'avvio migra comunque da solo il database.

Nota per l'automazione: `python heat.py test` e `python heat.py check` non propagano il codice di uscita. In CI conviene invocare direttamente pytest e i comandi npm.

## Struttura

| Percorso | Contenuto |
|---|---|
| `backend/app/api/` | Rotte FastAPI, raggruppate per dominio. |
| `backend/app/services/` | Regole di business, raggruppate per dominio. |
| `backend/app/db/models/` | Modelli SQLAlchemy; gli schemi Pydantic stanno in `backend/app/schemas/`. |
| `backend/alembic/versions/` | Migrazioni del database. |
| `backend/tests/` | Suite pytest. |
| `backend/media/` | Immagini delle carte, servite su `/media`. |
| `frontend/src/routes/` | Pagine SvelteKit. |
| `frontend/src/lib/` | Logica riusabile e componenti, con i test accanto ai file. |
| `tools/` | Avvio e gateway LAN, controlli del frontend. |
| `docs/` | Specifica, stato, note di lavoro e documentazione delle fasi. |
| `database/` | Riferimento dello schema del database. |
| `heat.py` | Setup, avvio, migrazioni, test, controlli e produzione. |

## Immagini delle carte

Le immagini stanno in `backend/media/cards/` (`base/modifiche`, `base/sponsor`, `starter`, `uploads`). Le cartelle `base` e `starter` vanno riempite a mano; `uploads` si riempie con il caricamento dell'admin (`POST /api/admin/cards`, immagine già tagliata a 560x870 px, al massimo 2 MB) e le carte caricate si eliminano con `DELETE /api/admin/cards`. L'interfaccia di caricamento con ritaglio e zoom è nella pagina admin delle pool: le carte caricate si riconoscono dal nome in arancione e si eliminano dall'elenco. I nomi seguono `nome_N.ext`, con N pari al numero di copie. Per portarle al formato usato dall'applicazione (WebP, scatola massima 560x870 px), da `backend`:

```
python -m app.scripts.resize_cards [cartella] [--dry-run]
```

Le immagini dei pacchetti del Negozio stanno in `backend/media/pack/`.

## Documentazione

- `docs/PROJECT_SPEC.md`: regole di gioco e di prodotto, fonte principale.
- `docs/PROJECT_STATUS.md`: stato di avanzamento.
- `docs/PROJECT_NOTES.md`: mappa del codice, comandi e convenzioni di lavoro.
- `docs/SETUP.md`: installazione e avvio in dettaglio.
- `docs/PRODUCTION_LAN.md`: uso in Wi-Fi/LAN e limiti.
- `docs/OPEN_QUESTIONS.md`: domande ancora aperte.
- `docs/SHOP_DESIGN.md` e `docs/SHOP_SCHEMA.md`: funzionamento e schema tecnico del Negozio.
- `docs/DATABASE.md` e `docs/DATABASE_ANALYSIS.md`: database e sua analisi.
- `docs/CHANGELOG.md`: versioni rilasciate e note di rilascio.
- `docs/HISTORY.md`: cronologia e note di stato precedenti.
- `docs/PHASE_*.md`: note delle singole fasi, da leggere come cronologia.

## Sicurezza

Non vanno inseriti nel repository ambiente virtuale, `node_modules`, database reali, file `.env`, password o token.

## Patch

### Beta 0.8.1

Versione attuale, non definitiva.

- Caricamento dei font senza bloccare il render della pagina.
- Drawer di navigazione su schermi stretti: menu completo anche sotto i 768 px.
- README riscritto per un pubblico esterno, con la modalità roguelike, i requisiti e i comandi.
- Voci di navigazione allineate a `resolve()` di SvelteKit e test del QR eseguibile in CI senza la libreria installata.

Le note delle versioni precedenti sono in `docs/CHANGELOG.md`; la cronologia dettagliata è in `docs/HISTORY.md`.

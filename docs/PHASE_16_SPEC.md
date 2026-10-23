# Fase 16 - Gestione admin carte piloti

Data: 2026-10-22. Ramo: phase-16-admin-pilot-inventory.
Base: main 6dcdc836dba33a506bd954cd27eda3d212ba84ad, merge PR 14 fase 15.
Specifica approvata con f87a759. Primo incremento: dominio puro dei trasferimenti;
API, persistenza e frontend ancora da implementare. Nessun dato reale modificato.

## 1. Obiettivo e accesso

Solo l'admin, dalle opzioni di un campionato, apre una sezione chiamata Piloti.
Elenco dei piloti iscritti con nome del pilota, username del proprietario e pulsante
con icona di carte/mazzo ed etichetta accessibile. Il pulsante apre la gestione
carte di quel pilota nel contesto del campionato selezionato.
Non modifica utenti, team, ruoli, saldi o punteggi. Non amplia i diritti del giudice.

## 2. Schermata

Prima meta', carte del pilota, tre sezioni apribili e distinte:
- Mazzo da gioco, con conteggio delle copie N/15.
- Inventario Modifiche, cioe' copie disponibili fuori dal mazzo.
- Inventario Sponsor.

Seconda meta', due sezioni apribili:
- Pool Modifiche del campionato.
- Pool Sponsor del campionato.

Tutte le carte in queste cinque sezioni hanno immagini e quantita', usando le
risorse correnti. Nessun inventario totale ottenuto sommando visivamente mazzo e
inventario: restano contenitori separati. Su mobile le due aree si dispongono in
sequenza mantenendo le sezioni apribili. Non sono richieste immagini o avatar degli
utenti. Pool di base, prototipi e pool di altri campionati non vengono modificati.

## 3. Spostamenti, una copia per clic

| Carta premuta in | Destinazione |
|---|---|
| Mazzo da gioco | Pool Modifiche del campionato |
| Inventario Modifiche | Pool Modifiche del campionato |
| Inventario Sponsor | Pool Sponsor del campionato |
| Pool Modifiche | Inventario Modifiche del pilota |
| Pool Sponsor | Inventario Sponsor del pilota |

Dalla pool non si aggiunge mai direttamente al mazzo. Le carte sponsor non entrano
nel mazzo da gioco. Ogni clic toglie una copia dalla sorgente selezionata e ne
aggiunge una alla destinazione, senza creare/distruggere copie o sottrarne una
seconda da un altro contenitore. Esempio: rimozione di una copia dal mazzo significa
mazzo -1 e pool Modifiche +1, inventario disponibile invariato. Copie uguali negli
altri contenitori restano al loro posto.

La precedente formulazione sul togliere una carta gia' nel mazzo viene resa
esplicita dalla nuova schermata: si puo' rimuovere proprio la copia della sezione
Mazzo. Non si applica una doppia sottrazione mazzo+inventario per un singolo clic.
Le copie a zero non sono spostabili. I clic modificano soltanto la bozza locale.
Non aggiungere un trasferimento diretto inventario/mazzo in questa schermata;
la costruzione ordinaria del mazzo resta quella del giocatore.

## 4. Salva e riepilogo

Salva in basso a destra apre un modal di conferma prima di scrivere sul server.
Il riepilogo e' testuale, senza immagini, ed elenca le modifiche effettivamente
da applicare, con pilota/utente, nome carta, quantita', sorgente e destinazione.
Mostra anche il nuovo conteggio del mazzo. Le altre rappresentazioni delle carte
restano con immagini, come richiesto dall'autore.

Annulla chiude la conferma senza salvare e conserva la bozza per correggerla.
Solo il comando di conferma invia il salvataggio, proteggendo dai doppi invii.
Salvataggio unico e atomico di tutti i contenitori coinvolti; un errore non deve
lasciare trasferimenti applicati a meta'. La chiusura/uscita con modifiche locali
richiede conferma prima di abbandonarle. Nessun autosalvataggio a ogni clic.

## 5. Quando e' vietato modificare

Campionato chiuso in sola lettura, regola esistente mantenuta. Modifiche vietate
anche con una gara aperta o una revisione non ancora confermata, come chiarito
dall'autore alle 17:49. Il controllo usa lo stato autorevole del backend, non
soltanto pulsanti disabilitati o un timer nel browser.

Ricontrollare stato, ruolo, iscrizione e versioni al salvataggio. Se durante la
bozza si apre una gara, cambia una pool o un altro client modifica i mazzi, non
sovrascrivere silenziosamente: rifiutare il salvataggio incompatibile, spiegare
l'errore e preservare la copia locale. Nessun retry automatico delle scritture.

## 6. Aggiornamento live

Dopo commit riuscito aggiornare la schermata admin, inventari e mazzo del pilota
nelle viste autorizzate gia' aperte. Usare il client SSE condiviso e riletture REST
protette, senza secondo stream, polling continuo o copie private nei segnali
pubblici. Non usare notifiche di regalo/tasto S per questi trasferimenti admin.
Nessun evento di successo o aggiornamento definitivo prima del commit.

## 7. Avvio gara e mazzi da 15

Prima di creare/avviare una nuova gara controllare tutti i piloti iscritti al
campionato: ogni mazzo da gioco deve contenere esattamente 15 copie totali.
Sono 15 carte contate per copia, non 15 nomi diversi e non 15 carte possedute tra
tutti gli inventari. In assenza di una selezione partecipanti prima dell'avvio,
il controllo e' su tutti gli iscritti, non sulla classifica inserita a fine gara.
Non aggiunge nuove regole sul numero minimo di iscritti rispetto a quelle esistenti.

Controllo obbligatorio nel backend, dentro la protezione transazionale dell'avvio.
Se qualche mazzo non e' pronto, nessuna nuova gara o evento race.started; mostrare
ai gestori l'elenco dei piloti non pronti e il loro conteggio N/15. Il controllo
deve restare coerente con modifiche contemporanee del giocatore o dell'admin:
non basta leggere 15 nel frontend prima della richiesta.

Tra le gare un mazzo puo' essere incompleto. Il Salva dell'admin puo' lasciarlo
sotto 15: e' l'avvio gara che viene bloccato finche' il giocatore non lo completa.
Non si cambia automaticamente l'inventario iniziale e non si inventano carte per
arrivare a 15. Restano il massimo di 15 durante la costruzione e gli altri blocchi
esistenti. L'aggiunta dalla pool va nell'inventario, mai direttamente nel mazzo.

## 8. Vincoli tecnici e verifiche

Codice letto: championship-settings.svelte; modelli Pilot e servizi races.py e
pilot_deck.py. Pilot ha tre riferimenti a Deck distinti. move_card sposta copie
fisicamente tra inventario disponibile e game_deck; create_race attuale controlla
stato e gare non concluse ma non la dimensione dei mazzi. Si riusano formato carte,
parser, versioni e risorse correnti, senza trasformare Deck.cards o immagini.
Nessuna migrazione prevista senza prima motivarla e farla autorizzare.

Specifica e stato generali riallineati al perimetro approvato in questo incremento. Endpoint, DTO e file specifici verranno descritti nel relativo blocco,
non presentati come gia' esistenti. Funzioni di dominio piccole e indipendenti;
API, tipi, store, validatori e componenti separati. Nessun falso scaffold frontend.

Test richiesti: movimenti nei cinque sensi, copie e immagini, indipendenza dei
contenitori, conservazione quantita', rollback, ruoli/campionato/iscrizione,
gara/revisione aperta, conflitti e richieste concorrenti, conferma senza scritture
su Annulla, live autorizzato e privacy. Per avvio: 15 validi, incompleti o eccessivi,
elenco non pronti e assenza di nuova gara/evento sul rifiuto, concorrenza con modifiche
mazzo. Aggiornare le fixture dei test senza alterare dati o inventari di produzione.

Lint/check/test/build frontend e suite backend, poi documenti riallineati con esiti
reali; collaudo browser separato. Nessun comando o test eseguito in questa
pubblicazione solo documentale. Nessun accesso, migrazione o reset del DB originale.

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.

## Fase 16 - Incremento API admin di lettura

Data: 2026-10-22. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento espone letture, non il salvataggio o la gestione frontend.

## Contratto

- GET /api/admin/championships/{championship_id}/pilots: iscritti visibili,
  con pilot_id, name, user_id e username. Solo admin, mai password o sessioni.
- GET /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards:
  metadati del pilota, read_only, blocked_reason e cinque contenitori distinti.
- Ogni contenitore espone available, id, version e cards nel formato corrente
  name/path/copies. Le pool assenti hanno available=false, id/version null e
  cards vuoto; una pool esistente ma vuota e' disponibile. Nessuna pool creata.
- Tutti i Deck presenti vengono letti con una sola query. Riferimenti duplicati
  o mancanti e JSON corrotto danno 409, non carte inventate o svuotate.
- Campionato chiuso, gara o revisione non confermata sono leggibili ma indicati
  in sola lettura. Nessuna conferma automatica della revisione dentro queste GET.
- Il servizio ricontrolla il ruolo oltre alla dipendenza HTTP AdminUser.
  Pilota nascosto o non iscritto: 404. Giudice e giocatore: 403; anonimo: 401.

## File e verifiche

Nuovi schemas/admin_pilot_cards.py, services/admin_pilot_cards.py e
api/admin_pilot_cards.py; main.py registra il router senza alterare lifespan.
Test HTTP in backend/tests/test_admin_pilot_cards_api.py: 13 casi, inclusi i
parametri per ruoli e revisione. Verificano anche assenza di modifiche a Deck
ed EventLog, immagini/versioni, pool assenti o vuote, dati corrotti e privacy.
Alla preparazione: parsing Python e git diff --check riusciti. Test HTTP non
eseguiti localmente: vanno eseguiti nel repository completo, senza dichiararli
PASS sulla sola analisi sintattica. Il workflow documentale li esegue prima di
riallineare i dieci documenti generali e di fase. La CI completa resta separata.

## Limiti e seguito

Nessuna POST/PUT di gestione carte, transazione di salvataggio, evento nuovo,
regola di avvio da 15, modifica ai movimenti del giocatore o interfaccia ancora
aggiunta da questo incremento. Quelle parti restano da implementare e testare.
Le versioni lette non autorizzano una futura scrittura: il salvataggio dovra'
ricontrollare ruolo, iscrizione, stato gara/revisione e tutti i contenitori.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al DB reale. Restano
il formato confermato name/path/copies e i percorsi relativi ai media correnti.
Un messaggio vuoto o solo @GitHub approva la proposta pendente; le sole modifiche
documentali non richiedono attesa della CI applicativa. Nessun merge implicito.

<!-- phase16-admin-save:start -->
## Fase 16 - Salvataggio admin atomico

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Stato sintetico fase 16: Perimetro funzionale implementato, incluso live e riepilogo effettivo; CI 40026443509 riuscita su 2366d1d; riscontro manuale complessivamente positivo dell'autore, senza protocollo caso per caso; riallineamento finale documentale; nessun merge autorizzato.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del workflow.
Il titolo deve restare esattamente quello corrente; la riga di stato e' unica e
senza pipe. Questo documento consolida lo stato corrente; le note incrementali
precedenti restano nello storico Git. Non costituisce merge o rilascio in main.

### Contratto backend e conservazione delle copie

GET /api/admin/championships/{championship_id}/pilots restituisce iscritti visibili
con nome e username. GET e PUT sul percorso
/api/admin/championships/{championship_id}/pilots/{pilot_id}/cards leggono o
salvano il contesto del pilota. Accesso solo admin; nessun diritto ampliato al
giudice e nessuna modifica a utenti, team, ruoli, saldi o punteggi.

Il PUT riceve versions di tutti i cinque contenitori e transfers con soli
source/path. ID/version interi positivi; solo le due pool possono essere null.
Campi extra, destinazioni client e sostituzioni arbitrarie sono rifiutati.
Pool assente distinta da pool vuota, mai creata automaticamente. Riferimenti
Deck incoerenti o JSON corrotto non diventano contenitori validi o vuoti.

Ogni clic sposta una copia nelle sole direzioni approvate:
- game_deck verso modification_pool;
- modification_inventory verso modification_pool;
- sponsor_inventory verso sponsor_pool;
- modification_pool verso modification_inventory;
- sponsor_pool verso sponsor_inventory.

Nessun movimento diretto pool/mazzo, sponsor/mazzo o inventario/mazzo nella
schermata admin. Una rimozione dal mazzo non sottrae anche dall'inventario.
Il pianificatore clona gli input e rifiuta copie non valide, percorsi ambigui
e nomi associati a immagini discordanti, senza mutazioni parziali su errore.

Il backend ricontrolla ruolo, pilota visibile/iscritto, campionato chiuso, gara
aperta, revisione non confermata e tutte le versioni nella transazione. 409 per
conflitto, 422 per movimento non applicabile, senza retry automatici. Commit
unico di Deck/eventi e rollback anche su errore eventi. Differenze effettive
soltanto: versioni ed eventi non cambiano per un salvataggio senza differenze.
Dopo commit: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio con mazzi da 15

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli. Invalida identita' ORM precedenti e
rifiuta modifiche pendenti; promuove una transazione nativa gia' aperta tramite
UPDATE senza righe, senza cambiare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di tutti gli
iscritti, inclusi i nascosti, sotto lo stesso lock. Non 15 nomi o il totale degli
inventari; nessun nuovo minimo di iscritti. race_deck_snapshot.py riusa il
dominio race_deck_readiness.py. Mancanza mazzo o JSON corrotto non sono sanati.
Tra le gare un mazzo puo' restare incompleto, anche dopo un salvataggio admin.

Rifiuto di avvio: nessuna nuova gara o race.started, rollback e 409 con nomi e
conteggi dei non pronti, senza carte. BUSY/LOCKED diventano RaceStartConflictError
e 409; altri errori SQL non sono mascherati. Restano blocchi di chiusura e
gara/revisione non confermata; gestione precedente delle revisioni scadute invariata.

### UI, richiesta e riepilogo effettivo

Nelle impostazioni campionato l'admin apre Piloti, vede nome/username e un
pulsante Carte accessibile. Cinque sezioni apribili con immagini e quantita':
mazzo N/15 per copie, due inventari distinti e due pool. Su mobile le aree
restano in sequenza. Modal e CardTile riusati, senza nuovo scaffold o risorse.

Il piano costruisce versions dalla baseline, anche per contenitori non toccati,
e ricalcola la sequenza senza fidarsi di un'anteprima alterata. Percorsi entro
255 code point, identita' nomi coerente con strip().casefold() del backend.
Nessun arrotondamento di ID/version e nessuna destinazione/copertura di copie
arbitraria nella richiesta. Tutti gli output sono indipendenti dalla sessione.

Salva in fondo a destra apre un modal solo testuale con pilota, username, nome
carta, quantita', sorgente/destinazione e nuovo conteggio del mazzo. Il riepilogo
accorpa copie e compensa i versi opposti inventario/pool della stessa carta,
senza inventare un verso inverso verso il mazzo. Non cambia il registro PUT:
il server riceve i clic originali validati in ordine. Nessuna proposta di PUT
quando non restano variazioni effettive. Annulla, X, Escape e sfondo non inviano
e conservano la bozza. Solo Conferma e salva consuma una proposta una volta.

Durante conferme e operazioni sono protetti clic, ripristino, ritorno, chiusura
ordinaria e navigazione. Successo: nuova sessione da snapshot PUT e versioni
server. Errori conservano la bozza; 422 consente azioni manuali, altri errori
bloccano nuovi invii fino a rilettura. Esito di rete o risposta inutilizzabile
non provano un rollback. Rileggi dal server e' esplicito: con bozza pendente
richiede conferma e la sostituisce soltanto dopo risposta utilizzabile.
Ripristina bozza e' locale e conserva i blocchi, non equivale a una rilettura.
Il client controlla contesto e la creazione della sessione controlla carte:
non e' una validazione runtime completa di ogni campo del DTO.

### Live e lifecycle

Il pannello usa eventClient condiviso e riletture REST autorizzate tramite il
coordinatore createRefreshCoalescer. Nessun secondo EventSource, polling o
autosalvataggio. I segnali non trasferiscono carte e non autorizzano scritture.
Eventi pertinenti di carte, iscrizioni, gara/revisione, resync e riapertura del
trasporto invalidano il contesto; gli altri campionati sono filtrati. Lo stato
della connessione non viene presentato come prova della freschezza dei dati.

Riletture accorpate e risultati obsoleti scartati. Una bozza non viene
sovrascritta: aggiornamenti incompatibili la bloccano conservando i dati.
Le conferme aperte sono distinte dalle richieste HTTP effettivamente in corso:
un evento puo' invalidare la proposta prima dell'invio; durante PUT/GET viene
rinviato, evitando di scartare il successo del proprio salvataggio. Una GET
live puo' seguire un evento pendente dopo il PUT: non e' un retry della scrittura.
Solo l'accettazione di uno snapshot server utilizzabile libera il blocco delle
riletture, non un reset locale o un cambio di stato del trasporto.

Cambio utente/ruolo, campionato, pilota o smontaggio invalidano il contesto;
risposte e callback tardive non ripopolano un contesto successivo. I cleanup
rimuovono i soli listener propri, senza chiudere lo stream condiviso. Una
chiusura forzata del browser non annulla una scrittura gia' inviata.

### Esiti finali verificati e collaudo dell'autore

Codice candidato: 2366d1de37cf1cf638b45c55313a3e31601eebff. CI 40026443509
riuscita per Frontend (check, lint, test, build), job 120664599995, Backend
(pytest), job 120664600371, Migrazioni (database di test), job 120664600375,
e Documenti fase 16 dopo backend, job 120665715224. Non sono nuove esecuzioni
locali. I conteggi complessivi di test e warning non sono stati letti dai log.

Dopo il via libera e la checklist in conversazione sul candidato 2366d1d,
il 2026-10-23 alle 23:59 CEST l'autore riferisce: «sembra funzionare tutto».
E' un riscontro manuale complessivamente positivo, non un verbale con esito
per ogni caso. Non sono stati forniti browser/dispositivo, log o risultati
individuali; non si marca automaticamente ogni voce OK. Non e' un collaudo
browser eseguito dall'assistente ne' prova di tutte le condizioni concorrenti.

Restano non attestati singolarmente i casi avanzati della checklist: doppio
invio, rete interrotta/esito incerto, conflitti tra sessioni, risposte tardive,
permessi e scadenza durante rete, rollback/concorrenza reale e privacy dei
payload. Le coperture automatiche e il riscontro qualitativo non vanno confusi.

### Tracciabilita' delle verifiche precedenti

Storico: dominio 934333c; sessione eedd729; chiusura modal d9ee662; UI c950510;
trasporto PUT 549e83e/f95c915; piano 024d47a/ad377d4; salvataggio 9769dd5/7d449cb;
adattatore eventi ecbf684/e725ba4; riletture 914ee47; collegamento live
fbcbd89/dc06e29; rimozione import 78661d8; prefer-const nei test 283c0ac;
riepilogo effettivo e posizione Salva 6d1b7cd/2366d1d. I controlli finali
sopra sostituiscono come stato corrente le letture incrementali in coda.

Il precedente riepilogo dell'autore era 748 passed, 14 warnings e 14 subtests
passed prima della pulizia 4514348; 27 asserzioni snapshot conservate tramite
AST. La regressione 72 failed/676 passed, poi un fallimento, era stata corretta
senza saltare test o allentare il dominio. Non sono i conteggi della CI finale.
Dieci casi di readiness includevano lock simulato, non tutta la concorrenza reale.

Identita' Unicode 15.0 verificata con confronto Node/Python su 1.112.064 scalari
e nove casi composti, senza NFC/rimozione accenti; non era type-check. Controlli
Node senza tipi: dodici scenari politica modal, venticinque adattatore eventi
e nove coordinatore riletture; non equivalgono a Vitest o browser. Sette test
Python della trasformazione documentale su fixture temporanee erano riusciti,
non il workflow GitHub completo. Le esecuzioni npm locali non sono inventate.

### Riallineamento documentale e consegna

Il titolo stabile e' stato ripristinato in f8a94e4; la tabella PROJECT_STATUS
deriva dalla riga Stato sintetico fase 16, senza stato hardcoded su vecchi commit.
Il pin CI aggiornato usa il blob 6858f05d89072cca488efeeb46166a2770383545 del
workflow approvato. Restano controlli su titolo, stato unico e marcatori anche
invertiti/adiacenti, protezioni di ramo e percorsi e nessun force-push.

Questo commit aggiorna soltanto i documenti sorgente e dedicati, dopo codice e
verifiche come richiesto dall'autore. La propagazione ai dieci documenti generali
va verificata dopo la pubblicazione, senza attendere nuovi test applicativi
per i soli docs. Il successo del job documentale sul codice precedente non
dimostra gia' propagato questo nuovo testo. Nessun merge, rilascio o ZIP finale
creato implicitamente; la PR resta in bozza.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato il 2026-10-22. Nessuna conversione a path/value o /images/cards,
migrazione, dipendenza, modifica di setup/avvio o accesso al database reale
da parte dell'assistente. Perimetro funzionale fase 16 distinto dal resto
delle istruzioni generali del progetto e da una consegna ZIP complessiva.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

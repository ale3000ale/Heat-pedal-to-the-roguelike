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
Questa versione consolida le precedenti note incrementali: il backend di lettura,
salvataggio e avvio con mazzi da 15 e' implementato. La cronologia delle versioni
precedenti resta nello storico Git. Nessun merge o completamento della fase implicito.

### Contratto di scrittura admin

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions descrive tutti i cinque contenitori con id/version
interi positivi, oppure null per le sole pool assenti. Ogni trasferimento contiene
solo source e path: una copia per elemento, destinazione imposta dal dominio.
Campi extra, destinazioni client e sostituzioni arbitrarie delle carte sono rifiutati.

Il backend ricontrolla ruolo admin, pilota visibile/iscritto, campionato chiuso,
gara aperta e revisione non confermata nella transazione. Confronta id e versione
anche dei contenitori non toccati. Le pool assenti non vengono create e non possono
fornire o ricevere copie. Conflitto: 409 senza retry automatico; movimento non
applicabile: 422. Un solo commit per Deck ed eventi, rollback anche su errore eventi.

Il mazzo puo' restare incompleto tra le gare. Nessuna aggiunta diretta pool/mazzo
o sponsor/mazzo e nessuna doppia sottrazione. Solo differenze effettive cambiano
le versioni; senza differenze non vengono prodotti eventi. La risposta restituisce
snapshot e versioni aggiornate. Dopo variazioni: cards.changed pubblico vuoto e
privato al proprietario con solo pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio gara

services/sqlite_write_lock.py e' usato da salvataggio admin, pilot_deck.move_card
e races.create_race prima delle letture autorevoli. Invalida le identita' ORM
precedenti e rifiuta modifiche pendenti. Una transazione nativa gia' aperta viene
promossa con UPDATE senza righe: nessuna carta o versione viene modificata dal lock.
Il retry preesistente di move_card resta limitato a StaleDataError; il salvataggio
admin e l'avvio gara non ritentano automaticamente i conflitti di lock.

create_race legge i mazzi da gioco di tutti gli iscritti sotto lo stesso lock e
richiede esattamente 15 copie totali, non 15 nomi o il totale degli inventari.
La lettura DB in race_deck_snapshot.py riusa il dominio race_deck_readiness.py;
include gli iscritti nascosti e non aggiunge un nuovo minimo di iscritti.
Mazzo mancante o JSON corrotto non vengono trasformati in un mazzo valido.

Se un iscritto non e' pronto: nessuna nuova gara o race.started, rollback e HTTP
409 con riepilogo testuale di nomi e conteggi, senza carte. I conflitti SQLite
BUSY/LOCKED vengono tradotti in RaceStartConflictError e HTTP 409; gli altri
errori SQL non sono mascherati. Restano chiusura e gara/revisione non confermata.
La gestione preesistente delle revisioni scadute prima dell'avvio non e' cambiata.

### Verifiche effettive

Il 2026-10-23 e' stata letta la CI 39917281059 sul codice 4514348: successo per
Backend (pytest), Frontend (check, lint, test, build), Migrazioni (database di test)
e Documenti fase 16 dopo backend. Anche align-docs-pr, esecuzione 39917281153,
risulta riuscito. Questi sono riscontri GitHub, non nuove esecuzioni locali.

L'autore ha fornito il riepilogo precedente alla pulizia dei warning: 748 passed,
14 warnings e 14 subtests passed. Il commit 4514348 rimuove soltanto Result.tuples()
dai due snapshot dei test eventi, conservando le 27 asserzioni verificate tramite
AST. La CI successiva e' verde; il conteggio esatto dei warning di quella nuova
esecuzione non e' stato letto e non viene dichiarato zero sulla sola conclusione.

La regressione iniziale mostrava 72 failed e 676 passed, poi un solo fallimento.
Le fixture residue del giudice e del secondo campionato, l'aspettativa sul nuovo
errore di conflitto e la preparazione dei mazzi nel test della classifica congelata
sono state corrette senza saltare test o allentare il vincolo di produzione.

I test dedicati comprendono dominio puro, letture e salvataggi admin, snapshot DB,
lock e avvio: dieci casi in test_race_start_readiness.py coprono conteggi errati,
JSON corrotto, accesso admin/giudice, esclusione dei non iscritti, rollback eventi
e traduzione di un lock occupato simulato. Non equivalgono a un collaudo browser
o a una nuova prova reale di tutte le interazioni concorrenti avvio/admin/giocatore.

### Limiti, dati e prossimo passo

Restano da implementare frontend admin, conferma testuale, protezione della bozza
e collegamento live tramite il client SSE condiviso, poi verifiche dedicate e
collaudo browser. Non dichiarare la fase 16 completa sulla sola CI del backend.
Prima di nuove funzionalita', verificare la propagazione di questo stato nei dieci
documenti gestiti dal processo esistente. Nessuna attesa CI applicativa per i soli
commit documentali e nessuna chiusura/riapertura abituale della PR.

Deck.cards resta TEXT con array JSON name/path/copies e i percorsi correnti relativi
ai media, come confermato dall'autore il 2026-10-22. Nessuna conversione al vecchio
esempio path/value, migrazione, dipendenza nuova, modifica a setup/avvio o accesso
al database reale. Nessun nuovo scaffold o modifica delle risorse.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

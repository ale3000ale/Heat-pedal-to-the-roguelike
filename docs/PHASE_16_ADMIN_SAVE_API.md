# Fase 16 - Salvataggio admin atomico e bozza UI

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Backend e integrazione locale della bozza sono implementati e verificati in CI.
Il salvataggio dalla UI e il live restano esclusi. Nessun merge o fase completa.
Questa versione consolida le note precedenti, conservate nello storico Git.

## Contratto di scrittura admin

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

## Lock condiviso e avvio gara

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

## Verifiche precedenti e dominio locale

La CI 39917281059 su 4514348 e align-docs-pr 39917281153 risultavano riusciti.
L'autore aveva fornito prima della pulizia: 748 passed, 14 warnings e 14 subtests
passed. 4514348 rimuove soltanto Result.tuples() dai due snapshot eventi,
conservando 27 asserzioni verificate tramite AST. I warning successivi non sono
stati contati dai log e non vengono dichiarati zero. La regressione iniziale,
72 failed e 676 passed e poi un solo fallimento, e' stata corretta nelle fixture
e nelle aspettative senza saltare test o allentare il vincolo dei mazzi da 15.

Dieci casi in test_race_start_readiness.py coprono conteggi errati, JSON corrotto,
accesso admin/giudice, esclusione dei non iscritti, rollback eventi e lock occupato
simulato. Non sono un collaudo browser o una nuova prova reale di tutte le
interazioni concorrenti avvio/admin/giocatore.

Tipi e client GET admin sono stati aggiunti in c01b486; 822a85a corregge il primo
stop Prettier, seguito dalla CI frontend 39976945581 riuscita. La consultazione
bb7f0f7, corretta in 89cab3d e 72e4274, ha superato la CI 39986696961.
I quattro casi sul conteggio coprono copie senza mutazioni, vuoto e conteggi
14/16 non corretti artificialmente, non il rendering delle interazioni Svelte.

934333c aggiunge il pianificatore con cinque direzioni imposte: game_deck e
modification_inventory verso modification_pool, sponsor_inventory verso
sponsor_pool, modification_pool verso modification_inventory e sponsor_pool
verso sponsor_inventory. Una copia per clic; nessuna doppia sottrazione, pool
assente non creata, percorsi ambigui e immagini discordanti rifiutati. Snapshot,
ID e versioni restano invariati; errore tardivo senza applicazione parziale.

admin-card-identity.ts conserva strip().casefold() usando Unicode 15.0, senza NFC
o rimozione degli accenti. Dati verificati in Python; copia JavaScript senza tipi
confrontata in Node con Python su 1.112.064 scalari e nove casi composti. Non era
un type-check. Prettier locale era indisponibile, con ENOTCACHED e comando globale
assente: non inventare successi npm locali. b54cc84 conserva le aspettative dei
test e aggiunge commenti dei code point. Il bot f2dc492 formatta il test della
bozza; la lettura delle 19:21 della CI 39994183218 in coda e' solo storica.
Successivamente la CI 39995224182 e' risultata riuscita.

eedd729 aggiunge sessione locale e otto test: baseline, anteprima e registro
separati, blocco senza perdere la bozza, ripristino esplicito che conserva il
blocco. Nessun retry, rebase automatico o scrittura. d9ee662 aggiunge politica
modal-close, dodici casi parametrizzati e onrequestclose opzionale: la chiusura
e' delegata senza open=false automatico. Senza callback resta il comportamento
precedente; X disponibile e Escape/sfondo subordinati a closeOnOutside. Dodici
scenari Node sul corpo senza tipi erano riusciti; la CI 39997899845 su d9ee662
e' poi risultata riuscita. Non erano prove browser.

## Bozza collegata alla UI e correzioni di stile

c950510 collega i quattro componenti admin alla sessione. I tre contenitori del
pilota e le due pool restano separati in cinque sezioni con immagini; mazzo N/15
contando copie, pool assente distinta da vuota. Modal e CardTile riusati, nessun
nuovo scaffold, dipendenza o copia di risorse. I clic modificano solo la bozza,
con destinazioni imposte dal pianificatore e stato pendente propagato al modal.
Il blocco iniziale e le destinazioni assenti disabilitano i clic. Gli errori locali
sono separati dagli errori REST e non sostituiscono la sessione. Le letture tardive
sono ignorate dopo cambio contesto o smontaggio, senza annullare la rete gia' inviata.

Ripristino, ritorno ai piloti e chiusura richiedono conferma prima dello scarto.
Il ripristino usa la baseline, non una rilettura del server, e conserva il blocco.
Le conferme sono montate solo quando aperte; il modal sottostante evita di aprire
un secondo dialog su Escape quando un altro dialog modale e' gia' presente.
La navigazione con destinazione viene annullata e proposta prima della ripresa
con goto o location.assign. I clic sono disabilitati durante l'uscita; un errore
di goto conserva la bozza. Con riuso del componente, ripristino solo dopo successo
e se la sessione e' ancora quella originale. Ricarica o chiusura senza destinazione
usa la protezione browser tramite SvelteKit, non window.confirm.

Il primo lint si fermava su Prettier nei quattro componenti. 2cf25fd separa la
pubblicazione dello stile dai controlli successivi; il bot ceb12b1 formatta solo
quei quattro file. Il successivo log dell'autore mostra Prettier riuscito e un
errore ESLint svelte/no-navigation-without-resolve sulla chiamata goto(target.url).
788e6f5 aggiunge soltanto due commenti al componente: provenienza da
navigation.to.url.href e direttiva eslint-disable-next-line per quella chiamata
gia' risolta. Nessuna esclusione globale o modifica della logica eseguibile.

format-review-ui.yml resta limitato al ramo fase 16 e ai quattro componenti.
Usa npm ci e Prettier dal lockfile; puo' pubblicare il solo stile dopo write/check,
poi esegue check, lint, test e build e stampa la SHA controllata. Mantiene controllo
del ramo remoto e protezioni sui percorsi estranei. La CI ordinaria non cambia.
Un commit del bot, da solo, non prova il successo dei controlli successivi.

## Ultima CI effettivamente letta

La lettura del 2026-10-23 sulla testa 788e6f57de3927c0fa774883f77f40b6dc005e87
mostra la CI 40003767478 riuscita per Frontend (check, lint, test, build),
job 120586341966, Backend (pytest), Migrazioni (database di test) e Documenti
fase 16 dopo backend. Anche align-docs-pr 40003767471 risulta riuscito.
Questo verifica la toolchain dell'integrazione e del fix ESLint, non un collaudo
browser. Nessuna nuova esecuzione locale o conteggio complessivo di test/warning
dai log dei singoli comandi viene dichiarato. I dettagli sono in
PHASE_16_DRAFT_UI.md e PHASE_16_FORMATTING.md.

## Limiti, dati e prossimo passo

Il prossimo incremento resta da approvare: riepilogo testuale, conferma unica e
PUT dalla UI, gestione di errori/conflitti senza perdere la bozza, quindi live
tramite client SSE condiviso. Nessuna PUT, autosalvataggio, polling o nuovo stream
SSE e' gia' attivato nella schermata. Il blocco iniziale non e' un aggiornamento
live della gara. Restano verifiche dedicate e collaudo browser di clic ripetuti,
annullamento, Escape, chiusura e navigazione. Non dichiarare la fase completa.

Dopo i controlli applicativi riusciti riallineare i documenti e verificarne la
propagazione nei dieci documenti generali; gli allineamenti precedenti includono
08f3443 ed e2fbdea. La propagazione di questo aggiornamento deve ancora essere
verificata dopo il commit. Nessuna attesa di test applicativi per i soli docs,
nessuna chiusura/riapertura abituale della PR.

Deck.cards resta TEXT con array JSON name/path/copies e percorsi relativi ai media,
come confermato dall'autore il 2026-10-22. Nessuna conversione al vecchio esempio
path/value, migrazione, modifica di setup/avvio o accesso al database reale.

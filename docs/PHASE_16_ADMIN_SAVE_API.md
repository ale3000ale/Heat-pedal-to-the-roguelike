# Fase 16 - Salvataggio admin atomico

Data: 2026-10-22. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento supera il precedente limite delle sole letture. Frontend e
controllo di avvio gara da 15 copie restano da completare, senza merge implicito.

## Contratto di scrittura

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions contiene tutti i cinque contenitori: id/version
interi positivi, oppure null per le sole pool assenti. Ogni trasferimento ha solo
source e path; una copia per elemento, destinazione imposta dal dominio. Campi
extra, sostituzioni arbitrarie delle carte e destinazioni client sono rifiutati.

Ruolo, pilota visibile/iscritto, chiusura e gara/revisione non confermata vengono
ricontrollati nella transazione. Confronto id e versione anche dei contenitori
non toccati; pool assenti non sono create e non possono ricevere o fornire copie.
Conflitto: 409 e nessun retry automatico. Movimento non applicabile: 422.

SQLite acquisisce il lock prima delle letture autorevoli e scade le identita'
SQLAlchemy gia' caricate. Una transazione nativa esistente e' promossa con un
UPDATE senza righe; se lo snapshot non puo' essere promosso si rifiuta la scrittura.
Un solo commit per Deck ed eventi, rollback anche per errore nel registro eventi.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al database reale.

Solo le differenze effettive aggiornano le versioni. Nessuna differenza significa
nessun evento. Il mazzo puo' restare incompleto: nessuna aggiunta pool/mazzo o
sponsor/mazzo, nessuna doppia sottrazione. Risposta con snapshot e versioni nuove.
Dopo variazioni sono accodati cards.changed pubblico vuoto e privato al proprietario
con solo pilot_id: nessun dettaglio carte, regalo o notifica tasto S inventata.

## Verifiche e limiti

Preparati 27 casi in backend/tests/test_admin_pilot_card_save.py: cinque direzioni,
versioni di tutti i contenitori, blocchi, ruoli, input non ammessi, pool assenti o
riassegnate, rollback tardivo/eventi, bozza senza differenze, segnali privi di carte
e due salvataggi concorrenti con sessioni distinte su un SQLite temporaneo.
Test HTTP non eseguiti localmente. Eseguiti invece controlli sintattici e una prova
SQLite isolata: UPDATE senza righe blocca il secondo writer, non incrementa
versioni e rollback libera il lock. Il conteggio dei test e' stato corretto dopo
un NameError del solo script di analisi; nessun risultato HTTP PASS inventato.

Il workflow esegue dominio, letture e salvataggi prima del riallineamento generale.
La CI completa resta da leggere separatamente. Non chiudere/riaprire la PR come
procedura abituale. Per commit solo documentali non attendere la CI applicativa.
Restano da integrare il controllo esatto di 15 all'avvio e il coordinamento con
move_card, interfaccia con conferma testuale e protezione bozza, SSE condiviso e
collaudo browser. Il backend non dimostra ancora queste parti. Il formato resta
TEXT con array name/path/copies e percorsi correnti relativi ai media.

## Riscontro CI e diagnosi sincronizzazione - 2026-10-22 20:15 CEST

La lettura della CI 39827070228 riporta successo per backend pytest, frontend
check/lint/test/build e migrazioni sul database di test. Non e' una nuova
esecuzione dei test in locale e non costituisce un collaudo browser.
Il commit fbc7789 aggiunge il collegamento documentale alla CI, ma al controllo
seguente non risultavano nuovi check o un commit documentale successivo.
La lettura della PR 15 esponeva ancora db94beb: i risultati del connettore non
consentono di distinguere sincronizzazione GitHub da dati non aggiornati.
Nessuna causa certa attribuita a token, eventi o configurazione senza prove.

Per la verifica si usa un aggiornamento reale di questo documento con
create_or_update_file (API Contents), anziche' push_files. Nessuna modifica a
workflow, codice o DB reale e nessuna chiusura/riapertura o merge della PR.
L'effettivo aggiornamento della testa PR e l'avvio dei nuovi controlli vanno
verificati dopo la scrittura: questa nota non dichiara gia' risolto il problema
ne' gia' riallineati i dieci documenti generali. Per il solo aggiornamento
documentale non attendere la CI applicativa.

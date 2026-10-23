# Fase 16 - Client PUT e preparazione dalla baseline

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, migrazione, dipendenza nuova o accesso al database reale.

## Contratto e client gia' pubblicati

Letti schema Pydantic e router backend admin_pilot_cards.py. La richiesta contiene
versions per tutti i cinque contenitori e transfers con soli source/path. Solo
le due pool possono avere versione attesa null. Il PUT restituisce AdminPilotCardsRead.
Il backend mantiene validazione autorevole di campi extra, versioni e movimenti.

549e83e aggiunge tipi, client saveAdminPilotCards e test con fetch simulato.
Il bot f95c915 formatta soltanto il relativo test. La lettura della CI 40007864343
su f95c915 mostra frontend (check, lint, test, build), job 120600935709, e
migrazioni riusciti; in quella lettura il backend era ancora in corso. Non e'
un verde globale, una nuova esecuzione locale o una prova browser.

Il client usa api.ts, controlla gli ID, non muta la richiesta, non ritenta e non
esegue GET di conferma. Gli ApiError conservano lo stato. Risposta mancante,
illeggibile o di altro contesto genera AdminCardSaveResponseError, non prova
un rollback e non autorizza retry. Anche una perdita di rete non prova che il
server non abbia applicato la scrittura. Il client non valida l'intera struttura
runtime dello snapshot: controlla il contesto; non confondere tipi e validazione.

## Nuovo incremento: piano puro di salvataggio

admin-pilot-cards-save-plan.ts prepara richiesta, anteprima ricalcolata e riepilogo
ordinato dalla baseline e dal registro. Non usa l'anteprima memorizzata come
autorita'. Tutte le versioni iniziali, comprese quelle dei contenitori non toccati,
sono copiate senza arrotondamenti. Pool assenti restano null; contenitori
obbligatori assenti o metadati incoerenti vengono rifiutati.

Ogni movimento viene validato dal dominio prima del riepilogo; una riga descrive
una copia con nome e direzione. Sono operazioni in ordine, non differenze nette
o un'autorizzazione del server. Un registro vuoto resta vuoto. I percorsi rispettano
il limite di 255 code point. La richiesta serializza solo source/path, senza
destinazioni o copie arbitrarie. Tutti gli output sono indipendenti dalla sessione.
Nessuna rete, modifica degli input o applicazione parziale su errore tardivo.

## Verifiche e limiti

Test preparati per versioni iniziali, anteprima alterata, ordine, indipendenza
degli oggetti, pool assenti e incoerenti, contenitori obbligatori, ID/versioni
invalidi, blocchi, errore tardivo, percorsi Unicode e campi extra non trasmessi.
Nessuna nuova esecuzione locale di npm, Vitest, lint o build in questo incremento.
I nuovi moduli non sono ancora dichiarati verificati. Il formatter esistente e'
limitato al modulo del piano e al suo test, mantenendo Prettier dal lockfile e
tutti i controlli applicativi successivi. La CI ordinaria non e' modificata.

Il piano non e' ancora collegato ai componenti e non invia PUT. Restano conferma
unica, coordinamento della richiesta in corso, protezione dai doppi invii e
conservazione della bozza su errori/conflitti, poi live e collaudo browser.
Nessun autosalvataggio, polling o secondo stream SSE. Dopo i controlli riusciti
riallineare i documenti sorgente e generali; per i soli docs non attendere test
applicativi. Fase 16 non completa.

# Fase 16 - Trasporto PUT admin separato dalla UI

Data: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, migrazione, dipendenza nuova o accesso al database reale.

## Fonte e contratto

Letti realmente backend/app/schemas/admin_pilot_cards.py e il router omonimo.
AdminPilotCardsSave contiene versions e transfers; versioni dei tre contenitori
del pilota obbligatorie, solo modification_pool e sponsor_pool nullable. Ogni
movimento contiene source/path, senza destinazione client. Il PUT restituisce
AdminPilotCardsRead. Il backend mantiene la validazione autorevole e rifiuta
campi extra: i nuovi tipi TypeScript non sostituiscono tale controllo runtime.

## Incremento

admin-pilot-cards-save-types.ts descrive il contratto; save-api.ts espone
saveAdminPilotCards attraverso api.ts, senza cambiare il client GET. Verifica
gli ID prima della rete, esegue una sola PUT con i cookie gestiti dal trasporto
comune e restituisce lo snapshot del contesto atteso. Non muta la richiesta,
non ripete invii e non effettua GET di conferma. Gli ApiError restano distinguibili
per stato, inclusi 409, 422 e rete con stato 0.

Una risposta mancante, illeggibile o di altro contesto genera
AdminCardSaveResponseError: non prova un rollback. L'integrazione futura non
deve trasformarla in successo o ritentare automaticamente. Neppure l'errore
di rete garantisce che il server non abbia applicato la scrittura.

## Test e automazione

Test con fetch simulato preparati per contratto esatto, singola chiamata, versioni
restituite, pool assente, ID invalidi, errori HTTP/rete senza retry, contesto
difforme, JSON illeggibile e risposta 204 inattesa. Nessuna rete o scrittura reale
prevista nei test. Non sono stati eseguiti localmente npm, Vitest, lint o build
in questo incremento: i nuovi moduli restano da verificare con la toolchain.
Il formatter esistente ora e' limitato ai tre nuovi moduli; conserva lockfile,
Prettier, pubblicazione dello stile circoscritta e controlli applicativi successivi.
La CI ordinaria non cambia. Non dichiarare il verde dal solo commit del formatter.

## Limiti e seguito

Il client non e' ancora chiamato dai componenti: nessun pulsante Salva attivato
e nessuna PUT dalla schermata. Restano costruzione della richiesta dalla baseline,
riepilogo, conferma unica, coordinamento della richiesta in corso e conservazione
della bozza su errori e conflitti, poi integrazione live e collaudo browser.
Nessun autosalvataggio, polling o stream SSE aggiuntivo. Dopo i controlli riusciti
riallineare i documenti sorgente e generali; per i soli docs non attendere test
applicativi. La fase 16 non e' completa.

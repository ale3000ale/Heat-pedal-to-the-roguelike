# Impostazioni account e cambio password

Funzione richiesta e sviluppata direttamente su main il 24 ottobre 2026, senza ramo o PR dedicati.

Clic sul proprio nome nella barra: apre Impostazioni account con Password attuale, Nuova password e Conferma nuova password. La nuova password deve avere 8-128 caratteri e la conferma deve coincidere. Gli spazi non vengono rimossi e il conteggio segue i code point Unicode.

Il pulsante Cambia password invia una sola richiesta. Durante l invio campi, doppio invio e chiusura ordinaria del modal sono bloccati. I campi locali sono svuotati dopo la richiesta e alla chiusura; nessuna password viene salvata negli store globali o nel browser storage. Una navigazione o chiusura forzata non annulla una richiesta gia inviata. Le risposte tardive non aggiornano un modal smontato o un account diverso.

POST /api/auth/change-password richiede la sessione autenticata. Corpo JSON: current_password, new_password, confirm_password; campi aggiuntivi rifiutati. Le verifiche sono anche server-side. Successo 204 senza hash, password, token o nuovo cookie; 401 sessione assente/scaduta/revocata; 403 password attuale errata; 409 SQLite occupato; 422 dati o conferma non validi. La validazione Pydantic del corpo non riporta gli input negli errori del nuovo endpoint.

La scelta approvata mantiene il token e la scadenza della sessione corrente e revoca le altre sessioni dello stesso account. Hash e revoche vengono salvati insieme con lock SQLite, rilettura della sessione e rollback su errore. Gli altri account non vengono modificati. Il flusso SSE esistente ricontrolla la sessione e termina con auth.expired quando rileva una revoca; non si dichiara una disconnessione istantanea di ogni dispositivo o la cancellazione di dati gia visualizzati.

Password attuale errata o conferma diversa non cambiano dati. Per errore di rete o risposta server non conclusiva la UI segnala un esito incerto: nessun retry automatico e nessuna promessa di rollback. Verificare quale password risulta attiva prima di riprovare.

Nessuna migrazione, nuova dipendenza o modifica di schema. La funzione modifica a runtime soltanto l hash del proprio utente e le sue altre sessioni; l assistente non ha eseguito operazioni sul database reale. Setup, avvio LAN, carte e regole del gioco restano invariati. Su LAN HTTP il traffico non e cifrato: usare esclusivamente una rete fidata.

Verifiche eseguite sul runner prima di questo riallineamento: pytest backend, check frontend, lint, test frontend e build. Esecuzione 40114589745, checkout 97653418434af55ff904d36ab75d80fb0e8fe365, con formattazione limitata ai cinque file frontend prima dei controlli. Il checkout identifica l avvio della run; il successivo commit contiene i file formattati effettivamente verificati. Nessun conteggio complessivo o warning viene inventato. Non e un collaudo manuale browser, di rete, di concorrenza reale o una prova di tutte le condizioni di login simultaneo. Nessun test locale eseguito dall assistente.

Test aggiunti: backend/tests/test_password_change.py e frontend/src/lib/auth/password-change.spec.ts. Il backend copre ruoli, password attuale, conferma/lunghezze/campi extra, sessione conservata, altre sessioni revocate, account estranei, hash, login vecchio/nuovo, sessione scaduta/revocata, rollback simulato ed esclusione delle sessioni revocate dal polling SSE. Il frontend copre validazione, Unicode, payload, cookie, errori e assenza di retry; non costituisce test DOM del modal.

<!-- account-password-ui-current:start -->
## Aggiornamento grafico impostazioni e login - 24 ottobre 2026

Nel modal Impostazioni account la sezione Cambio password e a scomparsa e inizialmente chiusa a ogni nuova apertura. La chiusura della sezione svuota i campi. In login e nei tre campi del cambio password e disponibile Mostra/Nascondi, indipendente per ogni campo e nascosto inizialmente. La visibilita non viene salvata; il componente dedicato password-input.svelte e riusato nei due contesti. Durante le richieste i controlli relativi sono disabilitati. Backend, API, database e comportamento di revoca delle altre sessioni restano invariati.

Il fallimento Prettier su account-settings.svelte e stato affrontato applicando il formatter del lockfile solo a quel componente. Prima di questo riallineamento sono riusciti sul runner: npm run check, npm run lint, npm test e npm run build. Run 40124870171, checkout fc8d1f301a9350c555e4c4f2ab0d8ff6a7bb89ae, con componente formattato prima delle verifiche. Il successivo commit pubblica quello stile e questi documenti; non e una nuova esecuzione della CI sul commit risultante. Nessun test locale o conteggio inventato.

I test password-ui.spec.ts presenti nel candidato sono controlli di rendering server, non prove interattive di clic, tastiera o browser. Restano da verificare manualmente espansione/richiusura, reset alla riapertura e Mostra/Nascondi nei quattro campi. Nessuna migrazione, nuova dipendenza, modifica al lockfile o operazione sul DB reale.
<!-- account-password-ui-current:end -->

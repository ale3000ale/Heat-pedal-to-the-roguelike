# Produzione Wi-Fi/LAN

Aggiornamento: 24 ottobre 2026. Funzionalita sul ramo production-lan, PR #16 in bozza. Nessun merge in main autorizzato. Questa guida e il riferimento corrente per la produzione LAN; le istruzioni storiche sul tunnel non sono necessarie per questo utilizzo.

## Avvio

Usare la versione del ramo production-lan, con le dipendenze dell'applicazione gia installate e il database gia allineato. Dalla radice:

```sh
python heat.py production
```

In alternativa, eseguire python heat.py e scegliere la voce 7, Produzione Wi-Fi/LAN. Non viene chiesto un URL di tunnel. La produzione non installa dipendenze, non crea database e non applica migrazioni. Verifica in sola lettura la revisione Alembic; se non e allineata si interrompe. Backup e migrazioni vanno gestiti separatamente. Il comportamento storico di setup, migrate e start non e stato modificato da questo incremento.

Il launcher cerca gli IPv4 privati associati al nome del PC. Con un solo candidato lo verifica; con piu candidati permette di scegliere o inserire un IP manuale. Se il rilevamento non trova candidati richiede l'IP manuale. Non e un'enumerazione garantita di tutte le interfacce e non distingue automaticamente Wi-Fi, Ethernet, VPN e schede virtuali. Un bind temporaneo verifica che l'IP scelto sia utilizzabile sul PC.

Dopo la build e i controlli di avvio, il terminale mostra l'indirizzo effettivo, per esempio http://192.168.1.50:5173. Aprire esattamente quell'indirizzo nel browser sia sul PC sia sugli altri dispositivi. L'indirizzo e un esempio, non un valore fisso. Premere Ctrl+C per arrestare i processi.

## Origine esplicita facoltativa

```sh
python heat.py production --public-url http://192.168.1.50:5173
python heat.py production --public-url http://127.0.0.1:5173
```

Il primo comando richiede che l'IPv4 privato indicato appartenga al PC. Il secondo mantiene l'accesso solo dal PC. Rimane accettata un'origine HTTPS esplicita per gli utilizzi preesistenti, ma il launcher non crea servizi HTTPS o tunnel. Per la LAN non occorrono tunnel, account esterni o applicazioni client.

## Rete e sicurezza

Il gateway Node ascolta sulla sola interfaccia IPv4 LAN scelta, porta TCP 5173; non su 0.0.0.0. Il backend resta su 127.0.0.1:8000 con un worker. API, media ed eventi SSE passano attraverso il gateway. Restano i controlli esatti su Host e origine delle scritture, la rimozione degli header inoltrati forniti dal client e il proxy con destinazione fissa loopback. Il controllo di readiness e limitato a connessioni locali al PC.

HTTP e destinato esclusivamente a una rete privata fidata: non cifra password, cookie o altri dati in transito. Il cookie di sessione usa la configurazione HTTP prevista dal backend; Secure viene impostato per un'origine HTTPS, non per la LAN HTTP. Non esporre questa modalita a Internet. Nessuna regola firewall o router viene modificata automaticamente. Se il firewall blocca l'accesso, consentire solo TCP 5173 sulla rete privata e con ambito appropriato alla LAN. Non e richiesta l'apertura di porte sul router.

Il PC deve restare acceso e non sospeso. Gli altri dispositivi devono poter raggiungere la sua interfaccia: rete ospiti, isolamento client, VLAN o VPN possono impedirlo anche con lo stesso nome Wi-Fi. Se il DHCP cambia l'IP, riavviare e usare il nuovo indirizzo mostrato. Una prenotazione DHCP sul router puo stabilizzare l'indirizzo, ma non viene configurata dall'app.

## Verifiche e limiti

Codice formattato: 09a9aa594bd75650fe0af0556b67b64f2c0dcc15. Il commit del bot modifica soltanto frontend/production-lan.test.mjs, frontend/production-server.mjs e frontend/production-server.test.mjs.

Workflow Production runtime checks: esecuzione 40047553032, job runtime 120733397223, conclusione success il 24 ottobre 2026. Il workflow include test Python LAN/launcher, help CLI, controllo dei tipi, test frontend, test gateway/proxy, build standalone, smoke test della build e lint. I conteggi complessivi dei test e i warning non sono stati letti dai log e non vengono inventati. Questo esito non dichiara riuscita una nuova esecuzione di tutti i job della CI generale.

Da richiesta dell'autore, i test sono delegati alla CI salvo necessita specifiche; nessun nuovo test locale eseguito per questo riallineamento documentale. I test isolati precedenti restano storici, non sostituiscono la CI. Non sono ancora attestati un collaudo del browser da telefono/tablet e la raggiungibilita sulla rete fisica dell'autore.

Nessuna modifica a schema, migrazioni, dati reali, formato delle carte, risorse, dipendenze o lockfile. Nessun merge o ZIP finale implicito.

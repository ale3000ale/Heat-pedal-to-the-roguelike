# sv

Everything you need to build a Svelte project, powered by [`sv`](https://github.com/sveltejs/cli).

## Creating a project

If you're seeing this, you've probably already done this step. Congrats!

```sh
# create a new project
npx sv create my-app
```

To recreate this project with the same configuration:

```sh
# recreate this project
npx sv@0.17.1 create --template minimal --types ts --add prettier tailwindcss="plugins:typography" --install npm ./
```

## Developing

Once you've created a project and installed dependencies with `npm install` (or `pnpm install` or `yarn`), start a development server:

```sh
npm run dev

# or start the server and open the app in a new browser tab
npm run dev -- --open
```

## Building

To create a production version of your app:

```sh
npm run build
```

You can preview the production build with `npm run preview`.

> To deploy your app, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

<!-- production-lan-current:start -->

## Produzione Wi-Fi/LAN - aggiornamento corrente del 24 ottobre 2026

Per la produzione prevale questa sezione sulle indicazioni storiche relative al solo loopback o al tunnel. Funzionalita sul ramo production-lan, PR #16 in bozza, senza merge in main.

Dalla radice: python heat.py production, oppure voce 7 del menu. Senza URL esplicito seleziona l IPv4 privato del PC e mostra l indirizzo da usare anche sugli altri dispositivi della LAN. Nessun tunnel o client aggiuntivo richiesto. --public-url resta facoltativo per un origine esplicita, incluso il solo loopback.

Gateway sul solo IPv4 scelto:5173, backend su 127.0.0.1:8000 con un worker. API, immagini e SSE passano dal gateway; controlli Host/Origin mantenuti. HTTP solo su rete fidata: traffico non cifrato. Nessuna modifica automatica a firewall o router. PC acceso e dispositivi reciprocamente raggiungibili necessari.

Production non installa dipendenze, non crea DB e non applica migrazioni: verifica soltanto le revisioni in lettura. Il comportamento storico di setup/start/migrate resta invariato. Nessuna modifica a schema, dati reali, formato carte, risorse, dipendenze o lockfile.

Verifica osservata: Production runtime checks 40047553032, job runtime 120733397223, success sul codice formattato 09a9aa594bd75650fe0af0556b67b64f2c0dcc15. Include test launcher/LAN/gateway, tipi, frontend, build, smoke test e lint. Non e una nuova attestazione di tutti i job della CI generale, ne un collaudo Wi-Fi/browser. Conteggi e warning non letti dai log. Nessun nuovo test locale per questo riallineamento; nessun merge o ZIP finale implicito.

Guida operativa e limiti: [Produzione Wi-Fi/LAN](../docs/PRODUCTION_LAN.md).
<!-- production-lan-current:end -->

<!-- account-password-current:start -->

## Impostazioni account e cambio password - 24 ottobre 2026

Su main: clic sul proprio nome apre Impostazioni account. Password attuale e doppio inserimento della nuova; nuova password di 8-128 caratteri, validata anche sul server. La sessione corrente resta attiva con token e scadenza invariati; le altre sessioni dello stesso account vengono revocate. Hash e revoche sono nella stessa transazione con rollback su errore. Gli altri account non cambiano.

Endpoint POST /api/auth/change-password, autenticato, successo 204. Nessuna migrazione o dipendenza nuova. Nessuna modifica al DB reale eseguita dall assistente. Durante l invio niente doppio invio o chiusura ordinaria; campi svuotati dopo la richiesta e alla chiusura. Errori di rete: esito incerto e nessun retry automatico. SSE riusa il controllo periodico delle sessioni.

Riallineamento dopo pytest backend, tipi, lint, test frontend e build riusciti nel runner: run 40114589745, checkout 97653418434af55ff904d36ab75d80fb0e8fe365, formattazione circoscritta applicata prima delle verifiche. Nessun conteggio inventato, test locale o collaudo browser attestato.

Dettagli, limiti e prove: [Impostazioni account](../docs/ACCOUNT_SETTINGS.md).
<!-- account-password-current:end -->

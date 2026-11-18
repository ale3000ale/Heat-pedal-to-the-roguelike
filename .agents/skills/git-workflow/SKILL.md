---
name: git-workflow
description: "Usa per qualsiasi operazione Git nel repository Heat: scegliere o creare un branch, preparare lo staging, scrivere il messaggio di commit, fondere una release, creare un tag, pushare o ripulire branch. Applica le regole di branch, commit e versioni del repository e impone un protocollo di trasparenza con autorizzazione esplicita prima di ogni modifica a storia o remoto."
---

# Git workflow — Heat

`AGENTS.md` è la fonte autorevole su regole, sicurezza e comandi. Questa skill descrive la procedura operativa; in caso di conflitto vince `AGENTS.md`. Non autorizza da sola nessuna scrittura su Git: commit, push, merge, tag e cancellazione di branch richiedono un'autorizzazione esplicita dell'autore.

## 1. Trasparenza

1. Dichiara obiettivo, file che tocchi e comandi che eseguirai **prima** di eseguirli, e attendi approvazione.
2. Mostra sempre `git status --short --branch` e il riepilogo del diff prima di ogni commit.
3. Procedi un passo per volta: nessun commit, merge, tag o cancellazione dentro un unico comando composito.
4. Nessun automatismo silenzioso: niente hook che committano, niente script che riscrivono file, niente `git add -A` implicito.
5. Riporta solo ciò che hai osservato davvero (output del comando, log, esito locale). La CI non osservata si dichiara come tale.
6. Un messaggio vuoto non è approvazione.

## 2. Modello dei branch

```
main                  ultima versione stabile, solo merge da release/*
└── release/X.Y       linea di rilascio attiva
    ├── feat/<slug>   nuova funzionalità
    ├── fix/<slug>    correzione
    ├── hotfix/<slug> correzione urgente su una linea mantenuta
    └── chore/<slug>  manutenzione, documentazione, CI
```

| Branch | Nasce da | Muore in | Chi lo cancella |
|---|---|---|---|
| `main` | — | — | mai |
| `release/X.Y` | `main`, a inizio ciclo | `main`, dopo il rilascio | dopo il merge e il tag |
| rami di lavoro | `release/X.Y` attivo | `release/X.Y` via PR | dopo il merge |

Direzione unica: lavoro → `release` → `main`.

## 3. Nomi

- `release/X.Y` con numeri interi: `release/0.9`, `release/1.0`.
- Rami di lavoro: `feat/0.9-negozio-filtri`, `fix/0.8-qr-ci`, `hotfix/0.8-login`, `chore/0.8.1-convenzione`.
- Slug minuscolo, parole separate da trattini, senza date e senza punti.
- La versione vive **solo** nei tag (`v0.9.1`), mai nei nomi dei branch.
- `main` non si fonde nei rami di lavoro senza un motivo concordato.

## 4. Messaggi di commit

Formato Conventional Commits:

```
type(scope): oggetto

Corpo: cosa cambia e perché. Una riga vuota dopo l'oggetto.

Verifiche: comando e risultato osservato.
```

- `type`: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `style`, `perf`.
- `scope` facoltativo: area toccata (`frontend`, `backend`, `docs`, `ci`).
- Oggetto in italiano, imperativo, minuscolo, senza punto finale, entro 72 caratteri.
- Esempi corretti: `fix: risolve l'errore lint delle voci di navigazione`, `docs: sposta la cronologia in docs/HISTORY.md`.
- Esempi da evitare: `fix`, `aggiornamenti vari`, `WIP`, un commit con tre modifiche non correlate.

## 5. Prima del commit

1. Verifica il branch: `git status --short --branch`. Se non è quello atteso, fermati.
2. Distingui modifiche tue, modifiche preesistenti e file non tracciati: non assumere che siano tue.
3. Stage esplicito per percorso: `git add -- <file> ...`. Mai `git add -A` o `git add .` senza aver elencato e approvato i file.
4. `git diff --cached --check` deve uscire 0.
5. Leggi `git diff --cached` e `git diff --cached --stat`: il commit deve contenere solo lo scope approvato.
6. Esegui i controlli pertinenti ai file toccati, senza `setup` né migrazioni:

| Area toccata | Controllo |
|---|---|
| `backend/` | da `backend/`: `.venv/Scripts/python.exe -m pytest -q` (POSIX `.venv/bin/python`) |
| `frontend/` | da `frontend/`: `npm run check`, `npm run lint`, `npm test`, `npm run build` |
| `tools/` | da root: `python -m unittest tools.test_lan tools.test_production tools.test_production_lan -v` |
| solo `docs/`, `README.md`, `AGENTS.md`, skill | `git diff --check` e coerenza dei riferimenti |

7. Se un controllo fallisce, non committare: correggi o riporta il problema.

## 6. Rilascio

```bash
git switch main && git pull --ff-only
git merge --no-ff release/X.Y -m "release: X.Y.Z"
git tag -a vX.Y.Z -m "X.Y.Z"
git push origin main
git push origin vX.Y.Z
git branch -d release/X.Y
git push origin --delete release/X.Y
```

Prima del merge aggiorna `docs/CHANGELOG.md` (voce con data) e la sezione `## Patch` del README. Il tag è annotato e non si sposta: se il rilascio è sbagliato si pubblica una nuova versione, non si ritagga.

## 7. Hotfix su una linea mantenuta

```bash
git switch -c release/X.Y vX.Y.Z          # solo se il branch non esiste più
git switch -c hotfix/X.Y-<slug> release/X.Y
# correzione e controlli
# PR verso release/X.Y, poi release/X.Y -> main, nuovo tag vX.Y.Z+1
```

Se `main` è molto avanti e il merge produce conflitti non pertinenti, valuta `git cherry-pick` del solo commit di correzione, dichiarandolo nel report.

## 8. Divieti

- Commit diretti su `main` o su `release/*`.
- `push --force`, `push -f`, riscrittura di storia già pubblicata, `--amend` su commit pushati.
- `git commit --no-verify`.
- Cancellare un branch non fuso: verifica prima con `git merge-base --is-ancestor <branch> main`. `git branch -d` deve poter fallire; non usare `-D` senza controllo esplicito.
- Committare file non elencati, `.env`, database reali, backup `*.bak`, media caricati, `node_modules`, ambienti virtuali.
- Ri-taggare o spostare un tag esistente.

## 9. Ripulire i branch

1. `git fetch --prune`.
2. Elenca i branch e, per ciascuno, `git rev-list --count main..<branch>` (deve essere 0) e `git merge-base --is-ancestor <branch> main`.
3. Mostra l'elenco e attendi autorizzazione esplicita.
4. `git branch -d <branch>` per i locali, `git push origin --delete <branch>` per i remoti.

## 10. Report finale

Chiudi con: branch di partenza e di arrivo, commit creati con SHA, tag creati, file toccati, comandi eseguiti con esito osservato, operazioni remote eseguite, e ciò che resta non verificato (per esempio l'esito della CI).

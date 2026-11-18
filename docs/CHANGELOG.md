# Changelog

Le versioni seguono `major.minor.patch` e ogni voce corrisponde a un tag annotato `vX.Y.Z` su `main`. La data indica il giorno di rilascio e non fa parte del numero di versione. Le versioni precedenti usavano lo schema `Beta M.m.DDMMYYYY`; la cronologia dettagliata resta in `docs/HISTORY.md`.

## 0.8.1 — 2026-11-18

### Corretto

- Le voci di navigazione usano `resolve()` di `$app/paths`, come richiesto dalla regola `svelte/no-navigation-without-resolve`.
- Il test del QR non richiede più `qrcode` installato: la suite di `production-runtime.yml` gira anche senza dipendenze.

### Aggiunto

- Drawer di navigazione per schermi sotto i 768 px.

### Migliorato

- Caricamento dei font senza bloccare il render della pagina.

### Documentazione

- README pubblico con modalità roguelike, requisiti, comandi e struttura; cronologia spostata in `docs/HISTORY.md`.
- Convenzione di branch, commit e versioni in `AGENTS.md`, con la skill `.agents/skills/git-workflow`.

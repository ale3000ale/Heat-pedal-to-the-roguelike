#!/usr/bin/env node
// Esegue in sequenza i controlli del frontend: format, check, lint, test.
// Funziona su Windows, macOS e Linux: serve solo Node (già richiesto da npm).
//
// Uso, da qualsiasi cartella del progetto:
//   node tools/check-frontend.mjs
//   node tools/check-frontend.mjs --keep-going   (non si ferma al primo errore)

import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'frontend');
const keepGoing = process.argv.includes('--keep-going');
const steps = ['format', 'check', 'lint', 'test'];

const results = [];
for (const step of steps) {
	console.log(`\n▶ npm run ${step}\n`);
	const started = Date.now();
	// shell: true serve su Windows, dove npm è un file .cmd.
	// stdin ignorato: nessun passo deve restare in attesa di input da tastiera
	// (succedeva quando lo script era lanciato da heat.py).
	const run = spawnSync('npm', ['run', step], {
		cwd: frontend,
		stdio: ['ignore', 'inherit', 'inherit'],
		shell: true,
		env: { ...process.env, CI: 'true' }
	});
	const ok = run.status === 0;
	results.push({ step, ok, seconds: ((Date.now() - started) / 1000).toFixed(1) });
	if (!ok && !keepGoing) break;
}

console.log('\n--- Riepilogo ---');
for (const { step, ok, seconds } of results) {
	console.log(`${ok ? '✔' : '✖'} ${step.padEnd(7)} ${seconds}s`);
}
for (const step of steps.slice(results.length)) {
	console.log(`– ${step.padEnd(7)} non eseguito`);
}

const failed = results.filter((r) => !r.ok);
if (failed.length > 0) {
	console.log(`\nFalliti: ${failed.map((r) => r.step).join(', ')}`);
	process.exit(1);
}
console.log('\nTutto a posto.');

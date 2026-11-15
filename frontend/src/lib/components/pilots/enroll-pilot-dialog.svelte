<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import Modal from '$lib/components/shared/modal.svelte';
	import type { Pilot } from '$lib/types';

	// Finestra per iscrivere un proprio pilota a un campionato attivo, in due passi:
	// prima si sceglie il pilota, poi si conferma. `pilots` contiene solo i piloti iscrivibili;
	// `onenroll` fa la richiesta e, se fallisce, lancia un errore che la finestra mostra.
	let {
		open = $bindable(false),
		championshipName,
		pilots,
		onenroll
	}: {
		open?: boolean;
		championshipName: string;
		pilots: Pilot[];
		onenroll: (pilotId: number) => Promise<void>;
	} = $props();

	const selectClass =
		'h-8 w-full rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let step = $state<'choose' | 'confirm'>('choose');
	let selectedId = $state('');
	let busy = $state(false);
	let error = $state<string | null>(null);

	let selected = $derived(pilots.find((p) => String(p.id) === selectedId) ?? null);

	// A ogni apertura si riparte dalla scelta del pilota, senza errori o scelte precedenti.
	$effect(() => {
		if (!open) return;
		step = 'choose';
		selectedId = '';
		error = null;
	});

	async function confirm() {
		if (!selected) return;
		busy = true;
		error = null;
		try {
			await onenroll(selected.id);
			open = false;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<Modal bind:open title="Iscrivi un tuo pilota">
	{#if pilots.length === 0}
		<p class="text-sm text-muted-foreground">Nessun tuo pilota può essere iscritto.</p>
		<p class="mt-2 text-sm text-muted-foreground">
			Serve un pilota con un team e non iscritto a un campionato attivo.
		</p>
		<div class="mt-4 flex justify-end">
			<Button variant="outline" onclick={() => (open = false)}>Chiudi</Button>
		</div>
	{:else if step === 'choose' || !selected}
		<p class="mb-3 text-sm text-muted-foreground">
			Scegli il pilota da iscrivere a {championshipName}.
		</p>
		<select class={selectClass} bind:value={selectedId} aria-label="Pilota da iscrivere">
			<option value="">Scegli un pilota</option>
			{#each pilots as p (p.id)}
				<option value={String(p.id)}>{p.name}</option>
			{/each}
		</select>
		<div class="mt-4 flex justify-end gap-2">
			<Button variant="outline" onclick={() => (open = false)}>Annulla</Button>
			<Button disabled={selected === null} onclick={() => (step = 'confirm')}>Avanti</Button>
		</div>
	{:else}
		<p class="text-sm">Iscrivere {selected.name} a {championshipName}?</p>
		<p class="mt-2 text-sm text-muted-foreground">
			L'iscrizione reimposta il pilota: inventari, mazzo da gioco, oro, sponsor e punti.
		</p>
		{#if error}
			<p class="mt-3 text-sm text-destructive" role="alert">{error}</p>
		{/if}
		<div class="mt-4 flex justify-end gap-2">
			<Button variant="outline" disabled={busy} onclick={() => (step = 'choose')}>Indietro</Button>
			<Button disabled={busy} onclick={confirm}>Conferma iscrizione</Button>
		</div>
	{/if}
</Modal>

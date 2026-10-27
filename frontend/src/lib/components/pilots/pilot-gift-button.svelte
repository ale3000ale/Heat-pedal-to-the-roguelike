<script lang="ts">
	import { giveRandomCard, undoGift } from '$lib/cards/card-play-api';
	import { secondsLeft, UNDO_SECONDS } from '$lib/cards/gift-undo';
	import ConfirmDialog from '$lib/components/shared/confirm-dialog.svelte';
	import { Button } from '$lib/components/ui/button';

	// Tasto S di un pilota: giudice e admin assegnano una carta sponsor casuale. La carta
	// ottenuta non viene mostrata a chi la assegna: il popup lo vede solo il giocatore.
	// Dopo l'assegnazione, per 60 secondi, chi ha premuto S può annullarla.
	// Con `showName` falso il nome non compare: serve dove la riga ha già il nome del pilota.
	let {
		championshipId,
		pilot,
		showName = true
	}: {
		championshipId: number;
		pilot: { id: number; name: string };
		showName?: boolean;
	} = $props();

	let confirmOpen = $state(false);
	let busy = $state(false);
	let message = $state<string | null>(null);
	let error = $state<string | null>(null);
	// Assegnazione appena fatta, annullabile fino a `deadline` (millisecondi).
	let giftId = $state<number | null>(null);
	let deadline = $state(0);
	let now = $state(Date.now());

	let left = $derived(giftId === null ? 0 : secondsLeft(deadline, now));

	// Finché l'annullo è possibile aggiorna l'orologio ogni secondo; poi si ferma.
	$effect(() => {
		if (giftId === null) return;
		const timer = setInterval(() => {
			now = Date.now();
			if (secondsLeft(deadline, now) === 0) clearInterval(timer);
		}, 1000);
		return () => clearInterval(timer);
	});

	// Chiede al backend una carta casuale per il pilota; l'errore (es. pool vuota) viene
	// mostrato sotto il tasto.
	async function give() {
		error = null;
		message = null;
		busy = true;
		try {
			const given = await giveRandomCard(championshipId, pilot.id);
			giftId = given.id;
			now = Date.now();
			deadline = now + UNDO_SECONDS * 1000;
			message = `Carta assegnata a ${pilot.name}.`;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}

	// Annulla l'assegnazione appena fatta: la carta torna nella pool sponsor.
	async function undo() {
		if (giftId === null) return;
		error = null;
		busy = true;
		try {
			await undoGift(championshipId, giftId);
			giftId = null;
			message = 'Assegnazione annullata.';
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<div class={showName ? 'flex flex-wrap items-center gap-2' : 'contents'}>
	{#if showName}
		<span class="min-w-32 flex-1 text-sm font-medium">{pilot.name}</span>
	{/if}
	<Button
		type="button"
		size="sm"
		onclick={() => (confirmOpen = true)}
		disabled={busy}
		aria-label={`Assegna una carta sponsor a ${pilot.name}`}
	>
		S
	</Button>
	{#if message || error}
		<div class="flex w-full flex-wrap items-center gap-2 text-xs">
			{#if message}
				<span class="text-muted-foreground" role="status">{message}</span>
			{/if}
			{#if giftId !== null && left > 0}
				<Button type="button" size="sm" variant="outline" disabled={busy} onclick={undo}>
					Annulla ({left} s)
				</Button>
			{/if}
			{#if error}
				<span class="text-destructive" role="alert">{error}</span>
			{/if}
		</div>
	{/if}
</div>

<ConfirmDialog
	bind:open={confirmOpen}
	title="Assegnare una carta sponsor?"
	message={`Vuoi dare una carta sponsor casuale a ${pilot.name}?`}
	confirmLabel="Assegna"
	onconfirm={give}
/>

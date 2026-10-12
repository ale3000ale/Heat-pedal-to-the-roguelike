<script lang="ts">
	import { giveRandomCard } from '$lib/card-play-api';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import { Button } from '$lib/components/ui/button';

	// Tasto S di un pilota nella pagina della gara: giudice e admin assegnano una carta
	// sponsor casuale. La carta ottenuta non viene mostrata a chi la assegna: il popup
	// lo vede solo il giocatore.
	let {
		championshipId,
		pilot
	}: {
		championshipId: number;
		pilot: { id: number; name: string };
	} = $props();

	let confirmOpen = $state(false);
	let busy = $state(false);
	let done = $state(false);
	let error = $state<string | null>(null);

	// Chiede al backend una carta casuale per il pilota; l'errore (es. pool vuota) viene
	// mostrato sotto il tasto.
	async function give() {
		error = null;
		done = false;
		busy = true;
		try {
			await giveRandomCard(championshipId, pilot.id);
			done = true;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<div class="flex flex-wrap items-center gap-2">
	<span class="min-w-32 flex-1 text-sm font-medium">{pilot.name}</span>
	<Button
		type="button"
		size="sm"
		onclick={() => (confirmOpen = true)}
		disabled={busy}
		aria-label={`Assegna una carta sponsor a ${pilot.name}`}
	>
		S
	</Button>
	{#if done}
		<span class="text-sm text-muted-foreground" role="status">Carta assegnata a {pilot.name}.</span>
	{/if}
</div>
{#if error}
	<p class="text-sm text-destructive" role="alert">{error}</p>
{/if}

<ConfirmDialog
	bind:open={confirmOpen}
	title="Assegnare una carta sponsor?"
	message={`Vuoi dare una carta sponsor casuale a ${pilot.name}?`}
	confirmLabel="Assegna"
	onconfirm={give}
/>

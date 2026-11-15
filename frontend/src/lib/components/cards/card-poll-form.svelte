<script lang="ts">
	import { onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { fetchCardPoll, saveCardPoll } from '$lib/cards/card-play-api';
	import { submitCardPoll } from '$lib/cards/card-poll-form';
	import { CARD_POLL_DEFAULT, CARD_POLL_MAX, CARD_POLL_MIN } from '$lib/cards/card-poll-validation';

	const inputClass =
		'h-9 w-24 rounded-md border border-input bg-background px-3 text-sm disabled:opacity-50';

	let text = $state(String(CARD_POLL_DEFAULT));
	let error = $state<string | null>(null);
	let status = $state<string | null>(null);
	let loaded = $state(false);
	let busy = $state(false);

	onMount(async () => {
		try {
			text = String((await fetchCardPoll()).seconds);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			loaded = true;
		}
	});

	async function save(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		status = null;
		busy = true;
		const result = await submitCardPoll(text, saveCardPoll);
		if (result.ok) {
			text = String(result.seconds);
			status = result.message;
		} else {
			error = result.message;
		}
		busy = false;
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>Controllo notifiche carte</Card.Title>
		<Card.Description>
			Ogni quanti secondi i giocatori controllano se hanno ricevuto una carta.
		</Card.Description>
	</Card.Header>
	<Card.Content>
		{#if !loaded}
			<p class="text-sm text-muted-foreground">Caricamento…</p>
		{:else}
			<form class="space-y-4" onsubmit={save}>
				<label class="flex items-center justify-between gap-3 text-sm">
					<span>Secondi ({CARD_POLL_MIN}-{CARD_POLL_MAX})</span>
					<input class={inputClass} type="text" bind:value={text} />
				</label>

				{#if error}
					<p class="text-sm text-destructive" role="alert">{error}</p>
				{/if}
				{#if status}
					<p class="text-sm text-muted-foreground" role="status">{status}</p>
				{/if}
				<Button type="submit" disabled={busy}>Salva</Button>
			</form>
		{/if}
	</Card.Content>
</Card.Root>

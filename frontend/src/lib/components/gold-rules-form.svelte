<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	type GoldRules = { base: number; positions: number[]; other: number };

	let {
		url,
		title,
		description,
		editable = false
	}: { url: string; title: string; description: string; editable?: boolean } = $props();

	const places = ['1ª', '2ª', '3ª', '4ª', '5ª', '6ª'];
	const inputClass =
		'h-9 w-24 rounded-md border border-input bg-background px-3 text-sm disabled:opacity-50';

	let base = $state(20);
	let positions = $state([0, 0, 0, 0, 0, 0]);
	let other = $state(0);
	let error = $state<string | null>(null);
	let saved = $state(false);
	let loaded = $state(false);
	let busy = $state(false);

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	function show(rules: GoldRules) {
		base = rules.base;
		positions = [...rules.positions];
		other = rules.other;
	}

	onMount(async () => {
		try {
			show(await api<GoldRules>(url));
		} catch (e) {
			error = message(e);
		} finally {
			loaded = true;
		}
	});

	async function save(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		saved = false;
		busy = true;
		try {
			show(await api<GoldRules>(url, { method: 'PUT', body: { base, positions, other } }));
			saved = true;
		} catch (e) {
			error = message(e);
		} finally {
			busy = false;
		}
	}
</script>

<Card.Root>
	<Card.Header>
		<Card.Title>{title}</Card.Title>
		<Card.Description>{description}</Card.Description>
	</Card.Header>
	<Card.Content>
		{#if !loaded}
			<p class="text-sm text-muted-foreground">Caricamento…</p>
		{:else}
			<form class="space-y-4" onsubmit={save}>
				<label class="flex items-center justify-between gap-3 text-sm">
					<span>Oro base a ogni iscritto, dopo ogni gara</span>
					<input
						class={inputClass}
						type="number"
						min={0}
						max={10000}
						bind:value={base}
						disabled={!editable}
						required
					/>
				</label>

				<div class="space-y-2">
					<p class="text-sm font-medium">Oro in più o in meno in base alla posizione</p>
					{#each places as place, i (place)}
						<label class="flex items-center justify-between gap-3 text-sm">
							<span>{place} posizione</span>
							<input
								class={inputClass}
								type="number"
								min={-1000}
								max={1000}
								bind:value={positions[i]}
								disabled={!editable}
								required
							/>
						</label>
					{/each}
					<label class="flex items-center justify-between gap-3 text-sm">
						<span>Dalla 7ª posizione in poi</span>
						<input
							class={inputClass}
							type="number"
							min={-1000}
							max={1000}
							bind:value={other}
							disabled={!editable}
							required
						/>
					</label>
				</div>

				{#if error}
					<p class="text-sm text-destructive" role="alert">{error}</p>
				{/if}
				{#if saved}
					<p class="text-sm text-muted-foreground" role="status">Salvato.</p>
				{/if}
				{#if editable}
					<Button type="submit" disabled={busy}>Salva</Button>
				{:else}
					<p class="text-sm text-muted-foreground">Sola lettura.</p>
				{/if}
			</form>
		{/if}
	</Card.Content>
</Card.Root>

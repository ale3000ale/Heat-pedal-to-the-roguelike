<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	const selectClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let championship = $state<ChampionshipDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let busy = $state(false);
	let selectedPilot = $state('');

	// Classifica: più punti prima; a parità, in ordine alfabetico.
	let ranking = $derived(
		championship
			? [...championship.pilots].sort((a, b) => b.point - a.point || a.name.localeCompare(b.name))
			: []
	);
	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Piloti che hanno un team e non sono già iscritti a questo campionato.
	let candidates = $derived(
		myPilots.filter(
			(p) => p.team_id !== null && !championship?.pilots.some((entrant) => entrant.id === p.id)
		)
	);

	async function reload() {
		championship = await api<ChampionshipDetail>(`/championships/${page.params.id}`);
	}

	onMount(async () => {
		try {
			[championship, myPilots] = await Promise.all([
				api<ChampionshipDetail>(`/championships/${page.params.id}`),
				api<Pilot[]>('/pilots')
			]);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});

	async function enroll(event: SubmitEvent) {
		event.preventDefault();
		if (selectedPilot === '') return;
		actionError = null;
		busy = true;
		try {
			await api(`/championships/${page.params.id}/pilots`, {
				method: 'POST',
				body: { pilot_id: Number(selectedPilot) }
			});
			selectedPilot = '';
			await reload();
		} catch (e) {
			actionError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>{championship ? championship.name : 'Campionato'} - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/championships')} class="text-sm text-muted-foreground hover:text-foreground">
		← Campionati
	</a>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else if !championship}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div>
			<h1 class="text-2xl font-bold">{championship.name}</h1>
			<p class="text-sm text-muted-foreground">
				{new Date(championship.date).toLocaleDateString('it-IT')} ·
				{championship.is_closed ? 'Chiuso' : 'Attivo'}
			</p>
		</div>

		{#if !championship.is_closed}
			<Card.Root>
				<Card.Header>
					<Card.Title>Iscrivi un tuo pilota</Card.Title>
					<Card.Description>
						Il pilota deve avere un team e non essere in un altro campionato attivo. L'iscrizione lo
						reimposta.
					</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if candidates.length === 0}
						<p class="text-sm text-muted-foreground">Nessun tuo pilota può essere iscritto.</p>
					{:else}
						<form onsubmit={enroll} class="flex flex-wrap items-center gap-2">
							<select
								class={selectClass}
								bind:value={selectedPilot}
								required
								aria-label="Pilota da iscrivere"
							>
								<option value="">Scegli un pilota</option>
								{#each candidates as p (p.id)}
									<option value={String(p.id)}>{p.name}</option>
								{/each}
							</select>
							<Button type="submit" size="sm" disabled={busy || selectedPilot === ''}>
								Iscrivi
							</Button>
						</form>
					{/if}
					{#if actionError}
						<p class="mt-3 text-sm text-destructive" role="alert">{actionError}</p>
					{/if}
				</Card.Content>
			</Card.Root>
		{/if}

		<Card.Root>
			<Card.Header>
				<Card.Title>Classifica</Card.Title>
				<Card.Description>{championship.pilots_count} piloti iscritti</Card.Description>
			</Card.Header>
			<Card.Content>
				{#if ranking.length === 0}
					<p class="text-sm text-muted-foreground">Nessun pilota iscritto.</p>
				{:else}
					<ol class="divide-y">
						{#each ranking as entrant, i (entrant.id)}
							<li class="flex items-center gap-3 py-2">
								<span class="w-6 text-right text-sm text-muted-foreground">{i + 1}</span>
								<span class="flex-1 font-medium">
									{entrant.name}
									{#if myIds.has(entrant.id)}
										<span class="ml-2 text-xs text-muted-foreground">(tuo)</span>
									{/if}
								</span>
								<span class="text-sm">{entrant.point} punti</span>
							</li>
						{/each}
					</ol>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>

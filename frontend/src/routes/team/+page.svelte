<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import type { Pilot, Team } from '$lib/types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';

	const selectClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let teams = $state<Team[]>([]);
	let pilots = $state<Pilot[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);
	let busy = $state(false);

	let newTeam = $state('');
	let newPilot = $state('');
	let newPilotTeam = $state('');
	let editing = $state<{ kind: 'team' | 'pilot'; id: number; name: string } | null>(null);

	// Piloti raggruppati per team, e piloti senza team.
	let groups = $derived(
		teams.map((team) => ({ team, pilots: pilots.filter((p) => p.team_id === team.id) }))
	);
	let freePilots = $derived(pilots.filter((p) => p.team_id === null));

	async function reload() {
		[teams, pilots] = await Promise.all([api<Team[]>('/teams'), api<Pilot[]>('/pilots')]);
	}

	// Esegue un'azione, poi ricarica i dati. Restituisce false se è fallita
	// (il messaggio del backend resta in `error`).
	async function run(action: () => Promise<void>): Promise<boolean> {
		error = null;
		busy = true;
		try {
			await action();
			await reload();
			return true;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
			return false;
		} finally {
			busy = false;
		}
	}

	onMount(async () => {
		await run(async () => {});
		loaded = true;
	});

	async function createTeam(event: SubmitEvent) {
		event.preventDefault();
		if (await run(() => api('/teams', { method: 'POST', body: { name: newTeam } }))) {
			newTeam = '';
		}
	}

	async function createPilot(event: SubmitEvent) {
		event.preventDefault();
		const team_id = newPilotTeam === '' ? null : Number(newPilotTeam);
		if (await run(() => api('/pilots', { method: 'POST', body: { name: newPilot, team_id } }))) {
			newPilot = '';
		}
	}

	async function saveEdit(event: SubmitEvent) {
		event.preventDefault();
		if (!editing) return;
		const { kind, id, name } = editing;
		const path = kind === 'team' ? `/teams/${id}` : `/pilots/${id}`;
		if (await run(() => api(path, { method: 'PATCH', body: { name } }))) editing = null;
	}

	async function changeTeam(pilot: Pilot, value: string) {
		const team_id = value === '' ? null : Number(value);
		await run(() => api(`/pilots/${pilot.id}/team`, { method: 'PUT', body: { team_id } }));
	}

	async function removeTeam(team: Team) {
		if (!confirm(`Eliminare il team "${team.name}" e tutti i suoi piloti?`)) return;
		await run(() => api(`/teams/${team.id}`, { method: 'DELETE' }));
	}

	async function removePilot(pilot: Pilot) {
		if (!confirm(`Eliminare il pilota "${pilot.name}"?`)) return;
		await run(() => api(`/pilots/${pilot.id}`, { method: 'DELETE' }));
	}
</script>

<svelte:head><title>Team e piloti - Heat</title></svelte:head>

{#snippet nameCell(kind: 'team' | 'pilot', id: number, name: string)}
	{#if editing && editing.kind === kind && editing.id === id}
		<form onsubmit={saveEdit} class="flex flex-1 items-center gap-2">
			<Input bind:value={editing.name} required class="h-8" />
			<Button type="submit" size="sm" disabled={busy}>Salva</Button>
			<Button type="button" size="sm" variant="ghost" onclick={() => (editing = null)}>
				Annulla
			</Button>
		</form>
	{:else}
		<span class="flex-1 font-medium">{name}</span>
		<Button size="sm" variant="ghost" onclick={() => (editing = { kind, id, name })}>
			Rinomina
		</Button>
	{/if}
{/snippet}

{#snippet pilotRow(p: Pilot)}
	<li class="flex flex-wrap items-center gap-2 py-2">
		{@render nameCell('pilot', p.id, p.name)}
		<span class="text-xs text-muted-foreground">
			Gold {p.gold} · Sponsor {p.sponsor} · Punti {p.point}
		</span>
		<select
			class={selectClass}
			value={p.team_id === null ? '' : String(p.team_id)}
			onchange={(e) => changeTeam(p, e.currentTarget.value)}
			disabled={busy}
			aria-label="Team di {p.name}"
		>
			<option value="">Nessun team</option>
			{#each teams as t (t.id)}
				<option value={String(t.id)}>{t.name}</option>
			{/each}
		</select>
		<Button
			size="sm"
			variant="ghost"
			class="text-destructive"
			disabled={busy}
			onclick={() => removePilot(p)}
		>
			Elimina
		</Button>
	</li>
{/snippet}

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<h1 class="text-2xl font-bold">Team e piloti</h1>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	{#if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2">
			<Card.Root>
				<Card.Header><Card.Title>Nuovo team</Card.Title></Card.Header>
				<Card.Content>
					<form onsubmit={createTeam} class="flex gap-2">
						<Input bind:value={newTeam} placeholder="Nome del team" required />
						<Button type="submit" disabled={busy}>Crea</Button>
					</form>
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header><Card.Title>Nuovo pilota</Card.Title></Card.Header>
				<Card.Content>
					<form onsubmit={createPilot} class="flex flex-wrap gap-2">
						<Input bind:value={newPilot} placeholder="Nome del pilota" required class="flex-1" />
						<select
							class={selectClass}
							bind:value={newPilotTeam}
							aria-label="Team del nuovo pilota"
						>
							<option value="">Nessun team</option>
							{#each teams as t (t.id)}
								<option value={String(t.id)}>{t.name}</option>
							{/each}
						</select>
						<Button type="submit" disabled={busy}>Crea</Button>
					</form>
				</Card.Content>
			</Card.Root>
		</div>

		{#each groups as group (group.team.id)}
			<Card.Root>
				<Card.Header>
					<div class="flex flex-wrap items-center gap-2">
						{@render nameCell('team', group.team.id, group.team.name)}
						<Button
							size="sm"
							variant="ghost"
							class="text-destructive"
							disabled={busy}
							onclick={() => removeTeam(group.team)}
						>
							Elimina team
						</Button>
					</div>
				</Card.Header>
				<Card.Content>
					{#if group.pilots.length === 0}
						<p class="text-sm text-muted-foreground">Nessun pilota in questo team.</p>
					{:else}
						<ul class="divide-y">
							{#each group.pilots as p (p.id)}
								{@render pilotRow(p)}
							{/each}
						</ul>
					{/if}
				</Card.Content>
			</Card.Root>
		{/each}

		{#if freePilots.length > 0}
			<Card.Root>
				<Card.Header><Card.Title>Piloti senza team</Card.Title></Card.Header>
				<Card.Content>
					<ul class="divide-y">
						{#each freePilots as p (p.id)}
							{@render pilotRow(p)}
						{/each}
					</ul>
				</Card.Content>
			</Card.Root>
		{/if}

		{#if teams.length === 0 && pilots.length === 0}
			<p class="text-muted-foreground">Non hai ancora né team né piloti: creane uno qui sopra.</p>
		{/if}
	{/if}
</main>

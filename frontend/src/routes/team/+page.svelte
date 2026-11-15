<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import type { Pilot, Team } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { resolve } from '$app/paths';
	import RacingIcon from '$lib/components/shared/racing-icon.svelte';

	const selectClass =
		'h-9 rounded-lg border border-white/10 bg-[#0e121a] px-3 text-xs text-foreground focus:border-primary focus:outline-none disabled:opacity-50';

	// Piloti per richiesta: coincide con il massimo accettato dal backend.
	const PILOTS_PAGE = 100;
	// Attesa dopo l'ultimo tasto prima di cercare, per non fare una richiesta a ogni lettera.
	const SEARCH_DELAY_MS = 300;

	let teams = $state<Team[]>([]);
	let pilots = $state<Pilot[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);
	let busy = $state(false);

	let newTeam = $state('');
	let newPilot = $state('');
	let newPilotTeam = $state('');
	let search = $state('');
	let editing = $state<{ kind: 'team' | 'pilot'; id: number; name: string } | null>(null);

	let searchTimer: ReturnType<typeof setTimeout> | undefined;
	// Numera i caricamenti: una risposta vecchia non deve sovrascrivere una più recente.
	let reloadId = 0;

	let searching = $derived(search.trim() !== '');

	// Piloti raggruppati per team, e piloti senza team. Durante la ricerca i team senza
	// risultati si nascondono.
	let groups = $derived(
		teams
			.map((team) => ({ team, pilots: pilots.filter((p) => p.team_id === team.id) }))
			.filter((group) => !searching || group.pilots.length > 0)
	);
	let freePilots = $derived(pilots.filter((p) => p.team_id === null));

	// Scarica i piloti a pagine finché una pagina non è incompleta.
	async function loadPilots(query: string): Promise<Pilot[]> {
		const all: Pilot[] = [];
		for (let offset = 0; ; offset += PILOTS_PAGE) {
			let url = `/pilots?limit=${PILOTS_PAGE}&offset=${offset}`;
			if (query !== '') url += `&q=${encodeURIComponent(query)}`;
			const chunk = await api<Pilot[]>(url);
			all.push(...chunk);
			if (chunk.length < PILOTS_PAGE) return all;
		}
	}

	async function reload() {
		const id = ++reloadId;
		const [newTeams, newPilots] = await Promise.all([
			api<Team[]>('/teams'),
			loadPilots(search.trim())
		]);
		if (id !== reloadId) return;
		teams = newTeams;
		pilots = newPilots;
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

	function onSearchInput() {
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => void run(async () => {}), SEARCH_DELAY_MS);
	}

	onMount(() => {
		void run(async () => {}).then(() => (loaded = true));
		return () => clearTimeout(searchTimer);
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

<svelte:head><title>Scuderie e Piloti — Heat</title></svelte:head>

{#snippet nameCell(kind: 'team' | 'pilot', id: number, name: string)}
	{#if editing && editing.kind === kind && editing.id === id}
		<form onsubmit={saveEdit} class="flex flex-1 items-center gap-2">
			<Input
				bind:value={editing.name}
				required
				class="h-8 rounded border-white/20 bg-[#0d1017] text-white"
			/>
			<Button
				type="submit"
				size="sm"
				class="bg-primary font-racing text-xs tracking-wider text-white uppercase"
				disabled={busy}>Salva</Button
			>
			<Button
				type="button"
				size="sm"
				variant="ghost"
				class="text-xs text-muted-foreground hover:text-white"
				onclick={() => (editing = null)}
			>
				Annulla
			</Button>
		</form>
	{:else}
		<div class="flex items-center gap-2">
			<span class="text-base font-bold tracking-wide text-foreground">{name}</span>
			<Button
				size="sm"
				variant="ghost"
				class="h-7 text-xs text-muted-foreground hover:text-foreground"
				onclick={() => (editing = { kind, id, name })}
			>
				Rinomina
			</Button>
		</div>
	{/if}
{/snippet}

{#snippet pilotRow(p: Pilot)}
	<li
		class="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/5 bg-[#121622] px-4 py-3 transition-all hover:border-white/15"
	>
		<div class="flex min-w-[200px] items-center gap-3">
			<!-- Racing Roundel Number -->
			<div class="racing-roundel h-8 w-8 shrink-0 text-xs shadow-md">
				#{p.id}
			</div>

			<div class="flex flex-col">
				{@render nameCell('pilot', p.id, p.name)}
				{#if p.championship}
					<span class="mt-0.5 inline-flex items-center gap-1 text-[11px] text-amber-400">
						<RacingIcon name="trophy" size="xs" />
						{p.championship.name}
					</span>
				{/if}
			</div>
		</div>

		<!-- Telemetry badges (Gold, Sponsor, Points) -->
		<div class="flex flex-wrap items-center gap-2">
			<span
				class="inline-flex items-center gap-1 rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-xs font-bold text-amber-400"
			>
				<RacingIcon name="trophy" size="xs" />
				{p.gold} Gold
			</span>
			<span
				class="inline-flex items-center gap-1 rounded-full border border-sky-500/20 bg-sky-500/10 px-2.5 py-1 text-xs font-bold text-sky-400"
			>
				<RacingIcon name="spark_plug" size="xs" />
				{p.sponsor} Sponsor
			</span>
			<span
				class="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-xs font-bold text-emerald-400"
			>
				<RacingIcon name="flags" size="xs" />
				{p.point} Punti
			</span>
		</div>

		<!-- Action buttons & Team select -->
		<div class="flex items-center gap-2.5">
			<a
				href={resolve('/pilots/[id]', { id: String(p.id) })}
				class="inline-flex items-center gap-1.5 rounded-lg border border-primary/40 bg-primary/20 px-3 py-1.5 font-racing text-xs font-bold tracking-wider text-white uppercase shadow-sm transition-all hover:bg-primary"
			>
				<RacingIcon name="speedometer" size="xs" />
				<span>Mazzi & Carte</span>
			</a>

			<select
				class={selectClass}
				value={p.team_id === null ? '' : String(p.team_id)}
				onchange={(e) => changeTeam(p, e.currentTarget.value)}
				disabled={busy}
				aria-label="Team di {p.name}"
			>
				<option value="">Nessuna Scuderia</option>
				{#each teams as t (t.id)}
					<option value={String(t.id)}>{t.name}</option>
				{/each}
			</select>

			<Button
				size="sm"
				variant="ghost"
				class="h-8 text-xs text-destructive hover:bg-destructive/20 hover:text-white"
				disabled={busy}
				onclick={() => removePilot(p)}
			>
				Elimina
			</Button>
		</div>
	</li>
{/snippet}

<main class="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
	<!-- Page Header Banner -->
	<div class="relative mb-2 overflow-hidden rounded-2xl border border-white/10 shadow-xl">
		<!-- Actual board game photo background -->
		<div class="absolute inset-0 z-0">
			<img
				src="/images/heat-cars.jpg"
				alt="Heat miniature griglia di partenza"
				class="h-full w-full object-cover object-center opacity-20"
			/>
			<div
				class="absolute inset-0 bg-gradient-to-r from-[#10141e] via-[#10141e]/85 to-[#10141e]/50"
			></div>
		</div>
		<div
			class="relative z-10 flex flex-col justify-between gap-4 px-6 py-5 sm:flex-row sm:items-center"
		>
			<div>
				<div class="flex items-center gap-3">
					<div
						class="flex h-11 w-11 items-center justify-center rounded-xl border border-primary/30 bg-primary/20 text-primary shadow-lg"
					>
						<RacingIcon name="helmet" size="lg" />
					</div>
					<div>
						<h1
							class="font-racing text-3xl font-black tracking-wide text-white uppercase italic sm:text-4xl"
						>
							SCUDERIE E PILOTI
						</h1>
						<p class="mt-0.5 text-xs tracking-widest text-muted-foreground uppercase">
							Gestione del Garage, contratti e mazzi di partenza
						</p>
					</div>
				</div>
			</div>

			<!-- Quick Search Input -->
			<div class="w-full sm:w-72">
				<Input
					type="search"
					bind:value={search}
					oninput={onSearchInput}
					maxlength={40}
					placeholder="Cerca pilota per nome…"
					aria-label="Cerca un pilota per nome"
					class="h-10 rounded-xl border-white/10 bg-[#121622]/80 px-4 text-xs text-white backdrop-blur placeholder:text-muted-foreground/40 focus:border-primary"
				/>
			</div>
		</div>
	</div>

	{#if error}
		<div
			class="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300"
			role="alert"
		>
			<RacingIcon name="flame" size="xs" />
			<span>{error}</span>
		</div>
	{/if}

	{#if !loaded}
		<div class="flex items-center justify-center p-12 text-muted-foreground">
			<RacingIcon name="speedometer" size="lg" class="mr-3 animate-spin text-primary" />
			<span class="font-racing text-lg tracking-wider uppercase">Accesso ai box in corso…</span>
		</div>
	{:else}
		<!-- Creation Cards (Toolboxes) -->
		<div class="grid gap-6 sm:grid-cols-2">
			<!-- Create Team Card -->
			<div
				class="curb-left overflow-hidden rounded-2xl border border-white/10 bg-[#141824] p-5 shadow-xl"
			>
				<div class="mb-3 flex items-center gap-2">
					<RacingIcon name="wrenches" size="sm" class="text-primary" />
					<h3 class="font-racing text-xl font-bold tracking-wider text-white uppercase">
						Nuova Scuderia
					</h3>
				</div>
				<form onsubmit={createTeam} class="flex gap-2.5">
					<Input
						bind:value={newTeam}
						placeholder="es. Scuderia Ferrari, Lotus..."
						required
						class="h-10 rounded-lg border-white/10 bg-[#0d1017] px-3 text-xs text-white placeholder:text-muted-foreground/40 focus:border-primary"
					/>
					<Button
						type="submit"
						disabled={busy}
						class="h-10 bg-primary px-5 font-racing font-bold tracking-wider text-white uppercase hover:bg-accent"
					>
						Crea
					</Button>
				</form>
			</div>

			<!-- Create Pilot Card -->
			<div
				class="curb-left overflow-hidden rounded-2xl border border-white/10 bg-[#141824] p-5 shadow-xl"
			>
				<div class="mb-3 flex items-center gap-2">
					<RacingIcon name="helmet" size="sm" class="text-amber-400" />
					<h3 class="font-racing text-xl font-bold tracking-wider text-white uppercase">
						Nuovo Pilota
					</h3>
				</div>
				<form onsubmit={createPilot} class="flex flex-wrap gap-2.5">
					<Input
						bind:value={newPilot}
						placeholder="Nome del pilota"
						required
						class="h-10 flex-1 rounded-lg border-white/10 bg-[#0d1017] px-3 text-xs text-white placeholder:text-muted-foreground/40 focus:border-primary"
					/>
					<select
						class="{selectClass} h-10"
						bind:value={newPilotTeam}
						aria-label="Team del nuovo pilota"
					>
						<option value="">Nessuna Scuderia</option>
						{#each teams as t (t.id)}
							<option value={String(t.id)}>{t.name}</option>
						{/each}
					</select>
					<Button
						type="submit"
						disabled={busy}
						class="h-10 bg-amber-500 px-5 font-racing font-bold tracking-wider text-white uppercase hover:bg-amber-600"
					>
						Iscrivi
					</Button>
				</form>
			</div>
		</div>

		<!-- Team Groups -->
		{#each groups as group (group.team.id)}
			<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#10141e] shadow-xl">
				<div
					class="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 bg-[#151926] px-5 py-3.5"
				>
					<div class="flex items-center gap-3">
						<div
							class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/20 text-primary"
						>
							<RacingIcon name="car" size="sm" />
						</div>
						{@render nameCell('team', group.team.id, group.team.name)}
					</div>
					<Button
						size="sm"
						variant="ghost"
						class="h-8 text-xs text-destructive hover:bg-destructive/20 hover:text-white"
						disabled={busy}
						onclick={() => removeTeam(group.team)}
					>
						Elimina Scuderia
					</Button>
				</div>
				<div class="p-4 sm:p-5">
					{#if group.pilots.length === 0}
						<p class="py-4 text-center text-xs text-muted-foreground italic">
							Nessun pilota assegnato a questa scuderia.
						</p>
					{:else}
						<ul class="space-y-2.5">
							{#each group.pilots as p (p.id)}
								{@render pilotRow(p)}
							{/each}
						</ul>
					{/if}
				</div>
			</div>
		{/each}

		<!-- Free Pilots (Piloti senza team) -->
		{#if freePilots.length > 0}
			<div class="overflow-hidden rounded-2xl border border-white/10 bg-[#10141e] shadow-xl">
				<div class="flex items-center gap-2 border-b border-white/10 bg-[#151926] px-5 py-3.5">
					<RacingIcon name="flags" size="sm" class="text-amber-400" />
					<h3 class="font-racing text-xl font-bold tracking-wider text-white uppercase">
						Piloti Indipendenti / Senza Scuderia
					</h3>
				</div>
				<div class="p-4 sm:p-5">
					<ul class="space-y-2.5">
						{#each freePilots as p (p.id)}
							{@render pilotRow(p)}
						{/each}
					</ul>
				</div>
			</div>
		{/if}

		{#if searching && pilots.length === 0}
			<div
				class="rounded-2xl border border-white/10 bg-[#121622] p-10 text-center text-muted-foreground"
			>
				<RacingIcon name="speedometer" size="xl" class="mx-auto mb-2 opacity-40" />
				<p class="font-racing text-xl tracking-wider text-white uppercase">Nessun pilota trovato</p>
				<p class="mt-1 text-xs text-muted-foreground">
					Nessun pilota corrisponde alla ricerca inserita.
				</p>
			</div>
		{:else if teams.length === 0 && pilots.length === 0}
			<!-- High impact Empty State -->
			<div class="rounded-2xl border border-dashed border-white/20 bg-[#10141e] p-10 text-center">
				<div
					class="heat-glow mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/20 text-primary"
				>
					<RacingIcon name="car" size="xl" />
				</div>
				<h3 class="font-racing text-2xl font-bold tracking-wider text-white uppercase">
					La griglia di partenza è vuota
				</h3>
				<p class="mx-auto mt-2 max-w-md text-xs text-muted-foreground sm:text-sm">
					Non hai ancora registrato scuderie né piloti. Usa i moduli qui sopra per fondare il tuo
					primo team e scendere in pista!
				</p>
			</div>
		{/if}
	{/if}
</main>

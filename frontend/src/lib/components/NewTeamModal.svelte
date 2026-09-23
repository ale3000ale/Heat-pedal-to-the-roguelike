<!-- frontend/src/lib/components/NewTeamModal.svelte -->
<!-- Modale per la creazione di un nuovo team: richiede nome team + un pilota dell'utente senza team. -->
<script lang="ts">
	import { apiRequest } from '$lib/api';
	import { createEventDispatcher } from 'svelte';

	export let availablePilots: { id: number; name: string }[] = [];
	export let open = false;

	const dispatch = createEventDispatcher<{ created: void; close: void }>();

	let name = '';
	let pilotId: number | null = availablePilots[0]?.id ?? null;
	let errorMsg = '';
	let loading = false;

	// handleSubmit()
	// Nessun parametro (legge nome e pilotId dal binding del form).
	// Crea il nuovo team associando il pilota scelto; mostra errore chiaro se non ci sono piloti disponibili.
	async function handleSubmit(): Promise<void> {
		errorMsg = '';
		if (availablePilots.length === 0) {
			errorMsg = 'Non hai piloti disponibili senza team: crea prima un pilota.';
			return;
		}
		if (!pilotId) {
			errorMsg = 'Seleziona un pilota da associare al nuovo team.';
			return;
		}
		loading = true;
		try {
			await apiRequest('/teams', { method: 'POST', auth: true, body: { name, pilot_id: pilotId } });
			dispatch('created');
			name = '';
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nella creazione del team';
		} finally {
			loading = false;
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="app-card w-full max-w-md">
			<h2 class="font-display font-semibold text-lg mb-4">Nuovo team</h2>

			{#if availablePilots.length === 0}
				<p class="text-racing-red text-sm mb-4">
					Non ci sono piloti tuoi disponibili senza team. Crea un nuovo pilota prima di procedere.
				</p>
			{:else}
				<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
					<div>
						<label class="block text-sm font-medium mb-1" for="team-name">Nome team</label>
						<input id="team-name" class="input-field" bind:value={name} required />
					</div>
					<div>
						<label class="block text-sm font-medium mb-1" for="team-pilot">Pilota da associare</label>
						<select id="team-pilot" class="input-field" bind:value={pilotId}>
							{#each availablePilots as p}
								<option value={p.id}>{p.name}</option>
							{/each}
						</select>
					</div>
					{#if errorMsg}<p class="text-racing-red text-sm">{errorMsg}</p>{/if}
					<div class="flex gap-2">
						<button type="submit" class="btn-primary flex-1" disabled={loading}>
							{loading ? 'Creazione…' : 'Crea team'}
						</button>
						<button type="button" class="btn-secondary" on:click={() => dispatch('close')}>Annulla</button>
					</div>
				</form>
			{/if}

			{#if availablePilots.length === 0}
				<button type="button" class="btn-secondary mt-4 w-full" on:click={() => dispatch('close')}>
					Chiudi
				</button>
			{/if}
		</div>
	</div>
{/if}

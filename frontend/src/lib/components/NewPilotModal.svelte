<!-- frontend/src/lib/components/NewPilotModal.svelte -->
<!-- Modale per la creazione di un nuovo pilota dell'utente loggato. -->
<script lang="ts">
	import { apiRequest } from '$lib/api';
	import { createEventDispatcher } from 'svelte';

	export let open = false;

	const dispatch = createEventDispatcher<{ created: void; close: void }>();

	let name = '';
	let errorMsg = '';
	let loading = false;

	// handleSubmit()
	// Nessun parametro (legge il nome dal binding del form).
	// Crea un nuovo pilota associato all'utente loggato tramite l'API.
	async function handleSubmit(): Promise<void> {
		errorMsg = '';
		if (!name.trim()) {
			errorMsg = 'Il nome del pilota e\' obbligatorio';
			return;
		}
		loading = true;
		try {
			await apiRequest('/pilots', { method: 'POST', auth: true, body: { name } });
			dispatch('created');
			name = '';
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore nella creazione del pilota';
		} finally {
			loading = false;
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
		<div class="app-card w-full max-w-md">
			<h2 class="font-display font-semibold text-lg mb-4">Nuovo pilota</h2>
			<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
				<div>
					<label class="block text-sm font-medium mb-1" for="pilot-name">Nome pilota</label>
					<input id="pilot-name" class="input-field" bind:value={name} required />
				</div>
				{#if errorMsg}<p class="text-racing-red text-sm">{errorMsg}</p>{/if}
				<div class="flex gap-2">
					<button type="submit" class="btn-primary flex-1" disabled={loading}>
						{loading ? 'Creazione…' : 'Crea pilota'}
					</button>
					<button type="button" class="btn-secondary" on:click={() => dispatch('close')}>Annulla</button>
				</div>
			</form>
		</div>
	</div>
{/if}

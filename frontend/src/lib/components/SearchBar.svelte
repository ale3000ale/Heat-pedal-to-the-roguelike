<!-- frontend/src/lib/components/SearchBar.svelte -->
<!-- Barra di ricerca generica riutilizzabile (Piloti, Mazzo) con campi configurabili via props. -->
<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let fields: { key: string; label: string; placeholder?: string }[];
	export let values: Record<string, string> = {};

	const dispatch = createEventDispatcher<{ search: Record<string, string> }>();

	// handleSubmit()
	// Nessun parametro (legge i valori correnti dai campi bindati).
	// Notifica il componente padre con i filtri correnti, per lanciare la ricerca lato API.
	function handleSubmit(): void {
		dispatch('search', values);
	}

	// handleReset()
	// Nessun parametro.
	// Azzera tutti i filtri e notifica il padre per ricaricare l'elenco completo.
	function handleReset(): void {
		for (const f of fields) values[f.key] = '';
		dispatch('search', values);
	}
</script>

<form class="flex flex-wrap gap-3 mb-6" on:submit|preventDefault={handleSubmit}>
	{#each fields as field}
		<input
			class="input-field flex-1 min-w-[140px]"
			placeholder={field.placeholder ?? field.label}
			bind:value={values[field.key]}
		/>
	{/each}
	<button type="submit" class="btn-primary">Cerca</button>
	<button type="button" class="btn-secondary" on:click={handleReset}>Reset</button>
</form>

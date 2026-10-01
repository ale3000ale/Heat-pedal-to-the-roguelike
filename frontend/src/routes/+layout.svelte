<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { auth } from '$lib/auth.svelte';

	let { children } = $props();

	// All'apertura dell'app chiede al backend se c'è già una sessione valida.
	onMount(() => {
		auth.init();
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="min-h-screen bg-neutral-950 text-neutral-100">
	{#if !auth.ready}
		<!-- Finché non sappiamo se l'utente è loggato non mostriamo nessuna pagina -->
		<p class="p-6 text-neutral-400">Caricamento…</p>
	{:else}
		{#if auth.error}
			<!-- Compare solo se il backend non risponde -->
			<p class="bg-red-900 px-4 py-2 text-sm" role="alert">{auth.error}</p>
		{/if}
		{@render children()}
	{/if}
</div>

<!-- frontend/src/routes/+layout.svelte -->
<!-- Layout globale: applica il tema salvato, monta la Navbar e lo stile di base racing. -->
<script lang="ts">
	import '../styles/app.css';
	import Navbar from '$lib/components/Navbar.svelte';
	import { onMount } from 'svelte';
	import { themeStore, applyTheme } from '$lib/store/theme';

	// onMount: applica subito il tema corrente al caricamento della pagina
	onMount(() => {
		applyTheme($themeStore);
	});
</script>

<div class="min-h-screen flex flex-col font-body">
	<Navbar />
	<main class="flex-1 mx-auto w-full max-w-6xl px-4 py-6">
		<slot />
	</main>
	<footer class="text-center text-xs text-racing-black/60 dark:text-racing-silver/60 py-4">
		Heat &mdash; gioco da tavolo, server locale
	</footer>
</div>

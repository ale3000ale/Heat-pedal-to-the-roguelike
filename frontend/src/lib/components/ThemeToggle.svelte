<!-- frontend/src/lib/components/ThemeToggle.svelte -->
<!-- Pulsante per alternare tema chiaro/scuro dell'intera applicazione. -->
<script lang="ts">
	import { themeStore, toggleTheme } from '$lib/store/theme';
</script>

<button
	class="btn-secondary border-white/40 !px-3"
	on:click={toggleTheme}
	aria-label="Cambia tema chiaro/scuro"
>
	{#if $themeStore === 'dark'}
		☀️
	{:else}
		🌙
	{/if}
</button>

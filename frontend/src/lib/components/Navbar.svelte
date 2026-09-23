<!-- frontend/src/lib/components/Navbar.svelte -->
<!-- Barra di navigazione superiore: hamburger su mobile, barra orizzontale su desktop. -->
<script lang="ts">
	import { authStore, clearAuth } from '$lib/store/auth';
	import ThemeToggle from '$lib/components/ThemeToggle.svelte';
	import { goto } from '$app/navigation';

	let menuOpen = false;

	const links = [
		{ href: '/campionati', label: 'Campionati' },
		{ href: '/team', label: 'Team' },
		{ href: '/piloti', label: 'Piloti' },
		{ href: '/mazzo', label: 'Mazzo' },
		{ href: '/negozio', label: 'Negozio' }
	];

	// toggleMenu()
	// Nessun parametro.
	// Apre/chiude il menu hamburger su mobile.
	function toggleMenu(): void {
		menuOpen = !menuOpen;
	}

	// handleLogout()
	// Nessun parametro.
	// Rimuove la sessione utente e reindirizza alla Home, aggiornando subito la UI "senza login".
	function handleLogout(): void {
		clearAuth();
		menuOpen = false;
		goto('/');
	}
</script>

<header class="sticky top-0 z-50 bg-racing-gradient text-white shadow-md">
	<nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
		<a href="/" class="font-display text-xl font-bold tracking-wide">HEAT</a>

		<button class="md:hidden" on:click={toggleMenu} aria-label="Apri menu">
			<span class="block h-0.5 w-6 bg-white mb-1"></span>
			<span class="block h-0.5 w-6 bg-white mb-1"></span>
			<span class="block h-0.5 w-6 bg-white"></span>
		</button>

		<div class="hidden md:flex items-center gap-6 font-display">
			{#each links as link}
				<a href={link.href} class="hover:text-racing-gold transition-colors">{link.label}</a>
			{/each}

			{#if $authStore.token}
				<span class="text-sm opacity-80">{$authStore.user?.username}</span>
				<button class="btn-secondary border-white/40" on:click={handleLogout}>Logout</button>
			{:else}
				<a href="/login" class="btn-secondary border-white/40">Login</a>
			{/if}

			<ThemeToggle />
		</div>
	</nav>

	{#if menuOpen}
		<div class="md:hidden flex flex-col gap-3 px-4 pb-4 font-display">
			{#each links as link}
				<a href={link.href} on:click={() => (menuOpen = false)} class="py-1">{link.label}</a>
			{/each}

			{#if $authStore.token}
				<span class="text-sm opacity-80">{$authStore.user?.username}</span>
				<button class="btn-secondary border-white/40" on:click={handleLogout}>Logout</button>
			{:else}
				<a href="/login" on:click={() => (menuOpen = false)} class="btn-secondary border-white/40">Login</a>
			{/if}

			<ThemeToggle />
		</div>
	{/if}
</header>

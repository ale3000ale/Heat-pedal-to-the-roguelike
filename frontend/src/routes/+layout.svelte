<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import { Button } from '$lib/components/ui/button';

	let { children } = $props();

	// Pagine visibili anche senza sessione.
	const publicPaths = ['/login', '/register'];
	let isPublic = $derived(publicPaths.includes(page.url.pathname));

	// All'apertura dell'app chiede al backend se c'è già una sessione valida.
	onMount(() => {
		auth.init();
	});

	// Chi non è loggato e apre una pagina protetta va al login.
	$effect(() => {
		if (auth.ready && !auth.user && !isPublic) goto(resolve('/login'));
	});

	async function logout() {
		try {
			await auth.logout();
		} catch {
			// Lo stato locale è già svuotato: l'effetto qui sopra porta al login.
		}
	}
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="min-h-screen bg-background text-foreground">
	{#if !auth.ready}
		<!-- Finché non sappiamo se l'utente è loggato non mostriamo nessuna pagina -->
		<p class="p-6 text-muted-foreground">Caricamento…</p>
	{:else}
		{#if auth.error}
			<!-- Compare solo se il backend non risponde -->
			<p class="bg-destructive px-4 py-2 text-sm text-white" role="alert">{auth.error}</p>
		{/if}

		{#if auth.user}
			<header class="border-b">
				<nav class="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
					<div class="flex items-center gap-6">
						<a href={resolve('/')} class="text-lg font-bold tracking-tight">Heat</a>
						<a href={resolve('/team')} class="text-sm text-muted-foreground hover:text-foreground">
							Team e piloti
						</a>
						<a
							href={resolve('/championships')}
							class="text-sm text-muted-foreground hover:text-foreground"
						>
							Campionati
						</a>
					</div>
					<div class="flex items-center gap-3 text-sm">
						<span class="text-muted-foreground">
							{auth.user.username}{auth.isAdmin ? ' · admin' : ''}
						</span>
						<Button variant="outline" size="sm" onclick={logout}>Esci</Button>
					</div>
				</nav>
			</header>
		{/if}

		<!-- Le pagine protette non compaiono nemmeno per un istante senza sessione -->
		{#if auth.user || isPublic}
			{@render children()}
		{/if}
	{/if}
</div>

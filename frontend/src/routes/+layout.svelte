<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount, untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import { eventClient } from '$lib/events/event-client';
	import { Button } from '$lib/components/ui/button';
	import AccountSettings from '$lib/components/account-settings.svelte';

	let { children } = $props();
	let settingsOpen = $state(false);

	// Pagine visibili anche senza sessione.
	const publicPaths = ['/login', '/register'];
	let isPublic = $derived(publicPaths.includes(page.url.pathname));

	// Menu a tendina dell'admin: si chiude cambiando pagina o cliccando fuori.
	let adminMenuOpen = $state(false);
	let adminMenu = $state<HTMLElement | null>(null);

	// All'apertura dell'app chiede al backend se c'è già una sessione valida.
	onMount(() => {
		auth.init();
	});

	// Una connessione per il layout autenticato; cleanup su cambio utente o smontaggio.
	$effect(() => {
		const userId = auth.ready ? auth.user?.id : undefined;
		if (userId === undefined) return;
		return untrack(() =>
			eventClient.connect(userId, () => {
				if (auth.user?.id === userId) auth.user = null;
			})
		);
	});

	// Chi non è loggato e apre una pagina protetta va al login.
	$effect(() => {
		if (auth.ready && !auth.user && !isPublic) goto(resolve('/login'));
	});

	$effect(() => {
		void page.url.pathname;
		adminMenuOpen = false;
		settingsOpen = false;
	});

	$effect(() => {
		void auth.user?.id;
		settingsOpen = false;
	});

	function closeAdminMenu(event: MouseEvent) {
		if (adminMenuOpen && adminMenu && !adminMenu.contains(event.target as Node)) {
			adminMenuOpen = false;
		}
	}

	async function logout() {
		eventClient.disconnect();
		try {
			await auth.logout();
		} catch {
			// Lo stato locale è già svuotato: l'effetto qui sopra porta al login.
		}
	}
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<svelte:window onclick={closeAdminMenu} />

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
						<a href={resolve('/shop')} class="text-sm text-muted-foreground hover:text-foreground">
							Negozio
						</a>
						{#if auth.isAdmin}
							<!-- Tutti i link riservati all'admin stanno qui dentro -->
							<details class="relative" bind:open={adminMenuOpen} bind:this={adminMenu}>
								<summary
									class="cursor-pointer list-none text-sm text-muted-foreground hover:text-foreground"
								>
									Admin ▾
								</summary>
								<ul
									class="absolute left-0 z-10 mt-2 min-w-44 rounded-md border bg-background p-1 shadow-md"
								>
									<li>
										<a
											href={resolve('/admin/championships')}
											class="block rounded-sm px-3 py-1.5 text-sm hover:bg-accent"
										>
											Gestione campionati
										</a>
									</li>
									<li>
										<a
											href={resolve('/admin/pools')}
											class="block rounded-sm px-3 py-1.5 text-sm hover:bg-accent"
										>
											Pool di carte
										</a>
									</li>
									<li>
										<a
											href={resolve('/admin/shop')}
											class="block rounded-sm px-3 py-1.5 text-sm hover:bg-accent"
										>
											Gestione negozio
										</a>
									</li>
									<li>
										<a
											href={resolve('/admin/users')}
											class="block rounded-sm px-3 py-1.5 text-sm hover:bg-accent"
										>
											Utenti e ruoli
										</a>
									</li>
								</ul>
							</details>
						{/if}
					</div>
					<div class="flex items-center gap-3 text-sm">
						<button
							type="button"
							class="text-muted-foreground hover:text-foreground"
							aria-label={`Impostazioni account di ${auth.user.username}`}
							aria-haspopup="dialog"
							aria-expanded={settingsOpen}
							onclick={() => (settingsOpen = true)}
						>
							{auth.user.username}{auth.isAdmin
								? ' · admin'
								: auth.canManageRaces
									? ' · giudice'
									: ''}
						</button>
						<Button variant="outline" size="sm" onclick={logout}>Esci</Button>
					</div>
				</nav>
			</header>
			{#if settingsOpen}
				{#key auth.user.id}
					<AccountSettings bind:open={settingsOpen} userId={auth.user.id} />
				{/key}
			{/if}
		{/if}

		<!-- Le pagine protette non compaiono nemmeno per un istante senza sessione -->
		{#if auth.user || isPublic}
			{@render children()}
		{/if}
	{/if}
</div>

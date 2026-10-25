<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount, untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import { createDraftHost } from '$lib/draft-host';
	import { provideDraftHost } from '$lib/draft-host-context';
	import DraftHost from '$lib/components/draft-host.svelte';
	import { eventClient } from '$lib/events/event-client';
	import { Button } from '$lib/components/ui/button';
	import AccountSettings from '$lib/components/account-settings.svelte';
	import RacingIcon from '$lib/components/racing-icon.svelte';

	let { children } = $props();
	let settingsOpen = $state(false);
	const draftHost = provideDraftHost(createDraftHost({
		getContext: () => {
			const key = auth.sessionKey;
			const user = auth.user;
			return key && user ? { key, userId: user.id, role: user.role } : null;
		}
	}));

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
		// I click nel draft non chiudono il menu sottostante sospeso.
		if (event.target instanceof Element && event.target.closest('[data-draft-host-dialog]')) return;
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

	function isActive(path: string) {
		if (path === '/') return page.url.pathname === '/';
		return page.url.pathname.startsWith(path);
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Heat — Pedal to the Roguelike</title>
</svelte:head>
<svelte:window onclick={closeAdminMenu} />

<DraftHost host={draftHost}>
<div
	class="flex min-h-screen flex-col bg-background text-foreground selection:bg-primary selection:text-white"
>
	{#if !auth.ready}
		<!-- Loading state styled like engine warming up -->
		<div class="flex min-h-screen flex-col items-center justify-center gap-4 bg-[#0a0c12]">
			<div class="relative animate-pulse">
				<RacingIcon name="speedometer" size="2xl" class="scale-125" />
				<div class="absolute -right-2 -bottom-2 animate-bounce">
					<RacingIcon name="flame" size="lg" />
				</div>
			</div>
			<div class="text-center">
				<p class="text-heat font-racing text-2xl font-black tracking-wider uppercase">
					Riscaldamento Motori…
				</p>
				<p class="mt-1 text-xs tracking-widest text-muted-foreground uppercase">
					Caricamento telemetria e asset del circuito
				</p>
			</div>
		</div>
	{:else}
		{#if auth.error}
			<!-- Racing Alert Banner -->
			<div class="curb-bar" role="presentation"></div>
			<div
				class="flex items-center justify-center gap-2 bg-destructive/95 px-4 py-2.5 text-sm font-medium text-white shadow-lg backdrop-blur"
				role="alert"
			>
				<RacingIcon name="flame" size="sm" />
				<span>{auth.error}</span>
			</div>
		{/if}

		{#if auth.user}
			<!-- Top Grand Prix Header -->
			<header
				class="sticky top-0 z-40 border-b border-white/10 bg-[#0d1017]/95 shadow-xl backdrop-blur-md"
			>
				<nav class="mx-auto flex max-w-6xl items-center justify-between px-4 py-2.5">
					<div class="flex items-center gap-7">
						<!-- Brand Logo -->
						<a
							href={resolve('/')}
							class="group flex items-center gap-2.5 transition-transform hover:scale-105"
						>
							<div class="relative flex items-center justify-center">
								<RacingIcon
									name="flags"
									size="lg"
									class="drop-shadow-[0_2px_8px_rgba(230,57,38,0.5)] filter"
								/>
							</div>
							<div class="flex flex-col">
								<span
									class="text-heat font-racing text-2xl leading-none font-black tracking-wider italic drop-shadow-[0_2px_10px_rgba(230,57,38,0.4)]"
								>
									HEAT
								</span>
								<span
									class="text-[9px] leading-tight font-bold tracking-[0.2em] text-muted-foreground uppercase transition-colors group-hover:text-amber-400"
								>
									GRAND PRIX
								</span>
							</div>
						</a>

						<!-- Nav links with themed icons -->
						<div class="hidden items-center gap-2 md:flex">
							<a
								href={resolve('/team')}
								class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all {isActive(
									'/team'
								)
									? 'border border-primary/40 bg-primary/20 text-white shadow-sm'
									: 'text-muted-foreground hover:bg-white/5 hover:text-foreground'}"
							>
								<RacingIcon name="helmet" size="sm" />
								<span>Team e piloti</span>
							</a>

							<a
								href={resolve('/championships')}
								class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all {isActive(
									'/championships'
								)
									? 'border border-primary/40 bg-primary/20 text-white shadow-sm'
									: 'text-muted-foreground hover:bg-white/5 hover:text-foreground'}"
							>
								<RacingIcon name="trophy" size="sm" />
								<span>Campionati</span>
							</a>

							<a
								href={resolve('/shop')}
								class="flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all {isActive(
									'/shop'
								)
									? 'border border-primary/40 bg-primary/20 text-white shadow-sm'
									: 'text-muted-foreground hover:bg-white/5 hover:text-foreground'}"
							>
								<RacingIcon name="tires" size="sm" />
								<span>Negozio</span>
							</a>

							{#if auth.isAdmin}
								<!-- Admin dropdown with wrench icon -->
								<details class="relative" bind:open={adminMenuOpen} bind:this={adminMenu}>
									<summary
										class="flex cursor-pointer list-none items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all select-none {isActive(
											'/admin'
										)
											? 'border border-amber-500/40 bg-amber-500/20 text-amber-300'
											: 'text-muted-foreground hover:bg-white/5 hover:text-foreground'}"
									>
										<RacingIcon name="wrenches" size="sm" />
										<span>Admin</span>
										<span class="text-xs opacity-70">▾</span>
									</summary>
									<ul
										class="absolute left-0 z-50 mt-2 min-w-52 animate-in rounded-lg border border-white/10 bg-[#161a24] p-1.5 shadow-2xl backdrop-blur-xl fade-in slide-in-from-top-2"
									>
										<li>
											<a
												href={resolve('/admin/championships')}
												class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-primary/20 hover:text-white"
											>
												<RacingIcon name="trophy" size="sm" />
												<span>Gestione campionati</span>
											</a>
										</li>
										<li>
											<a
												href={resolve('/admin/pools')}
												class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-primary/20 hover:text-white"
											>
												<RacingIcon name="spark_plug" size="sm" />
												<span>Pool di carte</span>
											</a>
										</li>
										<li>
											<a
												href={resolve('/admin/shop')}
												class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-primary/20 hover:text-white"
											>
												<RacingIcon name="tires" size="sm" />
												<span>Gestione negozio</span>
											</a>
										</li>
										<li class="my-1 border-t border-white/5"></li>
										<li>
											<a
												href={resolve('/admin/users')}
												class="flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors hover:bg-primary/20 hover:text-white"
											>
												<RacingIcon name="helmet" size="sm" />
												<span>Utenti e ruoli</span>
											</a>
										</li>
									</ul>
								</details>
							{/if}
						</div>
					</div>

					<!-- User Driver Badge & Logout -->
					<div class="flex items-center gap-3">
						<!-- Driver pass card button -->
						<button
							type="button"
							class="flex items-center gap-2.5 rounded-full border border-white/10 bg-[#151922] px-3.5 py-1.5 text-xs transition hover:border-primary/40 hover:bg-[#1c2230]"
							aria-label={`Impostazioni account di ${auth.user.username}`}
							aria-haspopup="dialog"
							aria-expanded={settingsOpen}
							onclick={() => (settingsOpen = true)}
						>
							<div class="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20">
								<RacingIcon name="helmet" size="xs" />
							</div>
							<span class="font-bold tracking-wide text-foreground">{auth.user.username}</span>
							{#if auth.isAdmin}
								<span
									class="rounded border border-primary/30 bg-primary/20 px-1.5 py-0.5 text-[10px] font-bold tracking-wider text-primary uppercase"
								>
									Admin
								</span>
							{:else if auth.canManageRaces}
								<span
									class="rounded border border-amber-500/30 bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold tracking-wider text-amber-400 uppercase"
								>
									Giudice
								</span>
							{/if}
						</button>

						<Button
							variant="outline"
							size="sm"
							onclick={logout}
							class="h-8 border-white/10 bg-transparent text-xs transition-colors hover:border-destructive/60 hover:bg-destructive/10 hover:text-destructive"
						>
							Esci
						</Button>
					</div>
				</nav>
				<!-- Signature Track Curb Accent Line -->
				<div class="curb-bar" role="presentation"></div>
			</header>

			{#if settingsOpen}
				{#key auth.user.id}
					<AccountSettings bind:open={settingsOpen} userId={auth.user.id} />
				{/key}
			{/if}
		{/if}

		<!-- Page Content -->
		<div class="flex-1">
			{#if auth.user || isPublic}
				{@render children()}
			{/if}
		</div>

		{#if auth.user}
			<!-- Retro Racing Footer Strip -->
			<footer
				class="mt-auto border-t border-white/5 bg-[#0a0c11] py-4 text-center text-xs text-muted-foreground"
			>
				<div class="mx-auto flex max-w-5xl items-center justify-between px-4">
					<div class="flex items-center gap-2">
						<RacingIcon name="car" size="sm" />
						<span class="font-racing text-[11px] tracking-wider text-muted-foreground/80 uppercase">
							Heat — Pedal to the Roguelike
						</span>
					</div>
					<p class="text-[11px] text-muted-foreground/60">
						Gareggia senza surriscaldare il motore · 1960s Grand Prix Edition
					</p>
				</div>
			</footer>
		{/if}
	{/if}
</div>
</DraftHost>

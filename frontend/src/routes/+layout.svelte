<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount, untrack } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth/auth.svelte';
	import { createDraftHost } from '$lib/draft/host/draft-host';
	import { provideDraftHost } from '$lib/draft/host/draft-host-context';
	import DraftHost from '$lib/components/draft/draft-host.svelte';
	import { eventClient } from '$lib/events/event-client';
	import { Button } from '$lib/components/ui/button';
	import AccountSettings from '$lib/components/shared/account-settings.svelte';
	import NavDrawer from '$lib/components/shared/nav-drawer.svelte';
	import NavMenu from '$lib/components/shared/nav-menu.svelte';
	import RacingIcon from '$lib/components/shared/racing-icon.svelte';

	let { children } = $props();
	let settingsOpen = $state(false);
	const draftHost = provideDraftHost(
		createDraftHost({
			getContext: () => {
				const key = auth.sessionKey;
				const user = auth.user;
				return key && user ? { key, userId: user.id, role: user.role } : null;
			}
		})
	);

	// Pagine visibili anche senza sessione.
	const publicPaths = ['/login', '/register'];
	let isPublic = $derived(publicPaths.includes(page.url.pathname));

	// Drawer di navigazione su schermi stretti: si chiude cambiando pagina.
	let navOpen = $state(false);

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
		navOpen = false;
		settingsOpen = false;
	});

	$effect(() => {
		void auth.user?.id;
		settingsOpen = false;
	});

	async function logout() {
		eventClient.disconnect();
		try {
			await auth.logout();
		} catch {
			// Lo stato locale è già svuotato: l'effetto qui sopra porta al login.
		}
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Heat — Pedal to the Roguelike</title>
</svelte:head>

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
						<div class="flex items-center gap-3 md:gap-7">
							<!-- Hamburger: apre il drawer di navigazione su schermi stretti -->
							<button
								type="button"
								class="flex h-9 w-9 items-center justify-center rounded-md border border-white/10 bg-[#151922] text-foreground transition hover:border-primary/40 hover:bg-[#1c2230] md:hidden"
								aria-label="Apri il menu di navigazione"
								aria-expanded={navOpen}
								aria-controls="nav-drawer"
								onclick={() => (navOpen = true)}
							>
								<svg
									viewBox="0 0 24 24"
									class="h-5 w-5"
									fill="none"
									stroke="currentColor"
									stroke-width="2"
									stroke-linecap="round"
									aria-hidden="true"
								>
									<path d="M4 7h16M4 12h16M4 17h16" />
								</svg>
							</button>

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
							<div class="hidden md:block">
								<NavMenu currentPath={page.url.pathname} isAdmin={auth.isAdmin} />
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

				<!-- Drawer di navigazione per schermi stretti -->
				<NavDrawer bind:open={navOpen}>
					<NavMenu
						currentPath={page.url.pathname}
						isAdmin={auth.isAdmin}
						orientation="vertical"
						onNavigate={() => (navOpen = false)}
					/>
				</NavDrawer>

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
							<span
								class="font-racing text-[11px] tracking-wider text-muted-foreground/80 uppercase"
							>
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

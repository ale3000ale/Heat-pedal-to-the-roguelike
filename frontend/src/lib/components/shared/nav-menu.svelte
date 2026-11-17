<script lang="ts">
	import { resolve } from '$app/paths';
	import type { Pathname } from '$app/types';
	import RacingIcon from './racing-icon.svelte';

	type NavItem = {
		href: Pathname;
		label: string;
		icon: 'helmet' | 'trophy' | 'tires' | 'spark_plug';
	};

	// Unica fonte delle voci: le usano sia la barra orizzontale sia il drawer.
	const mainItems: NavItem[] = [
		{ href: '/team', label: 'Team e piloti', icon: 'helmet' },
		{ href: '/championships', label: 'Campionati', icon: 'trophy' },
		{ href: '/shop', label: 'Negozio', icon: 'tires' }
	];
	const adminItems: NavItem[] = [
		{ href: '/admin/championships', label: 'Gestione campionati', icon: 'trophy' },
		{ href: '/admin/pools', label: 'Pool di carte', icon: 'spark_plug' },
		{ href: '/admin/shop', label: 'Gestione negozio', icon: 'tires' },
		{ href: '/admin/users', label: 'Utenti e ruoli', icon: 'helmet' }
	];

	let {
		currentPath,
		isAdmin,
		orientation = 'horizontal',
		onNavigate
	}: {
		currentPath: string;
		isAdmin: boolean;
		/** Orizzontale nella barra in alto, verticale nel drawer. */
		orientation?: 'horizontal' | 'vertical';
		/** Chiamata al clic su una voce: il drawer si chiude. */
		onNavigate?: () => void;
	} = $props();

	let vertical = $derived(orientation === 'vertical');

	// Menu a tendina dell'admin: si chiude cambiando pagina o cliccando fuori.
	let adminOpen = $state(false);
	let adminMenu = $state<HTMLElement | null>(null);

	$effect(() => {
		void currentPath;
		adminOpen = false;
	});

	function closeAdminMenu(event: MouseEvent) {
		// I click nel draft non chiudono il menu sottostante sospeso.
		if (event.target instanceof Element && event.target.closest('[data-draft-host-dialog]')) return;
		if (adminOpen && adminMenu && !adminMenu.contains(event.target as Node)) adminOpen = false;
	}

	function isActive(href: string) {
		return currentPath.startsWith(href);
	}

	function itemClass(href: string) {
		const base = vertical
			? 'flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-all'
			: 'flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all';
		const active = 'border border-primary/40 bg-primary/20 text-white shadow-sm';
		const idle = 'text-muted-foreground hover:bg-white/5 hover:text-foreground';
		return `${base} ${isActive(href) ? active : idle}`;
	}

	function adminSummaryClass() {
		const base =
			'flex cursor-pointer list-none items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all select-none';
		const active = 'border border-amber-500/40 bg-amber-500/20 text-amber-300';
		const idle = 'text-muted-foreground hover:bg-white/5 hover:text-foreground';
		return `${base} ${isActive('/admin') ? active : idle}`;
	}

	function adminLinkClass(href: string) {
		return `flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
			isActive(href) ? 'bg-primary/20 text-white' : 'hover:bg-primary/20 hover:text-white'
		}`;
	}
</script>

<svelte:window onclick={closeAdminMenu} />

<div class={vertical ? 'flex flex-col gap-1' : 'flex items-center gap-2'}>
	<ul class={vertical ? 'flex flex-col gap-1' : 'flex items-center gap-2'}>
		{#each mainItems as item (item.href)}
			<li class:contents={!vertical}>
				<a
					href={resolve(item.href)}
					class={itemClass(item.href)}
					aria-current={isActive(item.href) ? 'page' : undefined}
					onclick={() => onNavigate?.()}
				>
					<RacingIcon name={item.icon} size="sm" />
					<span>{item.label}</span>
				</a>
			</li>
		{/each}
	</ul>

	{#if isAdmin}
		{#if vertical}
			<div class="mt-3">
				<p class="mb-1 px-3 font-racing text-[11px] tracking-wider text-amber-400/80 uppercase">
					Admin
				</p>
				<ul class="flex flex-col gap-1">
					{#each adminItems as item (item.href)}
						<li>
							<a
								href={resolve(item.href)}
								class={adminLinkClass(item.href)}
								aria-current={isActive(item.href) ? 'page' : undefined}
								onclick={() => onNavigate?.()}
							>
								<RacingIcon name={item.icon} size="sm" />
								<span>{item.label}</span>
							</a>
						</li>
					{/each}
				</ul>
			</div>
		{:else}
			<details class="relative" bind:open={adminOpen} bind:this={adminMenu}>
				<summary class={adminSummaryClass()}>
					<RacingIcon name="wrenches" size="sm" />
					<span>Admin</span>
					<span class="text-xs opacity-70">▾</span>
				</summary>
				<ul
					class="absolute left-0 z-50 mt-2 min-w-52 animate-in rounded-lg border border-white/10 bg-[#161a24] p-1.5 shadow-2xl backdrop-blur-xl fade-in slide-in-from-top-2"
				>
					{#each adminItems as item (item.href)}
						<li>
							<a
								href={resolve(item.href)}
								class={adminLinkClass(item.href)}
								aria-current={isActive(item.href) ? 'page' : undefined}
								onclick={() => onNavigate?.()}
							>
								<RacingIcon name={item.icon} size="sm" />
								<span>{item.label}</span>
							</a>
						</li>
					{/each}
				</ul>
			</details>
		{/if}
	{/if}
</div>

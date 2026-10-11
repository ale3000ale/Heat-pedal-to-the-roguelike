<script lang="ts">
	import { auth } from '$lib/auth.svelte';
	import PackTemplatesPanel from '$lib/components/pack-templates-panel.svelte';
	import ShopTemplatesPanel from '$lib/components/shop-templates-panel.svelte';
	import { Button } from '$lib/components/ui/button';

	type Tab = 'packs' | 'shops';

	let tab = $state<Tab>('packs');
</script>

<svelte:head><title>Gestione negozio - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<h1 class="text-2xl font-bold">Gestione negozio</h1>

	{#if !auth.isAdmin}
		<p class="text-sm text-destructive" role="alert">Pagina riservata agli admin.</p>
	{:else}
		<div class="flex gap-2" role="group" aria-label="Sezione">
			<Button
				size="sm"
				variant={tab === 'packs' ? 'default' : 'outline'}
				aria-pressed={tab === 'packs'}
				onclick={() => (tab = 'packs')}
			>
				Template di pacchetto
			</Button>
			<Button
				size="sm"
				variant={tab === 'shops' ? 'default' : 'outline'}
				aria-pressed={tab === 'shops'}
				onclick={() => (tab = 'shops')}
			>
				Template di negozio
			</Button>
		</div>

		{#if tab === 'packs'}
			<PackTemplatesPanel />
		{:else}
			<ShopTemplatesPanel />
		{/if}
	{/if}
</main>

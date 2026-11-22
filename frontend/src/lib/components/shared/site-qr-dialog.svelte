<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { ApiError } from '$lib/api';
	import { fetchSiteQr, isLocalOnlyUrl, type SiteQr } from '$lib/site/site-qr';
	import Modal from '$lib/components/shared/modal.svelte';
	import { Button } from '$lib/components/ui/button';

	let { open = $bindable(false) }: { open?: boolean } = $props();

	let data = $state<SiteQr | null>(null);
	let error = $state<string | null>(null);
	let loading = $state(true);
	let active = true;

	async function load() {
		loading = true;
		error = null;
		try {
			const result = await fetchSiteQr();
			if (active) data = result;
		} catch (cause) {
			if (!active) return;
			error = cause instanceof ApiError ? cause.message : 'QR non disponibile';
		} finally {
			if (active) loading = false;
		}
	}

	onMount(() => {
		void load();
	});

	// Ignora risposte tardive dopo la chiusura del popup.
	onDestroy(() => {
		active = false;
	});
</script>

<Modal {open} title="QR di accesso" fitContent>
	<div class="space-y-4">
		{#if loading}
			<p class="text-sm text-muted-foreground" role="status">Generazione del QR…</p>
		{:else if error}
			<div class="space-y-3">
				<p class="text-sm text-destructive" role="alert">{error}</p>
				<Button variant="outline" onclick={() => void load()}>Riprova</Button>
			</div>
		{:else if data}
			<div class="flex flex-col items-center gap-3">
				<img
					src={data.image}
					alt="QR code con l'indirizzo del sito"
					class="h-56 w-56 rounded-md bg-white p-2"
				/>
				<p class="text-center text-sm text-muted-foreground">
					Inquadra il QR con il telefono, collegato alla stessa rete Wi-Fi/LAN.
				</p>
				<p class="font-mono text-sm break-all text-foreground">{data.url}</p>
			</div>
			{#if isLocalOnlyUrl(data.url)}
				<div
					class="rounded-md border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-200"
					role="alert"
				>
					Questo indirizzo funziona solo da questo PC. Per aprire Heat dal telefono avvia
					<code class="font-mono">python heat.py production</code> e usa il QR mostrato nel terminale.
				</div>
			{/if}
		{/if}
		<div class="flex justify-end">
			<Button variant="outline" onclick={() => (open = false)}>Chiudi</Button>
		</div>
	</div>
</Modal>

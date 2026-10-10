<script lang="ts">
	import { api } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipHistoryPanel from '$lib/components/championship-history-panel.svelte';
	import ChampionshipPacksManager from '$lib/components/championship-packs-manager.svelte';
	import ChampionshipPoolPanel from '$lib/components/championship-pool-panel.svelte';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import GoldRulesForm from '$lib/components/gold-rules-form.svelte';
	import Modal from '$lib/components/modal.svelte';
	import SettingsDialog from '$lib/components/settings-dialog.svelte';
	import type { Championship } from '$lib/types';

	// Con `shopOnly` il popup mostra solo le impostazioni del negozio (pacchetti, pool
	// completa, storico), senza oro per gara né chiusura o eliminazione del campionato.
	let {
		championship,
		open = $bindable(false),
		shopOnly = false,
		onclosed,
		ondeleted,
		onshopchanged
	}: {
		championship: { id: number; name: string; is_closed: boolean } | null;
		open?: boolean;
		shopOnly?: boolean;
		onclosed?: (updated: Championship) => void | Promise<void>;
		ondeleted?: () => void | Promise<void>;
		onshopchanged?: () => void | Promise<void>;
	} = $props();

	let busy = $state(false);
	let error = $state<string | null>(null);
	let confirmClose = $state(false);
	let confirmDelete = $state(false);
	let packsOpen = $state(false);
	let historyOpen = $state(false);
	let poolOpen = $state(false);

	$effect(() => {
		if (open) error = null;
	});

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	// I popup del negozio si aprono al posto delle impostazioni, non sopra di esse.
	function openPacks() {
		open = false;
		packsOpen = true;
	}

	function openHistory() {
		open = false;
		historyOpen = true;
	}

	function openPool() {
		open = false;
		poolOpen = true;
	}

	async function closeChampionship() {
		if (!championship) return;
		error = null;
		busy = true;
		try {
			const updated = await api<Championship>(`/championships/${championship.id}/close`, {
				method: 'POST'
			});
			await onclosed?.(updated);
		} catch (e) {
			error = message(e);
		} finally {
			busy = false;
		}
	}

	async function deleteChampionship() {
		if (!championship) return;
		error = null;
		busy = true;
		try {
			await api(`/championships/${championship.id}`, { method: 'DELETE' });
			open = false;
			await ondeleted?.();
		} catch (e) {
			error = message(e);
		} finally {
			busy = false;
		}
	}
</script>

<SettingsDialog
	bind:open
	title={shopOnly ? 'Impostazioni del negozio' : 'Impostazioni del campionato'}
>
	{#if championship}
		<div class="space-y-4">
			<p class="text-sm text-muted-foreground">{championship.name}</p>

			{#if !shopOnly && !championship.is_closed}
				<GoldRulesForm
					url={`/championships/${championship.id}/gold-rules`}
					title="Oro per gara"
					description="Oro dato a tutti gli iscritti dopo ogni gara, anche a chi non corre. Un totale negativo diventa 0. Le modifiche valgono dalla gara successiva."
					editable
				/>
			{/if}

			<div class={shopOnly ? 'space-y-2' : 'space-y-2 border-t pt-4'}>
				<h3 class="text-sm font-semibold">Negozio</h3>
				<div class="flex flex-wrap gap-2">
					<Button size="sm" variant="outline" onclick={openPacks}>Pacchetti</Button>
					<Button size="sm" variant="outline" onclick={openPool}>Pool completa</Button>
					<Button size="sm" variant="outline" onclick={openHistory}>Storico</Button>
				</div>
			</div>

			{#if !shopOnly}
				<div class="space-y-2 border-t pt-4">
					{#if error}
						<p class="text-sm text-destructive" role="alert">{error}</p>
					{/if}
					{#if championship.is_closed}
						<Button variant="destructive" disabled={busy} onclick={() => (confirmDelete = true)}>
							Elimina campionato
						</Button>
					{:else}
						<Button variant="destructive" disabled={busy} onclick={() => (confirmClose = true)}>
							Chiudi campionato
						</Button>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</SettingsDialog>

{#if championship}
	<ConfirmDialog
		bind:open={confirmClose}
		title="Chiudere il campionato?"
		message={`Il campionato "${championship.name}" diventa di sola lettura e i piloti iscritti vengono reimpostati.`}
		confirmLabel="Chiudi campionato"
		onconfirm={closeChampionship}
	/>
	<ConfirmDialog
		bind:open={confirmDelete}
		title="Eliminare il campionato?"
		message={`Il campionato "${championship.name}" viene cancellato con tutto lo storico. L'azione non si può annullare.`}
		confirmLabel="Elimina campionato"
		onconfirm={deleteChampionship}
	/>
	<Modal bind:open={packsOpen} title="Pacchetti del negozio">
		{#if packsOpen}
			<ChampionshipPacksManager
				championshipId={championship.id}
				closed={championship.is_closed}
				onchange={onshopchanged}
			/>
		{/if}
	</Modal>
	<Modal bind:open={poolOpen} title="Pool completa del campionato">
		{#if poolOpen}
			<ChampionshipPoolPanel championshipId={championship.id} />
		{/if}
	</Modal>
	<Modal bind:open={historyOpen} title="Storico acquisti del campionato">
		{#if historyOpen}
			<ChampionshipHistoryPanel championshipId={championship.id} />
		{/if}
	</Modal>
{/if}

<script lang="ts">
	import { api } from '$lib/api';
	import { Button } from '$lib/components/ui/button';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import GoldRulesForm from '$lib/components/gold-rules-form.svelte';
	import SettingsDialog from '$lib/components/settings-dialog.svelte';
	import type { Championship } from '$lib/types';

	let {
		championship,
		open = $bindable(false),
		onclosed,
		ondeleted
	}: {
		championship: { id: number; name: string; is_closed: boolean } | null;
		open?: boolean;
		onclosed?: (updated: Championship) => void | Promise<void>;
		ondeleted?: () => void | Promise<void>;
	} = $props();

	let busy = $state(false);
	let error = $state<string | null>(null);
	let confirmClose = $state(false);
	let confirmDelete = $state(false);

	$effect(() => {
		if (open) error = null;
	});

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
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

<SettingsDialog bind:open title="Impostazioni del campionato">
	{#if championship}
		<div class="space-y-4">
			<p class="text-sm text-muted-foreground">{championship.name}</p>

			{#if !championship.is_closed}
				<GoldRulesForm
					url={`/championships/${championship.id}/gold-rules`}
					title="Oro per gara"
					description="Oro dato a tutti gli iscritti dopo ogni gara, anche a chi non corre. Un totale negativo diventa 0. Le modifiche valgono dalla gara successiva."
					editable
				/>
			{/if}

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
{/if}

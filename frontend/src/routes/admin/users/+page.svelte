<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { AdminUser } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';

	const roleLabels: Record<AdminUser['role'], string> = {
		admin: 'Admin',
		judge: 'Giudice',
		player: 'Giocatore'
	};

	let users = $state<AdminUser[]>([]);
	let error = $state<string | null>(null);
	let actionError = $state<string | null>(null);
	let busyId = $state<number | null>(null);
	let loaded = $state(false);

	onMount(async () => {
		if (!auth.isAdmin) {
			loaded = true;
			return;
		}
		try {
			users = await api<AdminUser[]>('/admin/users');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			loaded = true;
		}
	});

	// Il giudice diventa giocatore e viceversa; l'admin non si può cambiare.
	async function toggleJudge(user: AdminUser) {
		actionError = null;
		busyId = user.id;
		try {
			const updated = await api<AdminUser>(`/admin/users/${user.id}/role`, {
				method: 'PUT',
				body: { role: user.role === 'judge' ? 'player' : 'judge' }
			});
			users = users.map((u) => (u.id === updated.id ? updated : u));
		} catch (e) {
			actionError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busyId = null;
		}
	}
</script>

<svelte:head><title>Utenti - Heat</title></svelte:head>

<main class="mx-auto max-w-5xl space-y-6 p-6">
	<a href={resolve('/')} class="text-sm text-muted-foreground hover:text-foreground">
		← Home
	</a>

	<h1 class="text-2xl font-bold">Utenti e ruoli</h1>

	{#if !loaded}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if !auth.isAdmin}
		<p class="text-sm text-destructive" role="alert">Questa pagina è riservata all'admin.</p>
	{:else if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{:else}
		<Card.Root>
			<Card.Header>
				<Card.Title>Giudici</Card.Title>
				<Card.Description>
					Il giudice può creare le gare e chiuderle con i risultati; solo l'admin può correggerle.
				</Card.Description>
			</Card.Header>
			<Card.Content>
				<ul class="divide-y">
					{#each users as user (user.id)}
						<li class="flex items-center gap-3 py-2">
							<span class="flex-1 font-medium">{user.username}</span>
							<span class="text-sm text-muted-foreground">{roleLabels[user.role]}</span>
							{#if user.role !== 'admin'}
								<Button
									size="sm"
									variant="outline"
									disabled={busyId === user.id}
									onclick={() => toggleJudge(user)}
								>
									{user.role === 'judge' ? 'Togli giudice' : 'Rendi giudice'}
								</Button>
							{/if}
						</li>
					{/each}
				</ul>
				{#if actionError}
					<p class="mt-3 text-sm text-destructive" role="alert">{actionError}</p>
				{/if}
			</Card.Content>
		</Card.Root>
	{/if}
</main>

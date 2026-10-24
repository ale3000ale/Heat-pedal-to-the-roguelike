<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { auth } from '$lib/auth.svelte';
	import { ApiError } from '$lib/api';
	import { changePassword } from '$lib/password-change-api';
	import { passwordChangeError, validatePasswordChange } from '$lib/password-change';
	import Modal from '$lib/components/modal.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';

	let { open = $bindable(false), userId }: { open?: boolean; userId: number } = $props();
	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmation = $state('');
	let pending = $state(false);
	let error = $state<string | null>(null);
	let success = $state(false);
	let active = true;
	let returnFocus: HTMLElement | null = null;

	onMount(() => {
		returnFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
	});

	/** Drop local secrets and ignore responses after this modal has been unmounted. */
	onDestroy(() => {
		active = false;
		clearPasswords();
		if (auth.user?.id === userId && returnFocus?.isConnected) returnFocus.focus();
	});

	function clearPasswords() {
		currentPassword = '';
		newPassword = '';
		confirmation = '';
	}

	/** Close only outside a request; shared Modal delegates X, Escape and outside clicks here. */
	function close() {
		if (pending) return;
		clearPasswords();
		open = false;
	}

	/** Submit once for the same account; an uncertain response never triggers an automatic retry. */
	async function submit(event: SubmitEvent) {
		event.preventDefault();
		if (pending || auth.user?.id !== userId) return;
		const data = {
			current_password: currentPassword,
			new_password: newPassword,
			confirm_password: confirmation
		};
		error = validatePasswordChange(data);
		success = false;
		if (error) return;
		pending = true;
		try {
			await changePassword(data);
			if (active && auth.user?.id === userId) success = true;
		} catch (cause) {
			if (!active || auth.user?.id !== userId) return;
			error = passwordChangeError(cause);
			if (cause instanceof ApiError && cause.status === 401) auth.user = null;
		} finally {
			data.current_password = '';
			data.new_password = '';
			data.confirm_password = '';
			clearPasswords();
			if (active) pending = false;
		}
	}
</script>

<Modal {open} title="Impostazioni account" onrequestclose={close}>
	<form class="space-y-4" onsubmit={submit} aria-busy={pending}>
		<h3 class="font-semibold">Cambio password</h3>
		<p class="text-sm text-muted-foreground">
			Resterai connesso in questa sessione. Le altre sessioni del tuo account verranno disconnesse.
		</p>
		<div class="space-y-2">
			<label for="account-current-password" class="text-sm font-medium">Password attuale</label>
			<Input
				id="account-current-password"
				type="password"
				autocomplete="current-password"
				bind:value={currentPassword}
				disabled={pending}
				required
			/>
		</div>
		<div class="space-y-2">
			<label for="account-new-password" class="text-sm font-medium">Nuova password</label>
			<Input
				id="account-new-password"
				type="password"
				autocomplete="new-password"
				bind:value={newPassword}
				disabled={pending}
				aria-describedby="account-password-help"
				required
			/>
			<p id="account-password-help" class="text-sm text-muted-foreground">Da 8 a 128 caratteri.</p>
		</div>
		<div class="space-y-2">
			<label for="account-confirm-password" class="text-sm font-medium">Conferma nuova password</label>
			<Input
				id="account-confirm-password"
				type="password"
				autocomplete="new-password"
				bind:value={confirmation}
				disabled={pending}
				required
			/>
		</div>
		{#if error}
			<p class="text-sm text-destructive" role="alert">{error}</p>
		{/if}
		{#if success}
			<p class="text-sm" role="status">
				Password aggiornata. Sei ancora connesso; le altre sessioni sono state revocate.
			</p>
		{/if}
		<div class="flex justify-end gap-2">
			<Button type="button" variant="outline" disabled={pending} onclick={close}>Chiudi</Button>
			<Button type="submit" disabled={pending}>
				{pending ? 'Aggiornamento…' : 'Cambia password'}
			</Button>
		</div>
	</form>
</Modal>

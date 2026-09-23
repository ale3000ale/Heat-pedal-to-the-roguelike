<!-- frontend/src/lib/components/RegisterForm.svelte -->
<!-- Form di registrazione: username + password (min 8 caratteri), senza email. -->
<script lang="ts">
	import { apiRequest } from '$lib/api';

	let username = '';
	let password = '';
	let errorMsg = '';
	let successMsg = '';
	let loading = false;

	// handleSubmit()
	// Nessun parametro (legge username/password dal binding del form).
	// Registra un nuovo utente; la validazione della password (min 8 caratteri) e' fatta anche
	// lato backend, qui si controlla solo per dare feedback immediato all'utente.
	async function handleSubmit(): Promise<void> {
		errorMsg = '';
		successMsg = '';
		if (password.length < 8) {
			errorMsg = 'La password deve contenere almeno 8 caratteri';
			return;
		}
		loading = true;
		try {
			await apiRequest('/auth/register', { method: 'POST', body: { username, password } });
			successMsg = 'Registrazione completata! Ora puoi effettuare il login.';
			username = '';
			password = '';
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore di registrazione';
		} finally {
			loading = false;
		}
	}
</script>

<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
	<div>
		<label class="block text-sm font-medium mb-1" for="reg-username">Username</label>
		<input id="reg-username" class="input-field" bind:value={username} required />
	</div>
	<div>
		<label class="block text-sm font-medium mb-1" for="reg-password">Password (min 8 caratteri)</label>
		<input id="reg-password" type="password" class="input-field" bind:value={password} required minlength={8} />
	</div>

	{#if errorMsg}<p class="text-racing-red text-sm">{errorMsg}</p>{/if}
	{#if successMsg}<p class="text-green-600 text-sm">{successMsg}</p>{/if}

	<button type="submit" class="btn-primary w-full" disabled={loading}>
		{loading ? 'Registrazione in corso…' : 'Registrati'}
	</button>
</form>

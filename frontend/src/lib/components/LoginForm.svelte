<!-- frontend/src/lib/components/LoginForm.svelte -->
<!-- Form di login: username + password, ottiene un JWT e aggiorna lo store di autenticazione. -->
<script lang="ts">
	import { apiRequest } from '$lib/api';
	import { setAuth } from '$lib/store/auth';
	import { goto } from '$app/navigation';

	let username = '';
	let password = '';
	let errorMsg = '';
	let loading = false;

	interface TokenResponse {
		access_token: string;
		role: 'user' | 'admin';
		username: string;
	}

	// handleSubmit()
	// Nessun parametro (legge username/password dal binding del form).
	// Invia le credenziali al backend; se valide salva il JWT e reindirizza alla Home.
	async function handleSubmit(): Promise<void> {
		errorMsg = '';
		loading = true;
		try {
			const res = await apiRequest<TokenResponse>('/auth/login', {
				method: 'POST',
				body: { username, password }
			});
			// Passaggio critico: il token viene salvato subito, cosi' tutte le pagine "con login" si aggiornano
			setAuth(res.access_token, { username: res.username, role: res.role });
			goto('/');
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Errore di login';
		} finally {
			loading = false;
		}
	}
</script>

<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
	<div>
		<label class="block text-sm font-medium mb-1" for="login-username">Username</label>
		<input id="login-username" class="input-field" bind:value={username} required />
	</div>
	<div>
		<label class="block text-sm font-medium mb-1" for="login-password">Password</label>
		<input id="login-password" type="password" class="input-field" bind:value={password} required />
	</div>

	{#if errorMsg}<p class="text-racing-red text-sm">{errorMsg}</p>{/if}

	<button type="submit" class="btn-primary w-full" disabled={loading}>
		{loading ? 'Accesso in corso…' : 'Accedi'}
	</button>
</form>

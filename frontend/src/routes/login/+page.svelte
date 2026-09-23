<!-- frontend/src/routes/login/+page.svelte -->
<!-- Pagina Login/Registrazione: due form affiancati (o impilati su mobile). -->
<script lang="ts">
	import LoginForm from '$lib/components/LoginForm.svelte';
	import RegisterForm from '$lib/components/RegisterForm.svelte';
</script>

<svelte:head><title>Heat - Login</title></svelte:head>

<h1 class="font-display text-2xl font-bold mb-6">Accedi o registrati</h1>

<div class="grid gap-6 sm:grid-cols-2">
	<div class="app-card">
		<h2 class="font-display font-semibold text-lg mb-4">Login</h2>
		<LoginForm />
	</div>
	<div class="app-card">
		<h2 class="font-display font-semibold text-lg mb-4">Registrazione</h2>
		<RegisterForm />
	</div>
</div>

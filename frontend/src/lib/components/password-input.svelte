<script lang="ts">
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';

	let {
		id,
		label,
		value = $bindable(''),
		autocomplete = 'current-password',
		disabled = false,
		required = false,
		describedBy
	}: {
		id: string;
		label: string;
		value?: string;
		autocomplete?: 'current-password' | 'new-password';
		disabled?: boolean;
		required?: boolean;
		describedBy?: string;
	} = $props();

	let visible = $state(false);

	// Each field owns its visibility; clearing or submitting hides it again.
	$effect(() => {
		if (!value || disabled) visible = false;
	});
</script>

<div class="flex items-center gap-2">
	<Input
		{id}
		type={visible ? 'text' : 'password'}
		bind:value
		{autocomplete}
		{disabled}
		{required}
		aria-describedby={describedBy}
		class="min-w-0 flex-1"
	/>
	<Button
		type="button"
		variant="outline"
		{disabled}
		aria-label={`${visible ? 'Nascondi' : 'Mostra'} ${label}`}
		aria-controls={id}
		aria-pressed={visible}
		onclick={() => {
			if (!disabled) visible = !visible;
		}}
	>
		{visible ? 'Nascondi' : 'Mostra'}
	</Button>
</div>

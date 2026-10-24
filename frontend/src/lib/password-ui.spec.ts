import { describe, expect, it } from 'vitest';
import { render } from 'svelte/server';
import PasswordInput from './components/password-input.svelte';
import AccountSettings from './components/account-settings.svelte';

// Server rendering assertions: these are not browser click or keyboard tests.

describe('password UI initial rendering', () => {
	it('starts hidden with an accessible toggle that cannot submit the form', () => {
		const { body } = render(PasswordInput, {
			props: { id: 'test-password', label: 'password attuale', value: 'example-only' }
		});
		expect(body).toContain('type="password"');
		expect(body).toContain('type="button"');
		expect(body).toContain('aria-controls="test-password"');
		expect(body).toContain('aria-pressed="false"');
		expect(body).toContain('Mostra password attuale');
	});

	it('preserves new-password autocomplete, required and the help reference', () => {
		const { body } = render(PasswordInput, {
			props: {
				id: 'test-new-password',
				label: 'nuova password',
				autocomplete: 'new-password',
				required: true,
				describedBy: 'password-help'
			}
		});
		expect(body).toContain('autocomplete="new-password"');
		expect(body).toContain('aria-describedby="password-help"');
		expect(body).toContain('required');
	});

	it('renders a disabled toggle while a request is pending', () => {
		const { body } = render(PasswordInput, {
			props: { id: 'disabled-password', label: 'password', disabled: true }
		});
		expect(body).toMatch(/<button[^>]*disabled/);
		expect(body).toContain('type="password"');
	});

	it('opens account settings with the password section collapsed and no password fields', () => {
		const { body } = render(AccountSettings, { props: { open: true, userId: 1 } });
		expect(body).toContain('Impostazioni account');
		expect(body).toContain('Cambio password');
		expect(body).toContain('aria-expanded="false"');
		expect(body).toContain('aria-controls="account-password-section"');
		expect(body).toMatch(/id="account-password-section"[^>]*hidden/);
		expect(body).not.toContain('id="account-current-password"');
	});
});

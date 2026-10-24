import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import { changePassword } from './password-change-api';
import { passwordChangeError, validatePasswordChange, type PasswordChange } from './password-change';

const valid: PasswordChange = {
	current_password: 'old-password',
	new_password: 'new-password',
	confirm_password: 'new-password'
};

afterEach(() => vi.unstubAllGlobals());

describe('password change', () => {
	it('accepts matching passwords without trimming spaces', () => {
		expect(validatePasswordChange(valid)).toBeNull();
		expect(
			validatePasswordChange({ ...valid, new_password: ' new-password ', confirm_password: ' new-password ' })
		).toBeNull();
		expect(validatePasswordChange({ ...valid, confirm_password: 'new-password ' })).not.toBeNull();
	});

	it('enforces current password, confirmation and backend length limits', () => {
		for (const data of [
			{ ...valid, current_password: '' },
			{ ...valid, current_password: 'x'.repeat(129) },
			{ ...valid, new_password: 'short', confirm_password: 'short' },
			{ ...valid, new_password: 'x'.repeat(129), confirm_password: 'x'.repeat(129) },
			{ ...valid, confirm_password: '' }
		]) expect(validatePasswordChange(data)).not.toBeNull();
	});

	it('counts Unicode code points rather than UTF-16 units', () => {
		const password = '🔐'.repeat(8);
		expect(validatePasswordChange({ ...valid, new_password: password, confirm_password: password })).toBeNull();
		const tooShort = '🔐'.repeat(4);
		expect(validatePasswordChange({ ...valid, new_password: tooShort, confirm_password: tooShort })).not.toBeNull();
	});

	it('sends only the three approved fields with the current cookie', async () => {
		const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
		vi.stubGlobal('fetch', fetch);
		await changePassword(valid);
		expect(fetch).toHaveBeenCalledTimes(1);
		const [path, options] = fetch.mock.calls[0];
		expect(path).toBe('/api/auth/change-password');
		expect(options.method).toBe('POST');
		expect(options.credentials).toBe('same-origin');
		expect(JSON.parse(options.body)).toEqual(valid);
	});

	it('does not send mismatched confirmation', async () => {
		const fetch = vi.fn();
		vi.stubGlobal('fetch', fetch);
		await expect(changePassword({ ...valid, confirm_password: 'different' })).rejects.toThrow();
		expect(fetch).not.toHaveBeenCalled();
	});

	it('does not retry network failures or assume rollback', async () => {
		const fetch = vi.fn().mockRejectedValue(new TypeError('network'));
		vi.stubGlobal('fetch', fetch);
		await expect(changePassword(valid)).rejects.toBeInstanceOf(ApiError);
		expect(fetch).toHaveBeenCalledTimes(1);
		expect(passwordChangeError(new ApiError(0, valid.new_password))).toContain('Esito non confermato');
	});

	it('uses safe messages for API errors without echoing secrets', () => {
		for (const code of [0, 401, 403, 409, 422, 500]) {
			expect(passwordChangeError(new ApiError(code, valid.new_password))).not.toContain(valid.new_password);
		}
		expect(passwordChangeError(new ApiError(403, 'ignored'))).toBe('Password attuale non corretta.');
	});
});

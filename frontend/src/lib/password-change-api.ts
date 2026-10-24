import { api } from './api';
import { validatePasswordChange, type PasswordChange } from './password-change';

/** Submit one validated change with the current session; no automatic retries. */
export async function changePassword(data: PasswordChange): Promise<void> {
	const error = validatePasswordChange(data);
	if (error) throw new Error(error);
	await api('/auth/change-password', {
		method: 'POST',
		body: {
			current_password: data.current_password,
			new_password: data.new_password,
			confirm_password: data.confirm_password
		}
	});
}

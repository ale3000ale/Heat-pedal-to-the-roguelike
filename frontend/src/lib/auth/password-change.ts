import { ApiError } from '../api';

export type PasswordChange = {
	current_password: string;
	new_password: string;
	confirm_password: string;
};

/** Validate without trimming secrets; count Unicode code points like the backend. */
export function validatePasswordChange(data: PasswordChange): string | null {
	const currentLength = Array.from(data.current_password).length;
	const newLength = Array.from(data.new_password).length;
	if (currentLength < 1 || currentLength > 128) {
		return 'Inserisci la password attuale (massimo 128 caratteri).';
	}
	if (newLength < 8 || newLength > 128) {
		return 'La nuova password deve contenere da 8 a 128 caratteri.';
	}
	if (data.new_password !== data.confirm_password) {
		return 'La conferma della nuova password non coincide.';
	}
	return null;
}

/** Return a safe user message without echoing arbitrary response bodies or secrets. */
export function passwordChangeError(error: unknown): string {
	if (error instanceof ApiError) {
		if (error.status === 401) return 'Sessione scaduta. Accedi nuovamente.';
		if (error.status === 403) return 'Password attuale non corretta.';
		if (error.status === 409) return 'Database occupato. Riprova manualmente.';
		if (error.status === 422) return 'Controlla la nuova password e la sua conferma.';
	}
	return 'Esito non confermato. La password potrebbe essere stata aggiornata: verifica prima di riprovare. Nessun nuovo invio automatico.';
}

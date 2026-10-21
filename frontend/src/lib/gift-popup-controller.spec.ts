import { describe, expect, it, vi } from 'vitest';
import { createGiftPopupController } from './gift-popup-controller';
import type { PilotGiftNotification } from './gift-notifications-api';

function notification(id: number, pilotId = 1): PilotGiftNotification {
	return {
		pilotId,
		gift: {
			id,
			race_id: 7,
			card_name: 'Sponsor',
			card_path: 'cards/sponsor.webp',
			created_at: '2026-10-20T21:00:00'
		}
	};
}

function setup() {
	const acknowledge = vi.fn<(shown: readonly PilotGiftNotification[]) => Promise<void>>();
	acknowledge.mockResolvedValue(undefined);
	const onChange = vi.fn<(visible: readonly PilotGiftNotification[]) => void>();
	const onError = vi.fn<(error: unknown) => void>();
	const controller = createGiftPopupController({ acknowledge, onChange, onError });
	return { controller, acknowledge, onChange, onError };
}

describe('gift popup controller', () => {
	it('accoda nuovi regali senza confermarli con il popup precedente', async () => {
		const { controller, acknowledge, onChange } = setup();
		controller.update([notification(10)]);
		controller.update([notification(10), notification(20, 2)]);
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([notification(10)]);
		await controller.close([10]);
		expect(acknowledge).toHaveBeenCalledExactlyOnceWith([notification(10)]);
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([notification(20, 2)]);
	});

	it('rimuove un regalo annullato senza chiamare la conferma', () => {
		const { controller, acknowledge, onChange } = setup();
		controller.update([notification(10)]);
		controller.update([]);
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([]);
		expect(acknowledge).not.toHaveBeenCalled();
	});

	it('non conferma un nuovo regalo se il click precede il suo rendering', async () => {
		const { controller, acknowledge, onChange } = setup();
		controller.update([notification(10)]);
		controller.update([notification(20)]);
		await controller.close([10]);
		expect(acknowledge).not.toHaveBeenCalled();
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([notification(20)]);
	});

	it('non riapre un regalo confermato se una lettura lo contiene ancora', async () => {
		const { controller, acknowledge, onChange } = setup();
		controller.update([notification(10)]);
		await controller.close([10]);
		controller.update([notification(10)]);
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([]);
		expect(acknowledge).toHaveBeenCalledTimes(1);
	});

	it('segnala il fallimento e conserva la possibilita di ripresentare il regalo', async () => {
		const { controller, acknowledge, onChange, onError } = setup();
		const error = new Error('Conferma fallita');
		acknowledge.mockRejectedValueOnce(error);
		controller.update([notification(10)]);
		await controller.close([10]);
		expect(onError).toHaveBeenCalledExactlyOnceWith(error);
		expect(onChange.mock.calls.at(-1)?.[0]).toEqual([notification(10)]);
		expect(acknowledge).toHaveBeenCalledTimes(1);
	});

	it('ignora doppi click e non applica callback dopo dispose', async () => {
		const { controller, acknowledge, onChange } = setup();
		let finish!: () => void;
		acknowledge.mockReturnValueOnce(new Promise<void>((resolve) => (finish = resolve)));
		controller.update([notification(10)]);
		const pending = controller.close([10]);
		await controller.close([10]);
		const calls = onChange.mock.calls.length;
		controller.dispose();
		controller.dispose();
		controller.update([notification(20)]);
		finish();
		await pending;
		await controller.close([20]);
		expect(acknowledge).toHaveBeenCalledTimes(1);
		expect(onChange).toHaveBeenCalledTimes(calls);
	});
});

const destinationInput = document.getElementById('destination');
const destinationsList = document.getElementById('destinations');
const fileInput = document.getElementById('files');
const dropZone = document.getElementById('drop');
const status = document.getElementById('status');
const form = document.getElementById('save-form');
const queue = document.getElementById('queue');
const saveButton = document.getElementById('save');
const clearButton = document.getElementById('clear');
const result = document.getElementById('result');
const resultBody = document.getElementById('result-body');

let busy = false;

function setStatus(message, kind = '') {
	status.textContent = message;
	status.className = `status ${kind}`.trim();
}

function setBusy(value) {
	busy = value;
	saveButton.disabled = value || !queue.children.length;
	clearButton.disabled = value;
	fileInput.disabled = value;
}

function fileSize(bytes) {
	if (bytes < 1024) return `${bytes} B`;
	if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
	return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function loadDestinations() {
	try {
		const response = await fetch('/api/destinations');
		if (!response.ok) throw new Error('Elenco delle cartelle non disponibile');
		const data = await response.json();
		destinationsList.replaceChildren();
		for (const name of data.destinations) {
			const option = document.createElement('option');
			option.value = name;
			destinationsList.append(option);
		}
		if (!destinationInput.value) destinationInput.value = data.default;
	} catch (error) {
		setStatus(error.message, 'error');
	}
}

function addItem(item) {
	const row = document.createElement('li');
	row.className = 'queue-item';
	row.dataset.id = item.id;

	const preview = document.createElement('img');
	preview.src = item.preview_url;
	preview.alt = `Anteprima di ${item.original}`;
	preview.loading = 'lazy';

	const info = document.createElement('div');
	info.className = 'queue-info';

	const label = document.createElement('label');
	label.className = 'field';
	const labelText = document.createElement('span');
	labelText.textContent = 'Nome file (senza estensione)';
	const name = document.createElement('input');
	name.className = 'name';
	name.type = 'text';
	name.value = item.suggested;
	name.autocomplete = 'off';
	name.spellcheck = false;
	label.append(labelText, name);

	const meta = document.createElement('p');
	meta.className = 'meta';
	meta.textContent = `${item.width} × ${item.height} px · ${fileSize(item.bytes)} · originale: ${item.original}`;
	info.append(label, meta);

	const discard = document.createElement('button');
	discard.type = 'button';
	discard.className = 'ghost';
	discard.textContent = 'Scarta';
	discard.addEventListener('click', () => discardItem(item.id, row, discard));

	row.append(preview, info, discard);
	queue.append(row);
	form.hidden = false;
	setBusy(busy);
}

async function discardItem(id, row, button) {
	if (busy) return;
	button.disabled = true;
	try {
		const response = await fetch(`/api/staged/${id}`, { method: 'DELETE' });
		if (!response.ok) throw new Error('Immagine non più disponibile');
		row.remove();
		if (!queue.children.length) form.hidden = true;
		setBusy(false);
		setStatus(queue.children.length ? 'Immagine scartata.' : 'Elenco vuoto.');
	} catch (error) {
		button.disabled = false;
		setStatus(error.message, 'error');
	}
}

async function uploadFiles(fileList) {
	const files = [...fileList].filter(
		(file) => file.type.startsWith('image/') || /\.(png|jpe?g|webp)$/i.test(file.name)
	);
	if (!files.length) {
		setStatus('Scegli almeno un file immagine (png, jpg o webp).', 'error');
		return;
	}
	result.hidden = true;
	setBusy(true);
	setStatus(`Carico e converto ${files.length} ${files.length === 1 ? 'immagine' : 'immagini'}…`);
	const body = new FormData();
	for (const file of files) body.append('files', file, file.name);
	try {
		const response = await fetch('/api/upload', { method: 'POST', body });
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(data.detail || 'Caricamento non riuscito');
		for (const item of data.items) addItem(item);
		const errors = data.errors || [];
		if (errors.length) {
			const detail = errors.map((error) => `${error.filename}: ${error.message}`).join(' · ');
			setStatus(
				`${data.items.length} pronte, ${errors.length} scartate. ${detail}`,
				'error'
			);
		} else if (data.items.length) {
			setStatus(
				`${data.items.length} ${data.items.length === 1 ? 'immagine pronta' : 'immagini pronte'}: controlla i nomi e salva.`,
				'ok'
			);
		} else {
			setStatus('Nessuna immagine valida caricata.', 'error');
		}
	} catch (error) {
		setStatus(error.message, 'error');
	} finally {
		setBusy(false);
	}
}

function showResult(saved, errors, destination) {
	if (!saved.length && !errors.length) {
		result.hidden = true;
		return;
	}
	result.hidden = false;
	resultBody.replaceChildren();
	if (saved.length) {
		const title = document.createElement('p');
		title.textContent = `Salvate in ${destination}:`;
		const list = document.createElement('ul');
		for (const entry of saved) {
			const item = document.createElement('li');
			item.textContent = entry.file;
			list.append(item);
		}
		resultBody.append(title, list);
	}
	if (errors.length) {
		const title = document.createElement('p');
		title.className = 'error';
		title.textContent = 'Non salvate:';
		const list = document.createElement('ul');
		for (const error of errors) {
			const item = document.createElement('li');
			item.textContent = error.message;
			list.append(item);
		}
		resultBody.append(title, list);
	}
}

async function saveAll(event) {
	event.preventDefault();
	if (busy || !queue.children.length) return;
	const destination = destinationInput.value.trim();
	if (!destination) {
		setStatus('Indica la cartella di destinazione.', 'error');
		destinationInput.focus();
		return;
	}
	const items = [...queue.querySelectorAll('.queue-item')].map((row) => ({
		id: row.dataset.id,
		name: row.querySelector('.name').value
	}));
	setBusy(true);
	setStatus('Salvo le immagini…');
	try {
		const response = await fetch('/api/save', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ destination, items })
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(data.detail || 'Salvataggio non riuscito');
		const saved = data.saved || [];
		const errors = data.errors || [];
		for (const entry of saved) {
			const row = queue.querySelector(`[data-id="${entry.id}"]`);
			if (row) row.remove();
		}
		if (!queue.children.length) form.hidden = true;
		showResult(saved, errors, destination);
		if (errors.length) {
			setStatus(`${saved.length} salvate, ${errors.length} non salvate.`, 'error');
		} else {
			setStatus(
				`${saved.length} ${saved.length === 1 ? 'immagine salvata' : 'immagini salvate'} in ${destination}.`,
				'ok'
			);
		}
	} catch (error) {
		setStatus(error.message, 'error');
	} finally {
		setBusy(false);
	}
}

async function clearQueue() {
	if (busy || !queue.children.length) return;
	setBusy(true);
	const rows = [...queue.querySelectorAll('.queue-item')];
	let failures = 0;
	for (const row of rows) {
		try {
			const response = await fetch(`/api/staged/${row.dataset.id}`, { method: 'DELETE' });
			if (!response.ok) throw new Error('Immagine non più disponibile');
			row.remove();
		} catch (error) {
			failures += 1;
			setStatus(error.message, 'error');
		}
	}
	form.hidden = !queue.children.length;
	setBusy(false);
	if (!failures) setStatus('Elenco svuotato.');
}

fileInput.addEventListener('change', () => {
	uploadFiles(fileInput.files);
	fileInput.value = '';
});

dropZone.addEventListener('dragover', (event) => {
	event.preventDefault();
	dropZone.classList.add('over');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('over'));

dropZone.addEventListener('drop', (event) => {
	event.preventDefault();
	dropZone.classList.remove('over');
	uploadFiles(event.dataTransfer.files);
});

form.addEventListener('submit', saveAll);
clearButton.addEventListener('click', clearQueue);

loadDestinations();

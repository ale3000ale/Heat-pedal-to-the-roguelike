const FIELDS = {
	events: [
		{ key: 'image', label: 'Path immagine', type: 'path' },
		{ key: 'nome', label: 'Nome', type: 'text' },
		{ key: 'effetto', label: 'Effetto', type: 'textarea' },
		{ key: 'sponsor', label: 'Sponsor', type: 'number' },
		{ key: 'fotografi', label: 'Fotografi', type: 'text' }
	],
	maps: [
		{ key: 'image', label: 'Path immagine', type: 'path' },
		{ key: 'nome', label: 'Nome', type: 'text' },
		{ key: 'giri', label: 'Giri', type: 'number' },
		{ key: 'curve', label: 'Curve', type: 'number' },
		{ key: 'caselle', label: 'Caselle', type: 'number' },
		{ key: 'sezioni', label: 'Numero sezioni', type: 'sections' }
	]
};
const LABELS = { events: 'Eventi', maps: 'Mappe' };
const DESCRIPTIONS = {
	events: 'Schede degli eventi: nome, immagine, effetto, sponsor e fotografi.',
	maps: 'Schede delle mappe: nome, immagine, giri, curve, caselle e sezioni.'
};

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

const jsonToggle = document.getElementById('json-toggle');
const jsonMenu = document.getElementById('json-menu');
const addItemButton = document.getElementById('add-item');
const viewMedia = document.getElementById('view-media');
const viewJson = document.getElementById('view-json');
const jsonTitle = document.getElementById('json-title');
const jsonDescription = document.getElementById('json-description');
const jsonStatus = document.getElementById('json-status');
const cards = document.getElementById('cards');

const editModal = document.getElementById('edit-modal');
const editTitle = document.getElementById('edit-title');
const editForm = document.getElementById('edit-form');
const editPreview = document.getElementById('edit-preview');
const editPreviewImage = document.getElementById('edit-preview-image');
const editFields = document.getElementById('edit-fields');
const editError = document.getElementById('edit-error');
const confirmModal = document.getElementById('confirm-modal');
const confirmMessage = document.getElementById('confirm-message');
const mediaModal = document.getElementById('media-modal');
const mediaSearch = document.getElementById('media-search');
const mediaStatus = document.getElementById('media-status');
const mediaUp = document.getElementById('media-up');
const mediaCrumb = document.getElementById('media-crumb');
const mediaFolders = document.getElementById('media-folders');
const mediaGrid = document.getElementById('media-grid');
const noticeModal = document.getElementById('notice-modal');
const noticeMessage = document.getElementById('notice-message');
const noticeOk = document.getElementById('notice-ok');

const state = {
	view: 'media',
	kind: null,
	items: [],
	errors: [],
	editingIndex: null,
	highlightErrors: false,
	media: { path: '', parent: null, directories: [], images: [] },
	onImageSelect: null,
	folderSave: Promise.resolve(),
	confirmResolve: null
};

let busy = false;

function setStatus(node, message, kind = '') {
	node.textContent = message;
	node.className = `status ${kind}`.trim();
}

function show(node) {
	node.hidden = false;
}

function hide(node) {
	node.hidden = true;
}

function imageUrl(path) {
	return '/media/' + path.split('/').map(encodeURIComponent).join('/');
}

function fileStem(path) {
	const name = path.split('/').pop() || '';
	return name.replace(/\.[^.]+$/, '');
}

function detailOf(response, data) {
	return data.detail || `Richiesta non riuscita (${response.status})`;
}

function showNotice(message) {
	noticeMessage.textContent = message;
	show(noticeModal);
	noticeOk.focus();
}

function showPreview(path) {
	if (!path) {
		hide(editPreview);
		editPreviewImage.removeAttribute('src');
		return;
	}
	editPreviewImage.src = imageUrl(path);
	show(editPreview);
}

/* ---------------- Vista Media ---------------- */

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
		setStatus(status, error.message, 'error');
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
	show(form);
	setBusy(busy);
}

async function discardItem(id, row, button) {
	if (busy) return;
	button.disabled = true;
	try {
		const response = await fetch(`/api/staged/${id}`, { method: 'DELETE' });
		if (!response.ok) throw new Error('Immagine non più disponibile');
		row.remove();
		if (!queue.children.length) hide(form);
		setBusy(false);
		setStatus(status, queue.children.length ? 'Immagine scartata.' : 'Elenco vuoto.');
	} catch (error) {
		button.disabled = false;
		setStatus(status, error.message, 'error');
	}
}

async function uploadFiles(fileList) {
	const files = [...fileList].filter(
		(file) => file.type.startsWith('image/') || /\.(png|jpe?g|webp)$/i.test(file.name)
	);
	if (!files.length) {
		setStatus(status, 'Scegli almeno un file immagine (png, jpg o webp).', 'error');
		return;
	}
	hide(result);
	setBusy(true);
	setStatus(status, `Carico e converto ${files.length} ${files.length === 1 ? 'immagine' : 'immagini'}…`);
	const body = new FormData();
	for (const file of files) body.append('files', file, file.name);
	try {
		const response = await fetch('/api/upload', { method: 'POST', body });
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(detailOf(response, data));
		for (const item of data.items) addItem(item);
		const errors = data.errors || [];
		if (errors.length) {
			const detail = errors.map((error) => `${error.filename}: ${error.message}`).join(' · ');
			setStatus(
				status,
				`${data.items.length} pronte, ${errors.length} scartate. ${detail}`,
				'error'
			);
		} else if (data.items.length) {
			setStatus(
				status,
				`${data.items.length} ${data.items.length === 1 ? 'immagine pronta' : 'immagini pronte'}: controlla i nomi e salva.`,
				'ok'
			);
		} else {
			setStatus(status, 'Nessuna immagine valida caricata.', 'error');
		}
	} catch (error) {
		setStatus(status, error.message, 'error');
	} finally {
		setBusy(false);
	}
}

function showResult(saved, errors, destination) {
	if (!saved.length && !errors.length) {
		hide(result);
		return;
	}
	show(result);
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
		setStatus(status, 'Indica la cartella di destinazione.', 'error');
		destinationInput.focus();
		return;
	}
	const items = [...queue.querySelectorAll('.queue-item')].map((row) => ({
		id: row.dataset.id,
		name: row.querySelector('.name').value
	}));
	setBusy(true);
	setStatus(status, 'Salvo le immagini…');
	try {
		const response = await fetch('/api/save', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ destination, items })
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(detailOf(response, data));
		const saved = data.saved || [];
		const errors = data.errors || [];
		for (const entry of saved) {
			const row = queue.querySelector(`[data-id="${entry.id}"]`);
			if (row) row.remove();
		}
		if (!queue.children.length) hide(form);
		showResult(saved, errors, destination);
		if (errors.length) {
			setStatus(status, `${saved.length} salvate, ${errors.length} non salvate.`, 'error');
		} else {
			setStatus(
				status,
				`${saved.length} ${saved.length === 1 ? 'immagine salvata' : 'immagini salvate'} in ${destination}.`,
				'ok'
			);
		}
	} catch (error) {
		setStatus(status, error.message, 'error');
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
			setStatus(status, error.message, 'error');
		}
	}
	if (queue.children.length) show(form);
	else hide(form);
	setBusy(false);
	if (!failures) setStatus(status, 'Elenco svuotato.');
}

/* ---------------- Navigazione ---------------- */

function closeDropdown() {
	hide(jsonMenu);
	jsonToggle.setAttribute('aria-expanded', 'false');
}

function markActive(view) {
	for (const button of document.querySelectorAll('.nav-link')) {
		button.classList.toggle('active', button.dataset.view === view || (view !== 'media' && button === jsonToggle));
	}
}

function showView(view) {
	state.view = view;
	closeDropdown();
	if (view === 'media') {
		show(viewMedia);
		hide(viewJson);
		hide(addItemButton);
	} else {
		state.kind = view;
		hide(viewMedia);
		show(viewJson);
		show(addItemButton);
		jsonTitle.textContent = LABELS[view];
		jsonDescription.textContent = DESCRIPTIONS[view];
		setStatus(jsonStatus, `Carico ${LABELS[view].toLowerCase()}…`);
		loadData(view);
	}
	markActive(view);
}

/* ---------------- Viste JSON ---------------- */

async function loadData(kind) {
	try {
		const response = await fetch(`/api/data/${kind}`);
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(detailOf(response, data));
		state.items = data.items || [];
		renderCards();
		const errors = state.errors.filter((fields) => fields.length).length;
		let message = `${state.items.length} elementi. Clicca una scheda per modificarla.`;
		if (errors) message += ` ${errors} con campi da correggere in cima.`;
		if (data.repaired) message += ' Campi mancanti o non validi impostati a null.';
		setStatus(jsonStatus, message, errors ? 'error' : 'ok');
		if (data.created) {
			showNotice(`Creato backend/json/${kind}.json vuoto.`);
		}
	} catch (error) {
		setStatus(jsonStatus, error.message, 'error');
	}
}

function valueRow(label, value) {
	const row = document.createElement('div');
	row.className = 'value-row';
	const name = document.createElement('span');
	name.className = 'value-label';
	name.textContent = label;
	const content = document.createElement('span');
	content.className = 'value-content';
	content.textContent = Array.isArray(value) ? value.join(', ') : String(value ?? '');
	row.append(name, content);
	return row;
}

function errorLabels(fields) {
	return fields
		.map((key) => FIELDS[state.kind].find((field) => field.key === key)?.label || key)
		.join(', ');
}

function invalidFields(item, index, items) {
	const found = new Set();
	for (const field of FIELDS[state.kind]) {
		const value = item[field.key];
		if (field.type === 'sections') {
			if (!Array.isArray(value) || value.some((entry) => !Number.isInteger(entry) || entry < 0)) {
				found.add(field.key);
			}
		} else if (field.type === 'number') {
			if (!Number.isInteger(value) || value < 0) found.add(field.key);
		} else if (typeof value !== 'string' || !value.trim()) {
			found.add(field.key);
		}
	}
	const name = typeof item.nome === 'string' ? item.nome.trim().toLowerCase() : '';
	if (
		name &&
		items.some(
			(other, otherIndex) =>
				otherIndex !== index &&
				typeof other.nome === 'string' &&
				other.nome.trim().toLowerCase() === name
		)
	) {
		found.add('nome');
	}
	const image = typeof item.image === 'string' ? item.image.replace(/\\/g, '/').toLowerCase() : '';
	if (
		image &&
		items.some(
			(other, otherIndex) =>
				otherIndex !== index &&
				typeof other.image === 'string' &&
				other.image.replace(/\\/g, '/').toLowerCase() === image
		)
	) {
		found.add('image');
	}
	return [...found];
}

function refreshErrors() {
	state.errors = state.items.map((item, index) => invalidFields(item, index, state.items));
	return state.errors.filter((fields) => fields.length).length;
}

function renderCards() {
	refreshErrors();
	cards.replaceChildren();
	const ordered = state.items
		.map((item, index) => ({ item, index }))
		.sort((left, right) => state.errors[right.index].length - state.errors[left.index].length);
	for (const { item, index } of ordered) {
		const title = typeof item.nome === 'string' && item.nome.trim() ? item.nome.trim() : '(senza nome)';
		const card = document.createElement('article');
		card.className = 'card';
		card.tabIndex = 0;
		card.setAttribute('role', 'button');
		card.setAttribute('aria-label', `Modifica ${title}`);

		const media = document.createElement('div');
		media.className = 'card-media';
		const image = document.createElement('img');
		image.className = 'card-image';
		image.alt = `Immagine di ${title}`;
		image.loading = 'lazy';
		if (item.image) {
			image.src = imageUrl(item.image);
		} else {
			image.hidden = true;
		}
		media.append(image);

		const errors = state.errors[index];
		if (errors.length) {
			const alert = document.createElement('button');
			alert.type = 'button';
			alert.className = 'card-alert';
			alert.textContent = '⚠';
			alert.title = `Campi con problemi: ${errorLabels(errors)}`;
			alert.setAttribute('aria-label', `Campi con problemi: ${errorLabels(errors)}`);
			alert.addEventListener('click', (event) => {
				event.stopPropagation();
				openEdit(index, true);
			});
			media.append(alert);
		}

		const values = document.createElement('div');
		values.className = 'card-values';
		const heading = document.createElement('h2');
		heading.textContent = title;
		values.append(heading);
		for (const field of FIELDS[state.kind]) {
			if (field.key === 'nome') continue;
			values.append(valueRow(field.label, item[field.key]));
		}

		card.append(media, values);
		card.addEventListener('click', () => openEdit(index));
		card.addEventListener('keydown', (event) => {
			if (event.key === 'Enter' || event.key === ' ') {
				event.preventDefault();
				openEdit(index);
			}
		});
		cards.append(card);
	}
}

function sectionControl(field, value) {
	const wrapper = document.createElement('div');
	wrapper.className = 'sections-field';
	wrapper.dataset.key = field.key;
	const count = document.createElement('input');
	count.type = 'number';
	count.min = '0';
	count.step = '1';
	count.dataset.role = 'count';
	count.setAttribute('aria-label', 'Numero sezioni');
	count.value = Array.isArray(value) ? String(value.length) : '';
	const list = document.createElement('div');
	list.className = 'section-inputs';
	list.dataset.role = 'items';
	const values = Array.isArray(value) ? [...value] : [];

	function renderInputs() {
		list.replaceChildren();
		const raw = count.value.trim();
		if (!raw) return;
		const total = Number(raw);
		if (!Number.isInteger(total) || total < 0) return;
		values.length = total;
		for (let index = 0; index < total; index += 1) {
			const input = document.createElement('input');
			input.type = 'number';
			input.min = '0';
			input.step = '1';
			input.dataset.index = String(index);
			input.setAttribute('aria-label', `Sezione ${index + 1}`);
			input.value = values[index] ?? '';
			input.addEventListener('input', () => {
				values[index] = input.value.trim() === '' ? null : Number(input.value);
			});
			list.append(input);
		}
	}

	count.addEventListener('input', renderInputs);
	renderInputs();
	wrapper.append(count, list);
	return wrapper;
}

function controlFor(field, value) {
	if (field.type === 'path') {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'path-button';
		button.dataset.key = field.key;
		button.dataset.path = value || '';
		button.textContent = value || 'Scegli un’immagine da backend/media…';
		button.addEventListener('click', () => {
			openMediaPicker((path) => {
				button.dataset.path = path;
				button.textContent = path;
				const nameControl = editFields.querySelector('[data-key="nome"]');
				if (nameControl) nameControl.value = fileStem(path);
				showPreview(path);
			});
		});
		return button;
	}
	if (field.type === 'sections') return sectionControl(field, value);
	let control;
	if (field.type === 'textarea') {
		control = document.createElement('textarea');
		control.rows = 3;
	} else {
		control = document.createElement('input');
		control.type = field.type === 'number' ? 'number' : 'text';
		if (field.type === 'number') {
			control.min = '0';
			control.step = '1';
		} else {
			control.autocomplete = 'off';
		}
	}
	control.dataset.key = field.key;
	control.value = value ?? '';
	return control;
}

function openEdit(index, highlight = false) {
	state.editingIndex = index;
	state.highlightErrors = highlight;
	const item = index === null ? {} : state.items[index];
	const title = typeof item.nome === 'string' && item.nome.trim() ? item.nome.trim() : 'elemento';
	editTitle.textContent = index === null ? `Aggiungi a ${LABELS[state.kind].toLowerCase()}` : `Modifica ${title}`;
	const errors = index === null ? [] : state.errors[index] || [];
	setStatus(editError, '');
	editFields.replaceChildren();
	for (const field of FIELDS[state.kind]) {
		const label = document.createElement('label');
		label.className = 'field';
		if (highlight && errors.includes(field.key)) label.classList.add('invalid');
		const caption = document.createElement('span');
		caption.textContent = field.label;
		label.append(caption, controlFor(field, item[field.key]));
		editFields.append(label);
	}
	if (highlight && errors.length) {
		setStatus(editError, `Campi con problemi: ${errorLabels(errors)}.`, 'error');
	}
	showPreview(item.image || '');
	show(editModal);
}

function collectForm() {
	const payload = {};
	for (const field of FIELDS[state.kind]) {
		const control = editFields.querySelector(`[data-key="${field.key}"]`);
		if (field.type === 'path') {
			payload[field.key] = control.dataset.path || '';
		} else if (field.type === 'number') {
			payload[field.key] = control.value === '' ? Number.NaN : Number(control.value);
		} else if (field.type === 'sections') {
			const raw = control.querySelector('[data-role="count"]').value.trim();
			const total = raw === '' ? Number.NaN : Number(raw);
			if (!Number.isInteger(total) || total < 0) {
				payload[field.key] = null;
				continue;
			}
			payload[field.key] = [];
			for (let index = 0; index < total; index += 1) {
				const input = control.querySelector(`[data-index="${index}"]`);
				const value = input ? input.value.trim() : '';
				payload[field.key].push(
					value !== '' && Number.isInteger(Number(value)) && Number(value) >= 0
						? Number(value)
						: null
				);
			}
		} else {
			payload[field.key] = control.value;
		}
	}
	return payload;
}

function validateForm(payload) {
	for (const field of FIELDS[state.kind]) {
		const value = payload[field.key];
		if (field.type === 'sections') {
			if (!Array.isArray(value)) {
				return `${field.label} deve essere un numero intero non negativo.`;
			}
			if (value.some((entry) => !Number.isInteger(entry) || entry < 0)) {
				return 'Compila tutte le sezioni con numeri interi non negativi.';
			}
		} else if (field.type === 'number') {
			if (!Number.isInteger(value) || value < 0) return `${field.label} deve essere un numero intero non negativo.`;
		} else if (typeof value === 'string' && !value.trim()) {
			return `${field.label} è obbligatorio.`;
		}
	}
	return null;
}

function askConfirm(message) {
	return new Promise((resolve) => {
		state.confirmResolve = resolve;
		confirmMessage.textContent = message;
		show(confirmModal);
	});
}

function answerConfirm(answer) {
	hide(confirmModal);
	const resolve = state.confirmResolve;
	state.confirmResolve = null;
	if (resolve) resolve(answer);
}

async function saveItem(payload) {
	const method = state.editingIndex === null ? 'POST' : 'PUT';
	const path = state.editingIndex === null
		? `/api/data/${state.kind}`
		: `/api/data/${state.kind}/${state.editingIndex}`;
	try {
		const response = await fetch(path, {
			method,
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload)
		});
		const data = await response.json().catch(() => ({}));
		if (!response.ok) {
			setStatus(editError, detailOf(response, data), 'error');
			return false;
		}
		state.items = data.items || [];
		renderCards();
		hide(editModal);
		setStatus(jsonStatus, 'Elemento salvato.', 'ok');
		return true;
	} catch (error) {
		setStatus(editError, error.message, 'error');
		return false;
	}
}

async function submitEdit(event) {
	event.preventDefault();
	const payload = collectForm();
	const invalid = validateForm(payload);
	if (invalid) {
		setStatus(editError, invalid, 'error');
		return;
	}
	const message = state.editingIndex === null
		? 'Aggiungere questo elemento al JSON?'
		: 'Salvare le modifiche a questo elemento?';
	const confirmed = await askConfirm(message);
	if (!confirmed) return;
	setStatus(editError, '');
	await saveItem(payload);
}

/* ---------------- Esploratore media ---------------- */

async function rememberMediaFolder(kind, path) {
	try {
		const response = await fetch('/api/media/last-folder', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ kind, path })
		});
		if (!response.ok) {
			const data = await response.json().catch(() => ({}));
			throw new Error(detailOf(response, data));
		}
	} catch (error) {
		setStatus(mediaStatus, `Cartella non salvata: ${error.message}`, 'error');
	}
}

function queueMediaFolderSave(kind, path) {
	state.folderSave = state.folderSave
		.catch(() => {})
		.then(() => rememberMediaFolder(kind, path));
}

async function loadMediaFolder(path = '', remember = true) {
	try {
		const query = path ? `?path=${encodeURIComponent(path)}` : '';
		const response = await fetch('/api/media/browse' + query);
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(detailOf(response, data));
		state.media = {
			path: data.path || '',
			parent: data.parent ?? null,
			directories: data.directories || [],
			images: data.images || []
		};
		const where = state.media.path ? `backend/media/${state.media.path}` : 'backend/media';
		setStatus(mediaStatus, `${state.media.images.length} immagini in ${where}.`);
		renderMediaGrid();
		if (remember) queueMediaFolderSave(state.kind, state.media.path);
	} catch (error) {
		setStatus(mediaStatus, error.message, 'error');
	}
}

async function openMediaPicker(onSelect) {
	state.onImageSelect = onSelect;
	mediaSearch.value = '';
	show(mediaModal);
	let last = '';
	try {
		const response = await fetch(
			'/api/media/last-folder?kind=' + encodeURIComponent(state.kind)
		);
		const data = await response.json().catch(() => ({}));
		if (!response.ok) throw new Error(detailOf(response, data));
		last = data.path || '';
	} catch (error) {
		last = '';
	}
	await loadMediaFolder(last, false);
}

function renderMediaGrid() {
	mediaFolders.replaceChildren();
	mediaGrid.replaceChildren();
	mediaCrumb.replaceChildren();
	mediaUp.disabled = state.media.parent === null;

	const parts = state.media.path ? state.media.path.split('/') : [];
	const crumbs = [{ label: 'media', path: '' }];
	let current = '';
	for (const part of parts) {
		current = current ? `${current}/${part}` : part;
		crumbs.push({ label: part, path: current });
	}
	crumbs.forEach((crumb, index) => {
		if (index) {
			const separator = document.createElement('span');
			separator.className = 'media-separator';
			separator.textContent = '/';
			mediaCrumb.append(separator);
		}
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'media-crumb';
		button.textContent = crumb.label;
		button.addEventListener('click', () => loadMediaFolder(crumb.path));
		mediaCrumb.append(button);
	});

	const query = mediaSearch.value.trim().toLowerCase();
	const folders = state.media.directories.filter((entry) =>
		entry.name.toLowerCase().includes(query)
	);
	for (const entry of folders) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'folder-item';
		button.textContent = `📁 ${entry.name}`;
		button.title = entry.path;
		button.addEventListener('click', () => loadMediaFolder(entry.path));
		mediaFolders.append(button);
	}

	const matches = state.media.images.filter((entry) => entry.name.toLowerCase().includes(query));
	if (!matches.length && !folders.length) {
		const empty = document.createElement('p');
		empty.className = 'hint';
		empty.textContent = query
			? 'Nessun elemento trovato in questa cartella.'
			: 'Questa cartella non contiene immagini o sottocartelle.';
		mediaGrid.append(empty);
		return;
	}
	for (const entry of matches) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'media-item';
		button.title = entry.path;
		const preview = document.createElement('img');
		preview.src = entry.url;
		preview.alt = '';
		preview.loading = 'lazy';
		const name = document.createElement('span');
		name.className = 'media-path';
		name.textContent = entry.name;
		button.append(preview, name);
		button.addEventListener('click', () => {
			queueMediaFolderSave(state.kind, state.media.path);
			if (state.onImageSelect) state.onImageSelect(entry.path);
			hide(mediaModal);
		});
		mediaGrid.append(button);
	}
}

/* ---------------- Eventi ---------------- */

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

jsonToggle.addEventListener('click', () => {
	const open = jsonMenu.hidden;
	if (open) {
		show(jsonMenu);
		jsonToggle.setAttribute('aria-expanded', 'true');
	} else {
		closeDropdown();
	}
});

for (const button of document.querySelectorAll('[data-view]')) {
	button.addEventListener('click', () => showView(button.dataset.view));
}

addItemButton.addEventListener('click', () => openEdit(null));
editForm.addEventListener('submit', submitEdit);
document.getElementById('edit-cancel').addEventListener('click', () => hide(editModal));
document.getElementById('confirm-yes').addEventListener('click', () => answerConfirm(true));
document.getElementById('confirm-no').addEventListener('click', () => answerConfirm(false));
document.getElementById('media-cancel').addEventListener('click', () => hide(mediaModal));
mediaUp.addEventListener('click', () => {
	if (state.media.parent !== null) loadMediaFolder(state.media.parent);
});
editPreviewImage.addEventListener('error', () => hide(editPreview));
noticeOk.addEventListener('click', () => hide(noticeModal));
mediaSearch.addEventListener('input', renderMediaGrid);

for (const backdrop of document.querySelectorAll('.modal-backdrop')) {
	backdrop.addEventListener('click', () => {
		if (backdrop.dataset.close === 'edit') hide(editModal);
		if (backdrop.dataset.close === 'confirm') answerConfirm(false);
		if (backdrop.dataset.close === 'media') hide(mediaModal);
		if (backdrop.dataset.close === 'notice') hide(noticeModal);
	});
}

loadDestinations();

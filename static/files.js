// File/Scraper Management page (/files). Mirrors static/admin.js's structure
// (DataTables + window.AdminShared helpers for modals/toasts/escaping) so this
// page renders and behaves consistently with User Management/Trash, rather
// than inventing a second UI pattern.
(function () {
  const tableEl = document.getElementById('files-table');
  if (!tableEl) return; // Not on the /files page.

  const Shared = window.AdminShared;
  const errorEl = document.getElementById('files-error');
  const loadingEl = document.getElementById('files-loading');
  const newBtn = document.getElementById('files-new-btn');
  const refreshBtn = document.getElementById('files-refresh-btn');
  const refreshIcon = document.getElementById('files-refresh-icon');

  const modal = document.getElementById('files-modal');
  const modalTitle = document.getElementById('files-modal-title');
  const modalError = document.getElementById('files-modal-error');
  const form = document.getElementById('files-form');
  const idInput = document.getElementById('files-form-id');
  const siteNameInput = document.getElementById('files-form-site-name');
  const logoInput = document.getElementById('files-form-logo');
  const submitBtn = document.getElementById('files-form-submit');
  const submitLabel = document.getElementById('files-form-submit-label');

  const deleteModal = document.getElementById('files-delete-modal');
  const deleteText = document.getElementById('files-delete-text');
  const deleteError = document.getElementById('files-delete-error');
  const deleteConfirmBtn = document.getElementById('files-delete-confirm');

  // --- URLs: paste a list directly into the textarea, or upload a CSV --
  // the CSV's rows get converted into that same newline list (via
  // /api/files/parse-urls) so by submit time there's one source of truth,
  // regardless of which path was used. ---
  const urlsTextarea = document.getElementById('files-form-urls');
  const urlsCsvInput = document.getElementById('files-form-urls-csv');
  const urlsSpinner = document.getElementById('files-form-urls-spinner');
  const urlsStatus = document.getElementById('files-form-urls-status');
  const URLS_STATUS_DEFAULT = "A CSV's URL column (or first column) is converted into the list above -- review it before saving.";

  // --- Python File: upload-only now (no more "pick an existing file"
  // dropdown), gated to SuperAdmin/Admin since it's the only way to set/
  // change a scraper's code. Everyone else still sees the current file name
  // read-only and can save Site Name/Logo edits without touching it. ---
  const currentFileNote = document.getElementById('files-form-current-file');
  const currentFileNameEl = document.getElementById('files-form-current-file-name');
  const uploadPanel = document.getElementById('files-form-upload-panel');
  const noAccessNote = document.getElementById('files-form-no-access');
  const uploadInput = document.getElementById('files-form-upload');
  const uploadStatus = document.getElementById('files-form-upload-status');
  const uploadSpinner = document.getElementById('files-form-upload-spinner');
  const submitSpinner = document.getElementById('files-form-submit-spinner');

  let csrfToken = null;
  let currentRole = null;
  let files = [];
  let filesById = new Map();
  let table = null;
  let pendingDeleteId = null;
  let inFlightStarts = new Map(); // file_id -> 'start'|'stop', for rows currently mid-request
  // Holds whatever python_file_path the form will submit: pre-filled with the
  // record's existing path when editing (so saving Site Name/Logo alone
  // doesn't require touching the file), overwritten if a new file is uploaded.
  let uploadedFileName = null;

  const canUploadScripts = () => currentRole === 'SuperAdmin' || currentRole === 'Admin';

  // No background polling -- the table only reloads on an explicit user
  // action (the Refresh button, or as the direct result of Start/Stop/Save/
  // Delete). lastFilesSnapshot still skips an unnecessary table rebuild if a
  // manual refresh happens to return exactly the same data.
  let lastFilesSnapshot = null;

  function logoCellHtml(row) {
    if (row.logo) {
      const safeUrl = Shared.escapeHtml(row.logo);
      return `<img src="${safeUrl}" alt="" class="w-8 h-8 rounded-lg object-cover border border-slate-200" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'inline-flex w-8 h-8 rounded-lg bg-slate-100 items-center justify-center text-slate-400 text-xs',textContent:'?'}))" />`;
    }
    return '<span class="inline-flex w-8 h-8 rounded-lg bg-slate-100 items-center justify-center text-slate-400 text-xs">?</span>';
  }

  function urlsCellHtml(row) {
    const urls = row.urls || [];
    if (!urls.length) {
      return '<span class="text-xs text-slate-400">No URLs</span>';
    }
    return `<button type="button" data-action="view-urls" data-id="${row.fileId}" class="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 hover:bg-slate-200 cursor-pointer">${urls.length} URL${urls.length === 1 ? '' : 's'}</button>`;
  }

  function openUrlsModal(file) {
    const modal = document.getElementById('files-urls-modal');
    const subtitle = document.getElementById('files-urls-modal-subtitle');
    const list = document.getElementById('files-urls-modal-list');
    const urls = file.urls || [];

    subtitle.textContent = `${file.siteName} — ${urls.length} URL${urls.length === 1 ? '' : 's'}`;
    list.innerHTML = urls.length
      ? urls.map((url) => `
          <li class="rounded-lg bg-slate-50 px-3 py-2">
            <span class="break-all text-sm text-slate-700">${Shared.escapeHtml(url)}</span>
          </li>
        `).join('')
      : '<li class="text-sm text-slate-400">No URLs saved for this scraper.</li>';

    Shared.openModal(modal);
  }

  function statusBadgeHtml(row) {
    return row.working
      ? '<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">Running</span>'
      : '<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-200 text-slate-500">Not Running</span>';
  }

  function actionsCellHtml(row) {
    const busyAction = inFlightStarts.get(row.fileId);
    const busy = !!busyAction;
    const startStopLabel = busyAction === 'stop' ? 'Stopping…' : busyAction === 'start' ? 'Starting…' : (row.working ? 'Stop' : 'Start');
    const startStopBtn = row.working
      ? `<button type="button" data-action="stop" data-id="${row.fileId}" ${busy ? 'disabled' : ''} class="text-xs font-semibold ${busy ? 'text-slate-300 cursor-not-allowed' : 'text-rose-600 hover:underline cursor-pointer'}">${startStopLabel}</button>`
      : `<button type="button" data-action="start" data-id="${row.fileId}" ${busy ? 'disabled' : ''} class="text-xs font-semibold ${busy ? 'text-slate-300 cursor-not-allowed' : 'text-emerald-600 hover:underline cursor-pointer'}">${startStopLabel}</button>`;
    return `
      <div class="flex items-center justify-end gap-3">
        ${startStopBtn}
        <button type="button" data-action="edit" data-id="${row.fileId}" ${row.working ? 'disabled title="Stop the scraper before editing it"' : ''} class="text-xs font-semibold ${row.working ? 'text-slate-300 cursor-not-allowed' : 'text-slate-600 hover:underline cursor-pointer'}">Edit</button>
        <button type="button" data-action="delete" data-id="${row.fileId}" ${row.working ? 'disabled title="Stop the scraper before deleting it"' : ''} class="text-xs font-semibold ${row.working ? 'text-slate-300 cursor-not-allowed' : 'text-rose-600 hover:underline cursor-pointer'}">Delete</button>
      </div>`;
  }

  function initTable() {
    table = $(tableEl).DataTable(Shared.commonDataTableOptions({
      data: [],
      order: [[1, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Search site name, python file…',
        lengthMenu: 'Show _MENU_ per page',
        info: 'Showing _START_ to _END_ of _TOTAL_',
        infoEmpty: 'No scrapers to show',
        infoFiltered: '(filtered from _MAX_ total)',
        paginate: { first: 'First', last: 'Last', next: 'Next', previous: 'Previous' },
      },
      columns: [
        {
          data: null, orderable: false, searchable: false,
          render: (data, type, row) => (type === 'display' ? logoCellHtml(row) : ''),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? Shared.escapeHtml(row.siteName) : row.siteName),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? `<code class="text-xs">${Shared.escapeHtml(row.pythonFilePath)}</code>` : row.pythonFilePath),
        },
        {
          data: null, orderable: false,
          render: (data, type, row) => (type === 'display' ? urlsCellHtml(row) : row.urlCount),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? statusBadgeHtml(row) : (row.working ? 'Running' : 'Not Running')),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? Shared.dateTimeHtml(row.createDateRaw) : (row.createDateRaw || '')),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? Shared.dateTimeHtml(row.updateDateRaw) : (row.updateDateRaw || '')),
        },
        {
          data: null, orderable: false, searchable: false, className: 'text-right',
          render: (data, type, row) => (type === 'display' ? actionsCellHtml(row) : ''),
        },
      ],
    }));
  }

  function showTable() {
    loadingEl.classList.add('hidden');
    tableEl.classList.remove('hidden');
  }

  async function loadMe() {
    try {
      const response = await fetch('/api/me');
      if (!response.ok) return;
      const data = await response.json();
      csrfToken = data.csrfToken;
      currentRole = data.user ? data.user.role : null;
      // Uploading is the only way left to set/change a scraper's Python
      // file, and it's code that will later run on the server -- so both
      // creating a scraper and the upload control itself are SuperAdmin/
      // Admin-only. Everyone else can still open Edit to change Site Name/
      // Logo (the file stays whatever it already was).
      newBtn.classList.toggle('hidden', !canUploadScripts());
      uploadPanel.classList.toggle('hidden', !canUploadScripts());
      noAccessNote.classList.toggle('hidden', canUploadScripts());
    } catch (err) {
      // Leave csrfToken/currentRole null -- any mutating request will just get a clear 401/403.
    }
  }

  async function loadFiles({ silent } = {}) {
    if (!silent) Shared.hideError(errorEl);
    if (refreshBtn) {
      refreshBtn.disabled = true;
      refreshIcon.classList.add('animate-spin');
    }
    try {
      const response = await fetch('/api/files?perPage=1000');
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to load scrapers.';
        Shared.showError(errorEl, message);
        if (!silent) Shared.showToast(message, 'error');
        return;
      }
      files = data.files || [];
      filesById = new Map(files.map((f) => [f.fileId, f]));

      // Rebuilding the table (clear/add/draw) recreates every row's DOM node
      // -- skip it when the data hasn't actually changed since last time.
      const snapshot = JSON.stringify(files);
      if (snapshot !== lastFilesSnapshot) {
        lastFilesSnapshot = snapshot;
        table.clear();
        table.rows.add(files);
        table.draw(false);
      }
    } catch (err) {
      Shared.showError(errorEl, 'Network error while loading scrapers.');
      if (!silent) Shared.showToast('Network error while loading scrapers.', 'error');
    } finally {
      showTable();
      if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshIcon.classList.remove('animate-spin');
      }
    }
  }

  // --- Create/Edit modal ---
  function resetForm() {
    form.reset();
    idInput.value = '';
    Shared.hideError(modalError);
    uploadedFileName = null;
    currentFileNote.classList.add('hidden');
    if (uploadInput) uploadInput.value = '';
    if (uploadStatus) {
      uploadStatus.textContent = 'Uploads a .py file into the scrapers/ folder. Re-uploading the same file name updates that scraper’s code in place.';
      uploadStatus.className = 'text-[11px] text-slate-400';
    }
    if (urlsCsvInput) urlsCsvInput.value = '';
    if (urlsStatus) {
      urlsStatus.textContent = URLS_STATUS_DEFAULT;
      urlsStatus.className = '';
    }
  }

  function openCreateModal() {
    resetForm();
    modalTitle.textContent = 'Add New Scraper';
    submitLabel.textContent = 'Add Scraper';
    Shared.openModal(modal);
  }

  function openEditModal(file) {
    resetForm();
    modalTitle.textContent = 'Edit Scraper';
    submitLabel.textContent = 'Save Changes';
    idInput.value = file.fileId;
    siteNameInput.value = file.siteName;
    logoInput.value = file.logo || '';
    // Pre-filled with the record's current list -- resaving without
    // touching this field just resubmits the same URLs unchanged.
    urlsTextarea.value = (file.urls || []).join('\n');
    // Carried forward unchanged unless the (SuperAdmin/Admin-only) upload
    // control below replaces it -- this is what lets anyone save a Site
    // Name/Logo edit without needing to touch the Python file at all.
    uploadedFileName = file.pythonFilePath;
    currentFileNameEl.textContent = file.pythonFilePath;
    currentFileNote.classList.remove('hidden');
    Shared.openModal(modal);
  }

  async function handleUrlsCsvUpload(file) {
    if (!file) return;
    urlsCsvInput.disabled = true;
    urlsSpinner.classList.remove('hidden');
    urlsStatus.textContent = 'Uploading… please wait';
    urlsStatus.className = 'text-slate-500';
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('/api/files/parse-urls', {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
        body: formData,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        urlsStatus.textContent = data.error || 'Unable to process that CSV.';
        urlsStatus.className = 'text-rose-600';
        return;
      }
      urlsTextarea.value = data.urls.join('\n');
      urlsStatus.textContent = `Imported ${data.urls.length} URL(s) from the CSV -- review the list above before saving.`;
      urlsStatus.className = 'text-emerald-600';
    } catch (err) {
      urlsStatus.textContent = 'Network error during upload.';
      urlsStatus.className = 'text-rose-600';
    } finally {
      urlsCsvInput.disabled = false;
      urlsSpinner.classList.add('hidden');
    }
  }

  async function handleScriptUpload(file) {
    if (!file) return;
    uploadInput.disabled = true;
    uploadSpinner.classList.remove('hidden');
    uploadStatus.textContent = 'Uploading… please wait';
    uploadStatus.className = 'text-[11px] text-slate-500';
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('/api/files/upload-script', {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
        body: formData,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        uploadStatus.textContent = data.error || 'Upload failed.';
        uploadStatus.className = 'text-[11px] text-rose-600';
        return;
      }
      uploadedFileName = data.fileName;
      uploadStatus.textContent = `Uploaded: ${data.fileName}`;
      uploadStatus.className = 'text-[11px] text-emerald-600';
    } catch (err) {
      uploadStatus.textContent = 'Network error during upload.';
      uploadStatus.className = 'text-[11px] text-rose-600';
    } finally {
      uploadInput.disabled = false;
      uploadSpinner.classList.add('hidden');
    }
  }

  function setSubmitLoading(isLoading, idleLabel) {
    submitBtn.disabled = isLoading;
    submitSpinner.classList.toggle('hidden', !isLoading);
    submitLabel.textContent = isLoading ? 'Processing…' : idleLabel;
  }

  // --- Per-field validation feedback: red outline (stays until fixed) + a
  // one-shot shake (replayed by removing/re-adding the class, since a CSS
  // animation won't restart just by the class already being present). ---
  function markFieldError(el) {
    if (!el) return;
    el.classList.add('field-error');
    el.classList.remove('field-shake');
    void el.offsetWidth; // force reflow so the animation can replay
    el.classList.add('field-shake');
  }

  function clearFieldError(el) {
    if (el) el.classList.remove('field-error', 'field-shake');
  }

  // Clears a field's error state as soon as the user starts fixing it,
  // rather than leaving the red outline until the next submit attempt.
  [siteNameInput, urlsTextarea].forEach((el) => {
    el.addEventListener('input', () => clearFieldError(el));
  });
  uploadInput?.addEventListener('change', () => clearFieldError(uploadInput));

  async function handleFormSubmit(event) {
    event.preventDefault();
    Shared.hideError(modalError);
    clearFieldError(siteNameInput);
    clearFieldError(urlsTextarea);
    clearFieldError(uploadInput);

    const id = idInput.value;
    const idleLabel = submitLabel.textContent;

    let hasError = false;
    if (!siteNameInput.value.trim()) {
      markFieldError(siteNameInput);
      hasError = true;
    }
    if (!urlsTextarea.value.trim()) {
      markFieldError(urlsTextarea);
      hasError = true;
    }
    if (!uploadedFileName) {
      markFieldError(uploadInput);
      hasError = true;
    }
    if (hasError) {
      Shared.showError(modalError, 'Please fix the highlighted field(s) below.');
      return;
    }

    const payload = {
      siteName: siteNameInput.value.trim(),
      urlsText: urlsTextarea.value,
      pythonFilePath: uploadedFileName,
      logo: logoInput.value.trim(),
    };

    setSubmitLoading(true, idleLabel);
    try {
      const response = await fetch(id ? `/api/files/${id}` : '/api/files', {
        method: id ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to save scraper.';
        Shared.showError(modalError, message);
        Shared.showToast(message, 'error');
        // The client-side checks above catch empty fields before a request
        // is even sent -- a field-level rejection reaching this point means
        // the server found something the quick client check couldn't (e.g.
        // an invalid URL, or a taken Python file path), so map it back to
        // the right field by a simple keyword match on the error text.
        const lower = message.toLowerCase();
        if (lower.includes('url')) markFieldError(urlsTextarea);
        else if (lower.includes('site name')) markFieldError(siteNameInput);
        else if (lower.includes('python') || lower.includes('file')) markFieldError(uploadInput);
        return;
      }
      Shared.closeModal(modal);
      Shared.showToast(id ? 'Scraper updated successfully.' : 'Scraper registered successfully.', 'success');
      await loadFiles();
    } catch (err) {
      Shared.showError(modalError, 'Network error. Please try again.');
      Shared.showToast('Network error. Please try again.', 'error');
    } finally {
      setSubmitLoading(false, idleLabel);
    }
  }

  async function handleDeleteConfirm() {
    if (!pendingDeleteId) return;
    Shared.hideError(deleteError);
    deleteConfirmBtn.disabled = true;
    try {
      const response = await fetch(`/api/files/${pendingDeleteId}`, {
        method: 'DELETE',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to delete scraper.';
        Shared.showError(deleteError, message);
        Shared.showToast(message, 'error');
        return;
      }
      Shared.closeModal(deleteModal);
      pendingDeleteId = null;
      Shared.showToast('Scraper and its Python file were deleted.', 'success');
      await loadFiles();
    } catch (err) {
      Shared.showError(deleteError, 'Network error. Please try again.');
      Shared.showToast('Network error. Please try again.', 'error');
    } finally {
      deleteConfirmBtn.disabled = false;
    }
  }

  // --- Start / Stop ---
  async function startFile(fileId) {
    inFlightStarts.set(fileId, 'start');
    table.draw(false);
    try {
      const response = await fetch(`/api/files/${fileId}/start`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success) {
        Shared.showToast(data.error || 'Unable to start scraper.', 'error');
        return;
      }
      Shared.showToast('Scraper started successfully.', 'success');
    } catch (err) {
      Shared.showToast('Network error while starting the scraper.', 'error');
    } finally {
      inFlightStarts.delete(fileId);
      // loadFiles() skips its own rebuild when the fetched data is unchanged
      // (e.g. a failed start/stop leaves `working` exactly as it was) -- draw
      // here regardless, so the "Starting…"/"Stopping…" label always clears
      // instead of getting stuck if that fetch happens to see no data change.
      table.draw(false);
      await loadFiles({ silent: true });
    }
  }

  async function stopFile(fileId) {
    inFlightStarts.set(fileId, 'stop');
    table.draw(false);
    try {
      const response = await fetch(`/api/files/${fileId}/stop`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.success) {
        Shared.showToast((data && data.message) || 'Unable to stop scraper.', 'error');
        return;
      }
      Shared.showToast('Scraper stopped.', 'success');
    } catch (err) {
      Shared.showToast('Network error while stopping the scraper.', 'error');
    } finally {
      inFlightStarts.delete(fileId);
      // loadFiles() skips its own rebuild when the fetched data is unchanged
      // (e.g. a failed start/stop leaves `working` exactly as it was) -- draw
      // here regardless, so the "Starting…"/"Stopping…" label always clears
      // instead of getting stuck if that fetch happens to see no data change.
      table.draw(false);
      await loadFiles({ silent: true });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTable();

    newBtn.addEventListener('click', openCreateModal);
    refreshBtn.addEventListener('click', () => loadFiles());
    form.addEventListener('submit', handleFormSubmit);
    deleteConfirmBtn.addEventListener('click', handleDeleteConfirm);

    uploadInput?.addEventListener('change', () => handleScriptUpload(uploadInput.files[0]));
    urlsCsvInput?.addEventListener('change', () => handleUrlsCsvUpload(urlsCsvInput.files[0]));

    $(tableEl.tBodies[0]).on('click', 'button[data-action]', function () {
      const btn = this;
      if (btn.disabled) return;
      const action = btn.getAttribute('data-action');
      const id = Number(btn.getAttribute('data-id'));
      const file = filesById.get(id);
      if (!file) return;

      if (action === 'start') { startFile(id); return; }
      if (action === 'stop') { stopFile(id); return; }
      if (action === 'edit') { openEditModal(file); return; }
      if (action === 'view-urls') { openUrlsModal(file); return; }
      if (action === 'delete') {
        pendingDeleteId = id;
        deleteText.textContent = `This permanently deletes "${file.siteName}" and its file ${file.pythonFilePath} from the server.`;
        Shared.hideError(deleteError);
        Shared.openModal(deleteModal);
      }
    });

    loadMe().then(loadFiles);
  });
})();

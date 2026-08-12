// --- DOM element references used throughout this file ---
const stopButton = document.getElementById('stop-scraper');
const downloadButton = document.getElementById('download-report');
const statusElement = document.getElementById('scraper-status');
const runningCountElement = document.getElementById('running-count');
const urlStatusList = document.getElementById('url-status-list'); // <ul> that holds the root/child URL tree
const urlSummaryElement = document.getElementById('url-summary'); // pending/running/blocked/done counters
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percentage');

// Holds the setInterval id used to poll /scraper-status while the scraper is running; null when not polling.
let statusIntervalId = null;

// Hide the download link until a completed run makes an output file available.
if (downloadButton) {
  downloadButton.style.display = 'none';
}

// Stops the periodic /scraper-status polling loop (called on stop/finish).
const stopStatusPolling = () => {
  if (statusIntervalId !== null) {
    clearInterval(statusIntervalId);
    statusIntervalId = null;
  }
};

// Starts polling /scraper-status every 3s (no-op if already polling).
const startStatusPolling = () => {
  if (statusIntervalId === null) {
    statusIntervalId = setInterval(refreshStatus, 3000);
  }
};

// Updates the small status pill (e.g. "Running" / "Idle" / "Finished") and its color classes.
const setStatus = (text, classes) => {
  if (!statusElement) return;
  statusElement.textContent = text;
  statusElement.className = `ml-2 py-0.2 px-1 border-rounded-2x1 ${classes}`;
};

// Enables/disables the Stop button and the download link based on the current scraper state,
// and hides the Scraper Input panel while a job is running (shown again once it stops/finishes).
const updateControls = (state) => {
  if (stopButton) {
    stopButton.disabled = !state.running;
    stopButton.style.display = state.running ? '' : 'none';
  }
  if (downloadButton) {
    downloadButton.href = state.outputAvailable ? '/download-output' : '#';
  }
  const inputSection = document.getElementById('scraper-input-section');
  if (inputSection) {
    inputSection.style.display = state.running ? 'none' : '';
  }
};

// Returns the SVG markup for a URL's status tick: spinning circle (running),
// green checkmark (done), red X (blocked), or a plain grey ring (pending/unknown).
const getStatusIcon = (status) => {
  switch (status) {
    case 'running':
      return `
        <svg class="icon-running" viewBox="0 0 50 50" width="22" height="22" aria-hidden="true">
          <circle cx="25" cy="25" r="20" fill="none" stroke="#f59e0b" stroke-width="4" stroke-linecap="round" stroke-dasharray="31.4 62.8" transform="rotate(-90 25 25)"></circle>
          <circle cx="25" cy="25" r="20" fill="none" stroke="#fb923c" stroke-width="4" stroke-linecap="round" stroke-dasharray="1 62.8" transform="rotate(-90 25 25)">
            <animateTransform attributeName="transform" type="rotate" values="0 25 25;360 25 25" dur="1s" repeatCount="indefinite" />
          </circle>
        </svg>
      `;
    case 'done':
      return `
        <svg class="icon-done" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <circle cx="12" cy="12" r="10" fill="#10b981" opacity="0.15" />
          <path d="M7 13.5l3 3 7-7" fill="none" stroke="#047857" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <animate attributeName="stroke-dasharray" from="0 20" to="20 0" dur="0.4s" fill="freeze" />
          </path>
        </svg>
      `;
    case 'blocked':
      return `
        <svg class="icon-blocked" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <circle cx="12" cy="12" r="10" fill="#fecaca" />
          <path d="M9 9l6 6M15 9l-6 6" fill="none" stroke="#b91c1c" stroke-width="2.5" stroke-linecap="round">
            <animate attributeName="opacity" values="0;1;1" dur="0.4s" fill="freeze" />
          </path>
        </svg>
      `;
    default:
      return `
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <circle cx="12" cy="12" r="9" fill="none" stroke="#94a3b8" stroke-width="2" />
        </svg>
      `;
  }
};

// Small button that copies `url` to the clipboard; `size` lets root vs child rows use different padding.
const copyButton = (url, size = 'p-2') => `
  <button class="btncopy flex items-center justify-center rounded-xl border border-slate-200 bg-white ${size} text-slate-500 transition hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-600 cursor-pointer" type="button" data-url="${url}" title="Copy URL" aria-label="Copy URL">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M8 8V5C8 3.89543 8.89543 3 10 3H19C20.1046 3 21 3.89543 21 5V14C21 15.1046 20.1046 16 19 16H16"/> <rect x="3" y="8" width="13" height="13" rx="2"/>
    </svg>
  </button>
`;

// Chevron arrow used on root rows to expand/collapse their child (product) list.
const chevronIcon = (expanded) => `
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="transition-transform duration-200 ${expanded ? 'rotate-90' : ''}">
    <polyline points="9 6 15 12 9 18"></polyline>
  </svg>
`;

// Root URLs (categories / directly-submitted product URLs) whose product tree is expanded.
const expandedRoots = new Set();

// Small pill badge that labels a child row as "Pagination" (listing page) or "Product".
const typeTag = (type) => {
  if (type === 'listing') {
    return '<span class="inline-flex shrink-0 items-center rounded-full bg-indigo-100 px-2 py-0.5 text-[11px] font-medium text-indigo-700">Pagination</span>';
  }
  if (type === 'product') {
    return '<span class="inline-flex shrink-0 items-center rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-500">Product</span>';
  }
  return '';
};

// Turns the flat `statuses` list from the backend into a tree: each root URL
// (a category/directly-submitted URL, i.e. no parent or its own parent) gets
// a `children` array of the sub-URLs (pagination/product pages) it owns.
// Any child whose parent can't be found (e.g. parent not yet reported) is
// kept as an "orphan" root so it still renders instead of being dropped.
const buildUrlTree = (statuses) => {
  const roots = new Map();
  const children = [];

  statuses.forEach((item) => {
    const isRoot = !item.parent || item.parent === item.url;
    if (isRoot) {
      roots.set(item.url, { ...item, children: [] });
    } else {
      children.push(item);
    }
  });

  const orphans = [];
  children.forEach((item) => {
    const root = roots.get(item.parent);
    if (root) {
      root.children.push(item);
    } else {
      orphans.push(item);
    }
  });

  return [...roots.values(), ...orphans.map((item) => ({ ...item, children: [] }))];
};

// Renders one sub-URL (child) row: status tick (done/running/blocked/pending) + url + copy button.
const renderChildRow = (item) => {
  // Bug fix: was reading the undefined global `status` instead of this item's own status,
  // so every sub-URL showed the same (blank) tick regardless of done/running/blocked state.
  const status = (item.status || 'pending').toLowerCase();
  return `
    <li class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2.5">
        <div class="mt-0.5">${getStatusIcon(status)}</div>
      <div class="min-w-0 flex-1 flex items-center justify-between gap-3">
        <div class="min-w-0 flex items-center gap-2">
          <p class="break-all text-sm text-slate-600">${item.url}</p>
          ${typeTag(item.type)}
        </div>
        <div class="flex shrink-0 items-center gap-2">
          ${copyButton(item.url, 'p-1.5')}
        </div>
      </div>
    </li>
  `;
};

// Renders one root node (a directly-submitted URL): toggle chevron, status tick,
// "x/y products done" badge, copy button, and (if expanded) its list of child rows.
const renderRootNode = (root) => {
  const status = (root.status || 'pending').toLowerCase();
  const hasChildren = root.children.length > 0;
  const expanded = hasChildren && expandedRoots.has(root.url);
  const doneCount = root.children.filter((c) => (c.status || '').toLowerCase() === 'done').length;

  return `
    <li class="rounded-2xl border border-slate-200 overflow-hidden">
      <div class="flex items-start gap-3 px-4 py-3">
        ${hasChildren
      ? `<button type="button" class="tree-toggle mt-0.5 flex items-center justify-center rounded-lg p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 cursor-pointer" data-url="${root.url}" aria-expanded="${expanded}" aria-label="Toggle product list">${chevronIcon(expanded)}</button>`
      : '<span class="w-[26px] shrink-0"></span>'}
        <div class="mt-0.5">${getStatusIcon(status)}</div>
        <div class="min-w-0 flex-1 flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="break-all text-sm font-medium text-slate-700">${root.url}</p>
            ${hasChildren ? `<span class="mt-1 inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">${doneCount}/${root.children.length} products done</span>` : ''}
          </div>
          <div class="flex shrink-0 items-center gap-2">
            ${copyButton(root.url)}
          </div>
        </div>
      </div>
      ${hasChildren ? `
        <ul class="child-list space-y-2 border-t border-slate-100 bg-slate-50/70 px-4 py-3 pl-9 sm:pl-12 ${expanded ? '' : 'hidden'}">
          ${root.children.map(renderChildRow).join('')}
        </ul>
      ` : ''}
    </li>
  `;
};

// Fetches the latest per-URL statuses from the backend, updates the summary
// counters + progress bar, and re-renders the root/child URL tree.
const refreshUrlStatuses = async () => {
  try {
    const response = await fetch('/scraper-url-statuses');
    if (!response.ok) throw new Error('Failed to fetch URL statuses');
    const data = await response.json();
    const statuses = data.statuses || [];
    const summary = data.summary || { pending: 0, running: 0, done: 0, blocked: 0 };

    const mainUrlDone = statuses.filter((s) => {
      const isRoot = s.type === 'root' || !s.parent || s.parent === s.url;
      return isRoot && (s.status || '').toLowerCase() === 'done';
    }).length;
    const subUrlDone = statuses.filter((s) => (s.status || '').toLowerCase() === 'done' && !(s.type === 'root' || !s.parent || s.parent === s.url)).length;

    if (urlSummaryElement) {
      urlSummaryElement.innerHTML = `
        <span class="rounded-full bg-slate-100 px-3 py-1">Pending: <strong>${summary.pending}</strong></span>
        <span class="rounded-full bg-amber-100 px-3 py-1 text-amber-700">Running: <strong>${summary.running}</strong></span>
        <span class="rounded-full bg-rose-100 px-3 py-1 text-rose-700">Blocked: <strong>${summary.blocked}</strong></span>
        <span class="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">Main URL Done: <strong>${mainUrlDone}</strong></span>
        <span class="rounded-full bg-emerald-100 px-3 py-1 text-emerald-700">Product URL Done: <strong>${subUrlDone}</strong></span>
      `;
    }

    const total = summary.pending + summary.running + summary.done + summary.blocked;
    const percent = total ? Math.round((summary.done + summary.blocked) / total * 100) : 0;
    if (progressBar) {
      progressBar.style.width = `${percent}%`;
    }
    if (progressPercentage) {
      progressPercentage.textContent = `${percent}%`;
      if (percent === 100 && downloadButton) {
        downloadButton.style.removeProperty('display');
      }
    }

    if (!urlStatusList) return;

    if (!statuses.length) {
      urlStatusList.innerHTML = '<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">No URLs have been reported yet.</li>';
      return;
    }

    const tree = buildUrlTree(statuses);
    urlStatusList.innerHTML = tree.map(renderRootNode).join('');
  } catch (error) {
    console.error(error);
  }
};

// Fetches the overall scraper run state (running/done/idle), updates the
// status pill + Start/Stop/Download controls, and refreshes the URL tree.
// Called on load, after Start/Stop, and every 3s while `statusIntervalId` is set.
const refreshStatus = async () => {
  try {
    const response = await fetch('/scraper-status');
    if (!response.ok) throw new Error('Failed to fetch status');
    const state = await response.json();
    // console.log(state);

    if (state.running) {
      setStatus('Running', 'bg-emerald-100 text-emerald-700');
      startStatusPolling();
    } else if (state.done) {
      setStatus('Finished', 'bg-slate-100 text-slate-700');
      stopStatusPolling();

    } else {
      setStatus('Idle', 'bg-slate-100 text-slate-700');
    }

    updateControls(state);
    await refreshUrlStatuses();
  } catch (error) {
    console.error(error);
  }
};

// Copies `text` to the clipboard via the modern Clipboard API when available
// (requires a secure context), falling back to the legacy hidden-textarea +
// document.execCommand('copy') trick for http/older browsers.
const copyTextToClipboard = async (text) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();

  try {
    const successful = document.execCommand('copy');
    if (!successful) throw new Error('execCommand copy failed');
  } finally {
    document.body.removeChild(textarea);
  }
};

let toastHideTimeout = null;
// Shows a brief bottom-of-screen toast (lazily creating the element on first use)
// and auto-hides it after ~1.8s.
const showToast = (message) => {
  let toast = document.getElementById('copy-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'copy-toast';
    toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 z-50 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-lg opacity-0 transition-opacity duration-300 pointer-events-none';
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.classList.remove('opacity-0');
  toast.classList.add('opacity-100');

  clearTimeout(toastHideTimeout);
  toastHideTimeout = setTimeout(() => {
    toast.classList.remove('opacity-100');
    toast.classList.add('opacity-0');
  }, 1800);
};

// Clears the summary/progress bar/URL tree back to their empty state after the scraper is stopped.
const resetScraperUI = () => {
  if (urlSummaryElement) {
    urlSummaryElement.innerHTML = '';
  }
  if (progressBar) {
    progressBar.style.width = '0%';
  }
  if (progressPercentage) {
    progressPercentage.textContent = '0%';

  }
  if (urlStatusList) {
    urlStatusList.innerHTML = '<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">Scraper stopped. Click Start to begin again.</li>';
  }
};

// Stop button: calls /stop-scraper, then resets the UI and stops polling on success.
if (stopButton) {
  stopButton.addEventListener('click', async (e) => {
    e.preventDefault();
    stopButton.disabled = true;

    try {
      const response = await fetch('/stop-scraper', { method: 'POST' });
      if (!response.ok) throw new Error('Failed to stop scraper');
      const result = await response.json();
      if (!result.stopped) {
        throw new Error(result.message || 'Unable to stop scraper');
      }
      setStatus('Stopped', 'bg-rose-100 text-rose-700');
      resetScraperUI();
      stopStatusPolling();
    } catch (error) {
      console.error(error);
      alert(error.message || 'Unable to stop scraper.');
    } finally {
      await refreshStatus();
    }
  });
}

// ---------------------------------------------------------------------------
// Scraper Input: Upload CSV | Upload JSON | Enter URL, with an "Analyze URLs"
// preview step before anything actually starts scraping. The backend alone
// decides which scraper handles which URL (see detect_scraper_type in
// scrapers/scraper_config.py) -- this UI only ever shows what the backend
// already decided, it never sends a scraper choice of its own.
// ---------------------------------------------------------------------------
const inputTabButtons = document.querySelectorAll('[data-input-tab]');
const inputPanels = document.querySelectorAll('[data-input-panel]');
const inputErrorBox = document.getElementById('input-error-box');
const previewSection = document.getElementById('preview-section');
const previewTableBody = document.getElementById('preview-table-body');
const previewSkippedNote = document.getElementById('preview-skipped-note');
const analyzeUrlsButton = document.getElementById('analyze-urls-btn');
const urlPasteTextarea = document.getElementById('url-paste-textarea');
const analyzeJsonButton = document.getElementById('analyze-json-btn');
const jsonPasteTextarea = document.getElementById('json-paste-textarea');
const startScrapingButton = document.getElementById('start-scraping-btn');

// Remembers exactly what was last analyzed so "Start Scraping" can resubmit
// the identical input (file or pasted text/JSON) rather than trying to
// serialize the already-parsed preview rows back into a request.
let lastAnalyzedSource = null; // { kind: 'file', file: File } | { kind: 'text', text: string } | { kind: 'json-text', text: string }

const showInputError = (message) => {
  if (!inputErrorBox) return;
  if (!message) {
    inputErrorBox.classList.add('hidden');
    inputErrorBox.textContent = '';
    return;
  }
  inputErrorBox.textContent = message;
  inputErrorBox.classList.remove('hidden');
};

const scraperLabel = (scraperFile) => (scraperFile || '').replace(/\.py$/i, '');

// Escapes a value pulled from user-supplied input (the URL itself) before it
// is inserted as innerHTML -- a "URL" is otherwise free-form text as far as
// the browser is concerned, so this is the only thing standing between a
// crafted row and stored/reflected XSS in the preview table.
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (ch) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[ch]));

const renderPreview = (data) => {
  const entries = data.entries || [];
  const errors = data.errors || [];
  const unsupported = data.unsupported || [];

  if (!entries.length) {
    previewSection?.classList.add('hidden');
  } else if (previewSection && previewTableBody) {
    previewTableBody.innerHTML = entries.map((entry, index) => `
      <tr>
        <td class="px-4 py-2 text-slate-500">${index + 1}</td>
        <td class="px-4 py-2 break-all text-slate-700">${escapeHtml(entry.url)}</td>
        <td class="px-4 py-2"><span class="inline-flex items-center rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700">${escapeHtml(entry.type)}</span></td>
        <td class="px-4 py-2 text-slate-500">${escapeHtml(scraperLabel(entry.scraper))}</td>
      </tr>
    `).join('');

    const skippedCount = errors.length + unsupported.length;
    if (previewSkippedNote) {
      previewSkippedNote.textContent = skippedCount
        ? `${skippedCount} row(s) skipped -- see message below`
        : '';
    }
    previewSection.classList.remove('hidden');
  }

  showInputError(data.message || '');
};

// Sends the currently-selected input (file or pasted text) to `endpoint`
// (either /api/scraper/analyze for a preview, or /StartScraper to actually
// launch the job) using the same request shape for both.
const submitScraperInput = async (endpoint, source) => {
  let response;
  if (source.kind === 'file') {
    const formData = new FormData();
    formData.append('file', source.file);
    response = await fetch(endpoint, { method: 'POST', body: formData });
  } else {
    const bodyKey = source.kind === 'json-text' ? 'json' : 'text';
    response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ [bodyKey]: source.text }),
    });
  }
  const data = await response.json().catch(() => ({}));
  return { ok: response.ok, status: response.status, data };
};

const analyzeSource = async (source) => {
  showInputError('');
  previewSection?.classList.add('hidden');
  lastAnalyzedSource = source;

  try {
    const { ok, data } = await submitScraperInput('/api/scraper/analyze', source);
    if (!ok) {
      showInputError(data.error || 'Unable to analyze the submitted URLs.');
      return;
    }
    renderPreview(data);
  } catch (error) {
    console.error(error);
    showInputError('Network error while analyzing URLs.');
  }
};

// --- Tab switching ---
inputTabButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const tab = button.dataset.inputTab;
    inputTabButtons.forEach((b) => b.classList.toggle('is-active', b === button));
    inputPanels.forEach((panel) => panel.classList.toggle('hidden', panel.dataset.inputPanel !== tab));
  });
});

// --- Upload CSV / Upload JSON: drag-and-drop + "Choose File", per panel ---
document.querySelectorAll('[data-dropzone]').forEach((zone) => {
  const fileInput = zone.querySelector('[data-file-input]');
  const chooseBtn = zone.querySelector('[data-choose-file]');
  const filenameLabel = zone.querySelector('[data-dropzone-filename]');
  const accept = zone.dataset.accept;

  const handleFile = (file) => {
    if (!file) return;
    if (accept && !file.name.toLowerCase().endsWith(accept)) {
      showInputError(`Please choose a ${accept} file.`);
      return;
    }
    if (filenameLabel) filenameLabel.textContent = file.name;
    analyzeSource({ kind: 'file', file });
  };

  chooseBtn?.addEventListener('click', () => fileInput?.click());
  fileInput?.addEventListener('change', () => handleFile(fileInput.files[0]));

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('is-dragover');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('is-dragover'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('is-dragover');
    handleFile(e.dataTransfer.files[0]);
  });
});

// --- Enter URL: "Analyze URLs" button ---
if (analyzeUrlsButton) {
  analyzeUrlsButton.addEventListener('click', () => {
    const text = (urlPasteTextarea?.value || '').trim();
    if (!text) {
      showInputError('Paste at least one URL first.');
      return;
    }
    analyzeSource({ kind: 'text', text });
  });
}

// --- Upload JSON: "Analyze JSON" button (pasted JSON, as an alternative to the file upload above) ---
if (analyzeJsonButton) {
  analyzeJsonButton.addEventListener('click', () => {
    const text = (jsonPasteTextarea?.value || '').trim();
    if (!text) {
      showInputError('Paste some JSON first.');
      return;
    }
    analyzeSource({ kind: 'json-text', text });
  });
}

// --- Start Scraping: resubmits the last-analyzed input to /StartScraper ---
if (startScrapingButton) {
  startScrapingButton.addEventListener('click', async () => {
    if (!lastAnalyzedSource) {
      showInputError('Analyze your URLs first.');
      return;
    }

    startScrapingButton.disabled = true;
    try {
      const { ok, status, data } = await submitScraperInput('/StartScraper', lastAnalyzedSource);
      if (!ok) {
        if (status === 409) {
          showInputError('A scraper job is already running.');
        } else {
          showInputError(data.error || 'Unable to start the scraper.');
        }
        return;
      }

      showInputError('');
      previewSection?.classList.add('hidden');
      setStatus('Running', 'bg-emerald-100 text-emerald-700');
      startStatusPolling();
      await refreshStatus();
    } catch (error) {
      console.error(error);
      showInputError('Network error while starting the scraper.');
    } finally {
      startScrapingButton.disabled = false;
    }
  });
}

// Event delegation: handles clicks on any copy button inside the URL tree (root or child rows),
// since rows are re-rendered/replaced on every refresh and can't hold their own listeners.
if (urlStatusList) {
  urlStatusList.addEventListener('click', async (e) => {
    const button = e.target.closest('.btncopy');
    if (!button) return;

    const url = button.dataset.url;
    try {
      await copyTextToClipboard(url);

      if (!button.dataset.originalHtml) {
        button.dataset.originalHtml = button.innerHTML;
        button.dataset.originalClass = button.className;
      }

      const sizeClass = button.classList.contains('p-1.5') ? 'p-1.5' : 'p-2';
      button.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      `;
      button.className = `btncopy flex items-center justify-center rounded-xl border border-emerald-500 bg-emerald-500 ${sizeClass} text-white transition cursor-pointer`;
      button.title = 'Copied!';

      showToast('URL copied to clipboard');

      clearTimeout(button._resetTimeout);
      button._resetTimeout = setTimeout(() => {
        button.innerHTML = button.dataset.originalHtml;
        button.className = button.dataset.originalClass;
        button.title = 'Copy URL';
      }, 1500);
    } catch (error) {
      console.error('Failed to copy URL', error);
      showToast('Failed to copy URL');
    }
  });
}

// Event delegation: handles clicks on a root row's chevron to expand/collapse its child list,
// tracking expanded state in `expandedRoots` so it survives the next refreshUrlStatuses() re-render.
if (urlStatusList) {
  urlStatusList.addEventListener('click', (e) => {
    const toggle = e.target.closest('.tree-toggle');
    if (!toggle) return;

    const url = toggle.dataset.url;
    const expanded = expandedRoots.has(url);

    if (expanded) {
      expandedRoots.delete(url);
    } else {
      expandedRoots.add(url);
    }

    toggle.setAttribute('aria-expanded', String(!expanded));
    toggle.innerHTML = chevronIcon(!expanded);

    const childList = toggle.closest('li').querySelector('.child-list');
    if (childList) {
      childList.classList.toggle('hidden', expanded);
    }
  });
}

// Initial load: populate status pill, controls, and URL tree as soon as the page has the list element.
if (urlStatusList) {
  refreshStatus();
}


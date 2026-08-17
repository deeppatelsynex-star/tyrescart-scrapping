// --- DOM element references used throughout this file ---
const stopButton = document.getElementById('stop-scraper');
const downloadButton = document.getElementById('download-report');
const statusElement = document.getElementById('scraper-status');
const runningCountElement = document.getElementById('running-count');
const urlStatusList = document.getElementById('url-status-list'); // <ul> that holds the root/child URL tree
const urlSummaryElement = document.getElementById('url-summary'); // pending/running/blocked/done counters
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percentage');
const fileScraperSwitcher = document.getElementById('file-scraper-switcher');
const fileScraperNameEl = document.getElementById('file-scraper-name');
const fileScraperSelect = document.getElementById('file-scraper-select');

// When the page is opened as /?fileId=<id> (redirected here from a "Start"
// click on the /files page), watch that registered scraper's own live
// status instead of this browser session's ad-hoc /StartScraper job -- the
// two run through entirely separate engines (see CLAUDE.md), so this page
// just points its existing polling/rendering at a different data source
// rather than merging the two.
//
// The chosen fileId is remembered in localStorage (not just the URL query
// string) so that navigating to another page and back -- including via the
// sidebar's plain "/" link, which drops ?fileId -- keeps watching the same
// still-running scraper instead of this page silently falling back to the
// (idle) ad-hoc session state and looking like the scraper got stopped.
const FILE_SCRAPER_STORAGE_KEY = 'activeFileScraperId';
let fileScraperId = new URLSearchParams(window.location.search).get('fileId');
if (!fileScraperId) {
  fileScraperId = localStorage.getItem(FILE_SCRAPER_STORAGE_KEY) || null;
}
if (fileScraperId) {
  localStorage.setItem(FILE_SCRAPER_STORAGE_KEY, fileScraperId);
}
// Called once a watched file scraper is confirmed no longer running (finished,
// stopped, or its registration no longer exists) so a later page visit goes
// back to normal idle instead of re-watching a job that's already over.
const forgetFileScraper = () => {
  localStorage.removeItem(FILE_SCRAPER_STORAGE_KEY);
};
let fileScraperCsrfToken = null;

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

// Enables/disables the Stop button and the download link based on the current scraper state.
const updateControls = (state) => {
  if (stopButton) {
    stopButton.disabled = !state.running;
    stopButton.style.display = state.running ? '' : 'none';
  }
  if (downloadButton) {
    const downloadUrl = fileScraperId ? `/api/files/${fileScraperId}/download` : '/download-output';
    // Visibility tracks the *current* state on every poll, not just a one-way
    // reveal at 100% -- otherwise the link from a previously-finished job
    // stays visible (and clickable, pointing at stale output) once a new job
    // starts back at 0%.
    if (state.outputAvailable) {
      downloadButton.href = downloadUrl;
      downloadButton.style.removeProperty('display');
    } else {
      downloadButton.href = '#';
      downloadButton.style.display = 'none';
    }
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
    return '<span class="inline-flex shrink-0 items-center rounded-full bg-indigo-100 border border-indigo-200/80 px-2.5 py-0.5 text-xs font-semibold text-indigo-800">Pagination</span>';
  }
  if (type === 'product') {
    return '<span class="inline-flex shrink-0 items-center rounded-full bg-slate-100 border border-slate-200 px-2.5 py-0.5 text-xs font-semibold text-slate-700">Product</span>';
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
  let status = (item.status || 'pending').toLowerCase();
  // When scraper is not actively running, never show spinning running animation
  if (!isCurrentRunning && status === 'running') {
    status = 'pending';
  }
  const isXlsx = !!item.written_to_xlsx;
  return `
    <li class="flex items-start gap-3 rounded-xl border border-slate-200/90 bg-white px-3.5 py-2.5 shadow-2xs">
      <div class="mt-0.5 shrink-0">${getStatusIcon(status)}</div>
      <div class="min-w-0 flex-1 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div class="min-w-0 flex flex-wrap items-center gap-2">
          <p class="break-all text-sm sm:text-base font-normal text-slate-800">${item.url}</p>
          ${typeTag(item.type)}
          ${isXlsx ? '<span class="inline-flex shrink-0 items-center rounded-full bg-emerald-100 border border-emerald-300 px-2.5 py-0.5 text-xs font-bold text-emerald-800">Written to XLSX</span>' : ''}
        </div>
        <div class="flex shrink-0 items-center gap-2">
          ${copyButton(item.url, 'p-1.5')}
        </div>
      </div>
    </li>
  `;
};

let isCurrentRunning = false;

// Renders one root node (a directly-submitted URL): toggle chevron, status tick,
// "x/y products done" badge, copy button, and (if expanded) its list of child rows.
const renderRootNode = (root) => {
  let status = (root.status || 'pending').toLowerCase();
  const hasChildren = root.children && root.children.length > 0;
  const expanded = hasChildren && expandedRoots.has(root.url);
  const doneCount = hasChildren ? root.children.filter((c) => (c.status || '').toLowerCase() === 'done').length : 0;
  const blockedCount = hasChildren ? root.children.filter((c) => (c.status || '').toLowerCase() === 'blocked').length : 0;

  if (isCurrentRunning) {
    // While scraper is actively running:
    // If all sub-URLs are not done yet, show root in running mode with spinner
    if (hasChildren) {
      const allChildrenFinished = root.children.every((c) => {
        const s = (c.status || '').toLowerCase();
        return s === 'done' || s === 'blocked';
      });
      if (!allChildrenFinished || status === 'running') {
        status = 'running';
      } else if (allChildrenFinished) {
        status = 'done';
      }
    }
  } else {
    // When scraper is STOPPED or FINISHED (not running):
    // Never show spinning running animation on any URL!
    if (status === 'running') {
      status = (doneCount > 0 || (root.status || '').toLowerCase() === 'done') ? 'done' : 'pending';
    } else if (hasChildren) {
      const allChildrenFinished = root.children.every((c) => {
        const s = (c.status || '').toLowerCase();
        return s === 'done' || s === 'blocked';
      });
      if (allChildrenFinished || (root.status || '').toLowerCase() === 'done' || doneCount > 0) {
        status = 'done';
      }
    }
  }

  return `
    <li class="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-2xs">
      <div class="flex items-start gap-3.5 px-4 sm:px-5 py-3.5">
        ${hasChildren
      ? `<button type="button" class="tree-toggle mt-0.5 flex items-center justify-center rounded-lg p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-700 cursor-pointer" data-url="${root.url}" aria-expanded="${expanded}" aria-label="Toggle product list">${chevronIcon(expanded)}</button>`
      : '<span class="w-[26px] shrink-0"></span>'}
        <div class="mt-0.5 shrink-0">${getStatusIcon(status)}</div>
        <div class="min-w-0 flex-1 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="break-all text-sm sm:text-base font-bold text-slate-900 leading-snug">${root.url}</p>
            ${hasChildren ? `<span class="mt-1.5 inline-flex items-center rounded-full bg-slate-100 border border-slate-200/90 px-3 py-0.5 text-xs sm:text-sm font-semibold text-slate-700">${doneCount}/${root.children.length} products done</span>` : ''}
          </div>
          <div class="flex shrink-0 items-center gap-2">
            ${copyButton(root.url)}
          </div>
        </div>
      </div>
      ${hasChildren ? `
        <ul class="child-list space-y-2 border-t border-slate-100 bg-slate-50/80 px-4 sm:px-5 py-3.5 pl-9 sm:pl-14 ${expanded ? '' : 'hidden'}">
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
    const endpoint = fileScraperId ? `/api/files/${fileScraperId}/url-statuses` : '/scraper-url-statuses';
    const response = await fetch(endpoint);
    if (!response.ok) throw new Error('Failed to fetch URL statuses');
    const data = await response.json();
    const statuses = data.statuses || [];
    const summary = data.summary || { pending: 0, running: 0, done: 0, blocked: 0 };
    const xlsxCount = Number(data.xlsx_count || 0);

    const totalProductUrls = statuses.filter((s) => !(s.type === 'root' || !s.parent || s.parent === s.url)).length;
    const totalMainUrls = statuses.filter((s) => (s.type === 'root' || !s.parent || s.parent === s.url)).length;

    const mainUrlDone = statuses.filter((s) => {
      const isRoot = s.type === 'root' || !s.parent || s.parent === s.url;
      return isRoot && (s.status || '').toLowerCase() === 'done';
    }).length;
    const subUrlDone = statuses.filter((s) => (s.status || '').toLowerCase() === 'done' && !(s.type === 'root' || !s.parent || s.parent === s.url)).length;

    if (urlSummaryElement) {
      const totalBadge = totalProductUrls > 0
        ? `<span class="rounded-full bg-indigo-50 border border-indigo-200 px-3.5 py-1.5 text-xs sm:text-sm text-indigo-800 font-semibold shadow-2xs">Total Product URLs: <strong class="text-indigo-950 font-bold">${totalProductUrls}</strong></span>`
        : `<span class="rounded-full bg-indigo-50 border border-indigo-200 px-3.5 py-1.5 text-xs sm:text-sm text-indigo-800 font-semibold shadow-2xs">Total URLs: <strong class="text-indigo-950 font-bold">${totalMainUrls}</strong></span>`;

      const xlsxBadge = xlsxCount > 0
        ? `<span class="rounded-full bg-teal-50 border border-teal-200 px-3.5 py-1.5 text-xs sm:text-sm text-teal-800 font-bold shadow-2xs">Written to XLSX: <strong class="text-teal-950 font-extrabold">${xlsxCount}</strong></span>`
        : '';

      urlSummaryElement.innerHTML = `
        ${totalBadge}
        ${xlsxBadge}
        <span class="rounded-full bg-slate-100 border border-slate-200 px-3.5 py-1.5 text-xs sm:text-sm text-slate-700 font-semibold shadow-2xs">Pending: <strong class="text-slate-900 font-bold">${summary.pending}</strong></span>
        <span class="rounded-full bg-amber-50 border border-amber-200 px-3.5 py-1.5 text-xs sm:text-sm text-amber-800 font-semibold shadow-2xs">Running: <strong class="text-amber-950 font-bold">${summary.running}</strong></span>
        <span class="rounded-full bg-rose-50 border border-rose-200 px-3.5 py-1.5 text-xs sm:text-sm text-rose-800 font-semibold shadow-2xs">Blocked: <strong class="text-rose-950 font-bold">${summary.blocked}</strong></span>
        <span class="rounded-full bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 text-xs sm:text-sm text-emerald-800 font-semibold shadow-2xs">Main URL Done: <strong class="text-emerald-950 font-bold">${mainUrlDone}</strong></span>
        <span class="rounded-full bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 text-xs sm:text-sm text-emerald-800 font-semibold shadow-2xs">Product URL Done: <strong class="text-emerald-950 font-bold">${subUrlDone}</strong></span>
      `;
    }

    const total = summary.pending + summary.running + summary.done + summary.blocked;
    const percent = total ? Math.round((summary.done + summary.blocked) / total * 100) : 0;
    if (progressBar) {
      progressBar.style.width = `${percent}%`;
    }
    if (progressPercentage) {
      progressPercentage.textContent = `${percent}%`;
    }

    if (!urlStatusList) return;

    if (!statuses.length) {
      if (isCurrentRunning) {
        urlStatusList.innerHTML = `
          <li class="rounded-2xl border border-amber-200 bg-amber-50/80 p-5 text-sm text-amber-900 flex items-start gap-3.5 shadow-xs">
            <svg class="w-5 h-5 animate-spin text-amber-600 shrink-0 mt-0.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <div class="space-y-1">
              <p class="font-semibold text-amber-900">Scraper is running. Please wait…</p>
              <p class="text-xs text-amber-700">The scraper script is initializing, connecting to the target website, and discovering product URLs.</p>
            </div>
          </li>
        `;
      } else {
        urlStatusList.innerHTML = '<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">No URLs have been reported yet.</li>';
      }
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
    const endpoint = fileScraperId ? `/api/files/${fileScraperId}/status` : '/scraper-status';
    const response = await fetch(endpoint);
    if (!response.ok) {
      // The watched scraper's registration is gone (e.g. deleted from
      // /files while this page was open elsewhere) -- stop chasing it.
      if (fileScraperId && response.status === 404) {
        forgetFileScraper();
        stopStatusPolling();
        setStatus('Idle', 'bg-slate-100 text-slate-700');
        return;
      }
      throw new Error('Failed to fetch status');
    }
    const rawState = await response.json();
    // Since this page is only ever reached this way right after a Start
    // click, "not running" always means it already finished (rather than
    // "never started") -- treat that as done so the status pill reads
    // "Finished" and polling actually stops.
    const state = fileScraperId
      ? { running: rawState.running, done: !rawState.running, outputAvailable: !!rawState.outputAvailable }
      : rawState;

    if (fileScraperSwitcher) {
      if (fileScraperId && rawState.siteName) {
        fileScraperNameEl.textContent = `Scraper: ${rawState.siteName}`;
        fileScraperSwitcher.classList.remove('hidden');
      } else {
        fileScraperSwitcher.classList.add('hidden');
      }
    }

    isCurrentRunning = !!state.running;

    if (state.running) {
      setStatus('Running', 'bg-emerald-100 text-emerald-700');
      startStatusPolling();
      if (window.IDBStorage && fileScraperId) {
        window.IDBStorage.setWorkingState(fileScraperId, true, { siteName: rawState.siteName });
      }
    } else if (state.done) {
      setStatus('Finished', 'bg-slate-100 text-slate-700');
      stopStatusPolling();
      if (fileScraperId) {
        if (window.IDBStorage) window.IDBStorage.setWorkingState(fileScraperId, false);
        forgetFileScraper();
      }
    } else {
      setStatus('Idle', 'bg-slate-100 text-slate-700');
      if (fileScraperId && window.IDBStorage) {
        window.IDBStorage.setWorkingState(fileScraperId, false);
      }
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

// Fetches a CSRF token for the file-scoped stop call below -- this page
// normally never needs one (/stop-scraper doesn't require it), but
// /api/files/<id>/stop does, same as every other mutating /api/files/* route.
const ensureFileScraperCsrfToken = async () => {
  if (fileScraperCsrfToken || !fileScraperId) return fileScraperCsrfToken;
  try {
    const response = await fetch('/api/me');
    if (response.ok) {
      const data = await response.json();
      fileScraperCsrfToken = data.csrfToken;
    }
  } catch (error) {
    console.error(error);
  }
  return fileScraperCsrfToken;
};
if (fileScraperId) ensureFileScraperCsrfToken();

if (downloadButton) {
  downloadButton.addEventListener('click', () => {
    if (window.AdminShared) {
      window.AdminShared.showToast('Starting report download…', 'info');
    }
  });
}



// Stop button: calls /stop-scraper (or, when watching a /files scraper,
// /api/files/<id>/stop), then resets the UI and stops polling on success.
if (stopButton) {
  stopButton.addEventListener('click', async (e) => {
    e.preventDefault();
    stopButton.disabled = true;
    if (window.AdminShared) {
      window.AdminShared.showToast('Stopping scraper… please wait', 'warning');
    }

    try {
      let response;
      if (fileScraperId) {
        const token = await ensureFileScraperCsrfToken();
        response = await fetch(`/api/files/${fileScraperId}/stop`, {
          method: 'POST',
          headers: { 'X-CSRF-Token': token },
        });
      } else {
        response = await fetch('/stop-scraper', { method: 'POST' });
      }
      if (!response.ok) throw new Error('Failed to stop scraper');
      const result = await response.json();
      const stopped = fileScraperId ? result.success : result.stopped;
      if (!stopped) {
        throw new Error(result.message || result.error || 'Unable to stop scraper');
      }
      isCurrentRunning = false;
      stopStatusPolling();
      setStatus('Stopped', 'bg-amber-100 text-amber-800 border border-amber-200 font-bold');
      resetScraperUI();
      if (window.AdminShared) {
        window.AdminShared.showToast('Scraper stopped successfully.', 'success');
      }
      if (fileScraperId) {
        if (window.IDBStorage) window.IDBStorage.setWorkingState(fileScraperId, false);
        forgetFileScraper();
      }
    } catch (error) {
      if (window.AdminShared) {
        window.AdminShared.logError('Stop Scraper Button', error, { fileScraperId });
        window.AdminShared.showToast(error.message || 'Unable to stop scraper.', 'error');
      } else {
        console.error('[TyresCart Scraper Error]:', error);
      }
    } finally {
      if (isCurrentRunning) {
        await refreshStatus();
      } else {
        stopButton.disabled = true;
        await refreshUrlStatuses();
      }
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

      if (window.AdminShared) {
        window.AdminShared.showToast('URL copied to clipboard!', 'success');
      } else {
        showToast('URL copied to clipboard');
      }

      clearTimeout(button._resetTimeout);
      button._resetTimeout = setTimeout(() => {
        button.innerHTML = button.dataset.originalHtml;
        button.className = button.dataset.originalClass;
        button.title = 'Copy URL';
      }, 1500);
    } catch (error) {
      if (window.AdminShared) {
        window.AdminShared.logError('Copy URL to Clipboard', error, { url });
        window.AdminShared.showToast('Failed to copy URL to clipboard.', 'error');
      } else {
        console.error('Failed to copy URL', error);
        showToast('Failed to copy URL');
      }
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


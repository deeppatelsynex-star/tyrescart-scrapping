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
    const endpoint = fileScraperId ? `/api/files/${fileScraperId}/url-statuses` : '/scraper-url-statuses';
    const response = await fetch(endpoint);
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
        refreshRunningFileScrapers();
      } else {
        fileScraperSwitcher.classList.add('hidden');
      }
    }

    if (state.running) {
      setStatus('Running', 'bg-emerald-100 text-emerald-700');
      startStatusPolling();
    } else if (state.done) {
      setStatus('Finished', 'bg-slate-100 text-slate-700');
      stopStatusPolling();
      if (fileScraperId) forgetFileScraper();

    } else {
      setStatus('Idle', 'bg-slate-100 text-slate-700');
    }

    updateControls(state);
    await refreshUrlStatuses();
  } catch (error) {
    console.error(error);
  }
};

// Populates the "switch to another running scraper" dropdown next to the
// site-name badge, so starting a second scraper from /files while this page
// is already watching one doesn't strand the first -- you can hop back to
// check on it without needing /files' table.
const refreshRunningFileScrapers = async () => {
  if (!fileScraperId || !fileScraperSelect) return;
  try {
    const response = await fetch('/api/files/running');
    if (!response.ok) return;
    const data = await response.json();
    const others = (data.files || []).filter((f) => String(f.fileId) !== String(fileScraperId));

    if (!others.length) {
      fileScraperSelect.classList.add('hidden');
      return;
    }

    fileScraperSelect.innerHTML = '';
    const currentOption = document.createElement('option');
    currentOption.value = String(fileScraperId);
    currentOption.textContent = 'Currently viewing';
    fileScraperSelect.appendChild(currentOption);
    others.forEach((f) => {
      const opt = document.createElement('option');
      opt.value = String(f.fileId);
      opt.textContent = f.siteName;
      fileScraperSelect.appendChild(opt);
    });
    fileScraperSelect.value = String(fileScraperId);
    fileScraperSelect.classList.remove('hidden');
  } catch (error) {
    console.error(error);
  }
};

if (fileScraperSelect) {
  fileScraperSelect.addEventListener('change', () => {
    const target = fileScraperSelect.value;
    if (target && target !== String(fileScraperId)) {
      window.location.href = `/?fileId=${target}`;
    }
  });
}

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

// Stop button: calls /stop-scraper (or, when watching a /files scraper,
// /api/files/<id>/stop), then resets the UI and stops polling on success.
if (stopButton) {
  stopButton.addEventListener('click', async (e) => {
    e.preventDefault();
    stopButton.disabled = true;

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
      setStatus('Stopped', 'bg-rose-100 text-rose-700');
      resetScraperUI();
      stopStatusPolling();
      if (fileScraperId) forgetFileScraper();
    } catch (error) {
      console.error(error);
      alert(error.message || 'Unable to stop scraper.');
    } finally {
      await refreshStatus();
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


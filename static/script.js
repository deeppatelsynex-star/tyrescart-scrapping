// ==============================================================================
// Scraper Live Progress Controller (with SSE Webhook Stream & User-Ownership)
// ==============================================================================

(function () {
  const urlStatusList = document.getElementById('url-status-list');
  const scraperBlockedScreen = document.getElementById('scraper-blocked-screen');
  const scraperMainContent = document.getElementById('scraper-main-content');

  // Only run this script if on the scraper live progress page
  if (!urlStatusList && !scraperBlockedScreen) {
    return;
  }

  const startButton = document.getElementById('start-scraper');
  const stopButton = document.getElementById('stop-scraper');
  const downloadButton = document.getElementById('download-report');
  const statusElement = document.getElementById('scraper-status');
  const urlSummaryElement = document.getElementById('url-summary');
  const progressBar = document.getElementById('progress-bar');
  const progressPercentage = document.getElementById('progress-percentage');
  const fileScraperSwitcher = document.getElementById('file-scraper-switcher');
  const fileScraperNameEl = document.getElementById('file-scraper-name');

  // Extract fileId from query parameters or resolve dynamically
  let fileScraperId = new URLSearchParams(window.location.search).get('fileId');

  let currentJobId = null;
  let isCurrentRunning = false;
  let statusIntervalId = null;
  let activeEventSource = null;
  let fileScraperCsrfToken = null;
  const collapsedRoots = new Set();
  const expandedRoots = new Set();

  const isRootExpanded = (rootUrl, childCount) => {
    if (expandedRoots.has(rootUrl)) return true;
    if (collapsedRoots.has(rootUrl)) return false;
    // Default: auto-expand small lists (<= 10 items); keep large lists (> 10 items) collapsed initially
    return childCount > 0 && childCount <= 10;
  };

  let lastKnownStatuses = [];

  const resolveFileScraperId = async () => {
    if (fileScraperId) return fileScraperId;
    try {
      const res = await fetch('/api/files?perPage=1');
      if (res.ok) {
        const data = await res.json();
        if (data.files && data.files.length > 0) {
          fileScraperId = String(data.files[0].fileId);
          try {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('fileId', fileScraperId);
            window.history.replaceState({}, '', newUrl);
          } catch (e) {}
          loadStateFromLocalStorage();
          return fileScraperId;
        }
      }
    } catch (e) {}
    return null;
  };

  const closeEventSource = () => {
    if (activeEventSource) {
      activeEventSource.close();
      activeEventSource = null;
    }
  };

  const stopStatusPolling = () => {
    if (statusIntervalId !== null) {
      clearInterval(statusIntervalId);
      statusIntervalId = null;
    }
  };

  const startStatusPolling = () => {
    if (statusIntervalId === null && !activeEventSource) {
      statusIntervalId = setInterval(refreshProgress, 3500);
    }
  };

  const setStatus = (text, classes) => {
    if (!statusElement) return;
    statusElement.textContent = text;
    statusElement.className = `ml-2 px-3 py-0.5 rounded-full font-bold ${classes}`;
  };

  const showBlockedScreen = () => {
    closeEventSource();
    if (scraperBlockedScreen) scraperBlockedScreen.classList.remove('hidden');
    if (scraperMainContent) scraperMainContent.classList.add('hidden');
  };

  const showMainProgress = () => {
    if (scraperBlockedScreen) scraperBlockedScreen.classList.add('hidden');
    if (scraperMainContent) scraperMainContent.classList.remove('hidden');
  };

  const updateControls = (state) => {
    const isRunning = state.status === 'RUNNING' || state.running === true;
    if (startButton) {
      startButton.disabled = isRunning;
      startButton.style.display = isRunning ? 'none' : 'inline-flex';
    }
    if (stopButton) {
      stopButton.disabled = !isRunning;
      stopButton.style.display = isRunning ? 'inline-flex' : 'none';
    }
    if (downloadButton) {
      const downloadUrl = fileScraperId ? `/api/files/${fileScraperId}/download` : '/download-output';
      if (state.output_available || state.outputAvailable) {
        downloadButton.href = downloadUrl;
        downloadButton.style.display = 'inline-flex';
      } else {
        downloadButton.href = '#';
        downloadButton.style.display = 'none';
      }
    }
  };

  const getStatusIcon = (status) => {
    const st = (status || '').toLowerCase();
    switch (st) {
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
      case 'success':
        return `
          <svg class="icon-done" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
            <circle cx="12" cy="12" r="10" fill="#10b981" opacity="0.15" />
            <path d="M7 13.5l3 3 7-7" fill="none" stroke="#047857" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <animate attributeName="stroke-dasharray" from="0 20" to="20 0" dur="0.4s" fill="freeze" />
            </path>
          </svg>
        `;
      case 'blocked':
      case 'failed':
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

  const copyButton = (url, size = 'p-2') => `
    <button class="btncopy flex items-center justify-center rounded-xl border border-slate-200 bg-white ${size} text-slate-500 transition hover:border-emerald-400 hover:bg-emerald-50 hover:text-emerald-600 cursor-pointer" type="button" data-url="${url}" title="Copy URL" aria-label="Copy URL">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M8 8V5C8 3.89543 8.89543 3 10 3H19C20.1046 3 21 3.89543 21 5V14C21 15.1046 20.1046 16 19 16H16"/> <rect x="3" y="8" width="13" height="13" rx="2"/>
      </svg>
    </button>
  `;

  const chevronIcon = (expanded) => `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="transition-transform duration-200 ${expanded ? 'rotate-90 text-emerald-600' : 'text-slate-500'}">
      <polyline points="9 6 15 12 9 18"></polyline>
    </svg>
  `;

  const typeTag = (type) => {
    if (type === 'listing') {
      return '<span class="inline-flex shrink-0 items-center rounded-full bg-indigo-100 border border-indigo-200/80 px-2.5 py-0.5 text-xs font-semibold text-indigo-800">Pagination</span>';
    }
    if (type === 'product') {
      return '<span class="inline-flex shrink-0 items-center rounded-full bg-slate-100 border border-slate-200 px-2.5 py-0.5 text-xs font-semibold text-slate-700">Product</span>';
    }
    return '';
  };

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

  const renderChildRow = (item) => {
    let status = (item.status || 'pending').toLowerCase();
    if (!isCurrentRunning && status === 'running') {
      status = 'pending';
    }
    const isXlsx = !!item.written_to_xlsx;
    return `
      <li class="child-url-item flex items-start gap-3 rounded-xl border border-slate-200/90 bg-white px-3.5 py-2.5 shadow-2xs transition-colors" data-url="${item.url}">
        <div class="mt-0.5 shrink-0 status-icon">${getStatusIcon(status)}</div>
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

  const renderRootNode = (root) => {
    let status = (root.status || 'pending').toLowerCase();
    const hasChildren = root.children && root.children.length > 0;
    const expanded = hasChildren && isRootExpanded(root.url, root.children.length);
    const doneCount = hasChildren ? root.children.filter((c) => (c.status || '').toLowerCase() === 'done').length : 0;

    if (isCurrentRunning) {
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
      <li class="root-url-item rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-2xs" data-url="${root.url}">
        <div class="root-header flex items-start gap-3.5 px-4 sm:px-5 py-3.5 ${hasChildren ? 'cursor-pointer hover:bg-slate-50/70 transition select-none' : ''}" data-url="${root.url}">
          ${hasChildren
        ? `<button type="button" class="tree-toggle mt-0.5 flex h-7 w-7 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-200/80 hover:text-slate-700 cursor-pointer transition" data-url="${root.url}" aria-expanded="${expanded}" aria-label="Toggle product list">${chevronIcon(expanded)}</button>`
        : '<span class="w-[28px] shrink-0"></span>'}
          <div class="mt-0.5 shrink-0 status-icon">${getStatusIcon(status)}</div>
          <div class="min-w-0 flex-1 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="min-w-0">
              <p class="break-all text-sm sm:text-base font-bold text-slate-900 leading-snug">${root.url}</p>
              ${hasChildren ? `<span class="mt-1.5 inline-flex items-center rounded-full bg-slate-100 border border-slate-200/90 px-3 py-0.5 text-xs sm:text-sm font-semibold text-slate-700 root-child-count">${doneCount}/${root.children.length} products done</span>` : ''}
            </div>
            <div class="flex shrink-0 items-center gap-2">
              ${copyButton(root.url)}
            </div>
          </div>
        </div>
        ${hasChildren ? `
          <ul class="child-list space-y-2 border-t border-slate-100 bg-slate-50/80 px-4 sm:px-5 py-3.5 pl-9 sm:pl-14 ${expanded ? '' : 'hidden'}">
            ${root.children.slice(0, 100).map(renderChildRow).join('')}
            ${root.children.length > 100 ? `<li class="rounded-xl border border-dashed border-slate-200 px-3.5 py-2.5 text-xs text-slate-500 text-center">… and <strong>${root.children.length - 100}</strong> more product URLs (${root.children.length} total)</li>` : ''}
          </ul>
        ` : ''}
      </li>
    `;
  };

  const renderSummaryPills = (state) => {
    if (!urlSummaryElement) return;

    const totalProducts = state.total_product_urls || state.total_products || 0;
    const totalUrls = state.total_urls || 0;
    const writtenToXlsx = state.written_to_xlsx || 0;
    const pending = state.pending || 0;
    const running = state.running_count !== undefined ? state.running_count : (state.running ? 1 : 0);
    const blocked = state.blocked || 0;
    const mainUrlDone = state.main_url_done || 0;
    const productUrlDone = state.product_url_done || 0;

    const totalBadge = totalProducts > 0
      ? `<span class="rounded-full bg-indigo-50 border border-indigo-200 px-3.5 py-1.5 text-xs sm:text-sm text-indigo-800 font-semibold shadow-2xs">Total Product URLs: <strong class="text-indigo-950 font-bold">${totalProducts}</strong></span>`
      : `<span class="rounded-full bg-indigo-50 border border-indigo-200 px-3.5 py-1.5 text-xs sm:text-sm text-indigo-800 font-semibold shadow-2xs">Total URLs: <strong class="text-indigo-950 font-bold">${totalUrls}</strong></span>`;

    const xlsxBadge = writtenToXlsx > 0
      ? `<span class="rounded-full bg-teal-50 border border-teal-200 px-3.5 py-1.5 text-xs sm:text-sm text-teal-800 font-bold shadow-2xs">Written to XLSX: <strong class="text-teal-950 font-extrabold">${writtenToXlsx}</strong></span>`
      : '';

    urlSummaryElement.innerHTML = `
      ${totalBadge}
      ${xlsxBadge}
      <span class="rounded-full bg-slate-100 border border-slate-200 px-3.5 py-1.5 text-xs sm:text-sm text-slate-700 font-semibold shadow-2xs">Pending: <strong class="text-slate-900 font-bold">${pending}</strong></span>
      <span class="rounded-full bg-amber-50 border border-amber-200 px-3.5 py-1.5 text-xs sm:text-sm text-amber-800 font-semibold shadow-2xs">Running: <strong class="text-amber-950 font-bold">${running}</strong></span>
      <span class="rounded-full bg-rose-50 border border-rose-200 px-3.5 py-1.5 text-xs sm:text-sm text-rose-800 font-semibold shadow-2xs">Blocked: <strong class="text-rose-950 font-bold">${blocked}</strong></span>
      <span class="rounded-full bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 text-xs sm:text-sm text-emerald-800 font-semibold shadow-2xs">Main URL Done: <strong class="text-emerald-950 font-bold">${mainUrlDone}</strong></span>
      <span class="rounded-full bg-emerald-50 border border-emerald-200 px-3.5 py-1.5 text-xs sm:text-sm text-emerald-800 font-semibold shadow-2xs">Product URL Done: <strong class="text-emerald-950 font-bold">${productUrlDone}</strong></span>
    `;

    const st = (state.status || '').toUpperCase();
    let pct = Math.min(100, Math.max(0, state.progress_percent || 0));
    if (st === 'SUCCESS') pct = 100;
    if (progressBar) progressBar.style.width = `${pct}%`;
    if (progressPercentage) progressPercentage.textContent = `${pct}%`;
  };

  const renderUrlTreeList = (statuses) => {
    if (!urlStatusList) return;
    lastKnownStatuses = statuses || [];

    if (!lastKnownStatuses.length) {
      if (isCurrentRunning) {
        urlStatusList.innerHTML = `
          <li class="rounded-2xl border border-amber-200 bg-amber-50/80 p-5 text-sm text-amber-900 flex items-start gap-3.5 shadow-xs">
            <svg class="w-5 h-5 animate-spin text-amber-600 shrink-0 mt-0.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <div class="space-y-1">
              <p class="font-semibold text-amber-900">Scraper is running. Please wait…</p>
              <p class="text-xs text-amber-700">The crawler is actively running on the server. URLs and progress will stream below.</p>
            </div>
          </li>
        `;
      } else {
        urlStatusList.innerHTML = '<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">No URLs have been reported yet.</li>';
      }
    } else {
      const tree = buildUrlTree(lastKnownStatuses);
      const MAX_ROOTS = 50;
      const visibleTree = tree.slice(0, MAX_ROOTS);
      const hidden = tree.length - visibleTree.length;
      const html = visibleTree.map(renderRootNode).join('');
      const moreHtml = hidden > 0
        ? `<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500 text-center">… and <strong>${hidden}</strong> more root URLs (total: ${tree.length})</li>`
        : '';
      urlStatusList.innerHTML = html + moreHtml;
    }
  };

  const updateUiState = (statusRes) => {
    if (!statusRes) return;
    if (fileScraperSwitcher && (statusRes.site_name || statusRes.siteName)) {
      fileScraperNameEl.textContent = `Scraper: ${statusRes.site_name || statusRes.siteName}`;
      fileScraperSwitcher.classList.remove('hidden');
    }

    const st = (statusRes.status || '').toUpperCase();
    isCurrentRunning = st === 'RUNNING' || statusRes.running === true;

    if (isCurrentRunning) {
      setStatus('Running', 'bg-emerald-100 text-emerald-700');
    } else if (st === 'STOPPED') {
      setStatus('Stopped', 'bg-amber-100 text-amber-800 border border-amber-200');
    } else if (st === 'SUCCESS' || statusRes.done) {
      setStatus('Finished', 'bg-emerald-50 text-emerald-800 border border-emerald-200');
    } else if (st === 'FAILED' || st === 'FAIL') {
      setStatus('Failed', 'bg-rose-100 text-rose-800 border border-rose-200');
    } else {
      setStatus('Idle', 'bg-slate-100 text-slate-700');
    }

    updateControls(statusRes);
    renderSummaryPills(statusRes);
  };

  // ==============================================================================
  // SSE Webhook Client (Real-time Push Stream)
  // ==============================================================================

  const getCacheKey = () => fileScraperId ? `tyrescart_scraper_cache_file_${fileScraperId}` : null;

  const saveStateToLocalStorage = (summary, statuses) => {
    const key = getCacheKey();
    if (!key) return;
    try {
      const data = {
        summary: summary || {},
        statuses: (statuses && statuses.length) ? statuses : (lastKnownStatuses || []),
        timestamp: Date.now(),
      };
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.warn('[LocalStorage] Save failed:', e);
    }
  };

  const loadStateFromLocalStorage = () => {
    const key = getCacheKey();
    if (!key) return false;
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return false;
      const data = JSON.parse(raw);
      if (data && data.summary) {
        updateUiState(data.summary);
        if (Array.isArray(data.statuses) && data.statuses.length > 0) {
          renderUrlTreeList(data.statuses);
        }
        return true;
      }
    } catch (e) {
      console.warn('[LocalStorage] Load failed:', e);
    }
    return false;
  };

  const startEventSource = (jobId) => {
    if (!jobId || (activeEventSource && activeEventSource._jobId === jobId)) {
      return;
    }
    closeEventSource();
    stopStatusPolling();

    try {
      const es = new EventSource(`/api/scraper/job/${jobId}/events`);
      es._jobId = jobId;
      activeEventSource = es;

      es.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          handleSsePayload(payload);
        } catch (err) {
          console.error('[SSE Parse Error]:', err);
        }
      };

      es.onerror = () => {
        closeEventSource();
        startStatusPolling();
      };
    } catch (e) {
      console.warn('[SSE Connection Failed, falling back to polling]:', e);
      startStatusPolling();
    }
  };

  let treeRenderTimeout = null;
  let lastTreeRenderTime = 0;
  const TREE_RENDER_THROTTLE_MS = 1000;

  const scheduleThrottledTreeRender = () => {
    const now = Date.now();
    const elapsed = now - lastTreeRenderTime;
    if (elapsed >= TREE_RENDER_THROTTLE_MS) {
      lastTreeRenderTime = now;
      if (treeRenderTimeout) {
        clearTimeout(treeRenderTimeout);
        treeRenderTimeout = null;
      }
      renderUrlTreeList(lastKnownStatuses);
    } else if (!treeRenderTimeout) {
      treeRenderTimeout = setTimeout(() => {
        lastTreeRenderTime = Date.now();
        treeRenderTimeout = null;
        renderUrlTreeList(lastKnownStatuses);
      }, TREE_RENDER_THROTTLE_MS - elapsed);
    }
  };

  const updateUrlItemInPlace = (item) => {
    if (!urlStatusList || !item || !item.url) return false;
    try {
      const escapedUrl = CSS.escape(item.url);
      const el = urlStatusList.querySelector(`[data-url="${escapedUrl}"]`);
      if (!el) return false;
      const statusIcon = el.querySelector('.status-icon');
      if (statusIcon) {
        statusIcon.innerHTML = getStatusIcon((item.status || 'pending').toLowerCase());
      }
      return true;
    } catch (e) {
      return false;
    }
  };

  const handleSsePayload = (payload) => {
    if (!payload) return;

    if (payload.type === 'snapshot') {
      updateUiState(payload.summary || {});
      renderUrlTreeList(payload.statuses || []);
      saveStateToLocalStorage(payload.summary || {}, payload.statuses || []);
    } else if (payload.type === 'url_update') {
      updateUiState(payload.summary || {});
      if (payload.url) {
        const idx = lastKnownStatuses.findIndex((u) => u.url === payload.url.url);
        if (idx >= 0) {
          lastKnownStatuses[idx] = payload.url;
          // In-place update: 0ms, 0 flicker, never destroys copy button or resets expanded state
          const updatedInPlace = updateUrlItemInPlace(payload.url);
          if (!updatedInPlace) {
            scheduleThrottledTreeRender();
          }
        } else {
          lastKnownStatuses.push(payload.url);
          scheduleThrottledTreeRender();
        }
        saveStateToLocalStorage(payload.summary || {}, lastKnownStatuses);
      }
    } else if (payload.type === 'status') {
      const st = (payload.status || '').toUpperCase();
      updateUiState(payload);
      saveStateToLocalStorage(payload, lastKnownStatuses);
      if (payload.done || ['SUCCESS', 'STOPPED', 'FAILED', 'FAIL'].includes(st)) {
        if (treeRenderTimeout) {
          clearTimeout(treeRenderTimeout);
          treeRenderTimeout = null;
        }
        renderUrlTreeList(lastKnownStatuses);
        closeEventSource();
        stopStatusPolling();
        refreshProgress();
      }
    }
  };

  // ==============================================================================
  // Fallback Polling / Initial Loader
  // ==============================================================================

  const refreshProgress = async () => {
    try {
      if (fileScraperId) {
        const activeRes = await fetch(`/api/scraper/file/${fileScraperId}/active-job`);
        if (activeRes.ok) {
          const activeInfo = await activeRes.json();
          if (activeInfo.already_running && !activeInfo.is_owner) {
            showBlockedScreen();
            closeEventSource();
            stopStatusPolling();
            return;
          }

          showMainProgress();
          currentJobId = activeInfo.job_id || null;
          const isRunning = Boolean(activeInfo.has_active_job && activeInfo.job_id);

          const statusEndpoint = currentJobId
            ? `/api/scraper/job/${currentJobId}/status`
            : `/api/files/${fileScraperId}/status`;
          const urlsEndpoint = currentJobId
            ? `/api/scraper/job/${currentJobId}/urls`
            : `/api/files/${fileScraperId}/url-statuses`;

          const [statusRes, urlsRes] = await Promise.all([
            fetch(statusEndpoint).then((r) => (r.ok ? r.json() : null)),
            fetch(urlsEndpoint).then((r) => (r.ok ? r.json() : null)),
          ]);

          if (statusRes) {
            updateUiState(statusRes);
            const statuses = Array.isArray(urlsRes)
              ? urlsRes
              : urlsRes && Array.isArray(urlsRes.statuses)
              ? urlsRes.statuses
              : [];
            renderUrlTreeList(statuses);
            saveStateToLocalStorage(statusRes, statuses);
          } else {
            const rawStatus = activeInfo.status || (isRunning ? 'RUNNING' : 'IDLE');
            setStatus(isRunning ? 'Running' : (rawStatus === 'STOPPED' ? 'Stopped' : 'Idle'), isRunning ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700');
            updateControls({ running: isRunning, status: rawStatus });
          }

          if (isRunning) {
            startEventSource(currentJobId);
          } else {
            closeEventSource();
            stopStatusPolling();
          }
          return;
        }
      }

      if (!currentJobId && !fileScraperId) {
        stopStatusPolling();
        closeEventSource();
        setStatus('Idle', 'bg-slate-100 text-slate-700');
        return;
      }

      const statusEndpoint = currentJobId
        ? `/api/scraper/job/${currentJobId}/status`
        : `/api/files/${fileScraperId}/status`;

      const urlsEndpoint = currentJobId
        ? `/api/scraper/job/${currentJobId}/urls`
        : `/api/files/${fileScraperId}/url-statuses`;

      const [statusRes, urlsRes] = await Promise.all([
        fetch(statusEndpoint).then((r) => (r.ok ? r.json() : null)),
        fetch(urlsEndpoint).then((r) => (r.ok ? r.json() : null)),
      ]);

      if (!statusRes) {
        stopStatusPolling();
        closeEventSource();
        setStatus('Idle', 'bg-slate-100 text-slate-700');
        return;
      }

      updateUiState(statusRes);

      const statuses = Array.isArray(urlsRes)
        ? urlsRes
        : urlsRes && Array.isArray(urlsRes.statuses)
        ? urlsRes.statuses
        : [];
      renderUrlTreeList(statuses);
      saveStateToLocalStorage(statusRes, statuses);

      if (isCurrentRunning && currentJobId) {
        startEventSource(currentJobId);
        startStatusPolling();
      } else {
        closeEventSource();
        stopStatusPolling();
      }
    } catch (error) {
      console.error('[TyresCart Scraper Refresh Error]:', error);
    }
  };

  const ensureFileScraperCsrfToken = async () => {
    if (fileScraperCsrfToken) return fileScraperCsrfToken;
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

  if (startButton) {
    startButton.addEventListener('click', async () => {
      if (!fileScraperId) {
        await resolveFileScraperId();
      }
      if (!fileScraperId) return;
      startButton.disabled = true;
      startButton.innerHTML = '<span>Starting…</span>';
      if (window.AdminShared) {
        window.AdminShared.showToast('Starting scraper… please wait', 'info');
      }

      try {
        const token = await ensureFileScraperCsrfToken();
        const res = await fetch(`/api/files/${fileScraperId}/start`, {
          method: 'POST',
          headers: { 'X-CSRF-Token': token },
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || !data.success) {
          const errMsg = data.message || data.error || 'Unable to start scraper.';
          if (window.AdminShared) window.AdminShared.showToast(errMsg, 'warning');
          await refreshProgress();
          return;
        }
        if (window.AdminShared) window.AdminShared.showToast('Scraper started successfully!', 'success');
        currentJobId = data.job_id;
        setStatus('Running', 'bg-emerald-100 text-emerald-700');
        updateControls({ running: true, status: 'RUNNING' });
        startEventSource(currentJobId);
        startStatusPolling();
        await refreshProgress();
      } catch (err) {
        if (window.AdminShared) window.AdminShared.showToast('Failed to start scraper.', 'error');
      } finally {
        if (startButton) {
          startButton.disabled = false;
          startButton.innerHTML = `
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            <span class="ml-2">Start Scraper</span>
          `;
        }
      }
    });
  }

  if (stopButton) {
    stopButton.addEventListener('click', async (e) => {
      e.preventDefault();
      if (!confirm('Are you sure you want to stop this scraper?')) {
        return;
      }
      stopButton.disabled = true;
      if (window.AdminShared) {
        window.AdminShared.showToast('Stopping scraper… please wait', 'warning');
      }

      try {
        const token = await ensureFileScraperCsrfToken();
        let stopEndpoint;
        if (currentJobId) {
          stopEndpoint = `/api/scraper/job/${currentJobId}/stop`;
        } else if (fileScraperId) {
          stopEndpoint = `/api/files/${fileScraperId}/stop`;
        } else {
          stopEndpoint = '/stop-scraper';
        }

        const response = await fetch(stopEndpoint, {
          method: 'POST',
          headers: { 'X-CSRF-Token': token },
        });

        if (!response.ok) throw new Error('Failed to stop scraper');
        const result = await response.json();

        isCurrentRunning = false;
        closeEventSource();
        stopStatusPolling();
        setStatus('Stopped', 'bg-amber-100 text-amber-800 border border-amber-200');
        updateControls({ running: false, status: 'STOPPED' });

        if (window.AdminShared) {
          window.AdminShared.showToast('Scraper stopped successfully.', 'success');
        }
      } catch (error) {
        if (window.AdminShared) {
          window.AdminShared.logError('Stop Scraper Button', error, { fileScraperId, currentJobId });
          window.AdminShared.showToast(error.message || 'Unable to stop scraper.', 'error');
        }
      } finally {
        stopButton.disabled = true;
        await refreshProgress();
      }
    });
  }

  if (urlStatusList) {
    urlStatusList.addEventListener('click', async (e) => {
      const button = e.target.closest('.btncopy');
      if (!button) return;
      e.stopPropagation();

      const url = button.getAttribute('data-url') || button.dataset.url;
      if (!url) return;

      let copied = false;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(url);
          copied = true;
        }
      } catch (err) {
        copied = false;
      }

      if (!copied) {
        try {
          const textarea = document.createElement('textarea');
          textarea.value = url;
          textarea.style.position = 'fixed';
          textarea.style.top = '0';
          textarea.style.left = '0';
          textarea.style.opacity = '0';
          textarea.style.pointerEvents = 'none';
          document.body.appendChild(textarea);
          textarea.focus();
          textarea.select();
          copied = document.execCommand('copy');
          document.body.removeChild(textarea);
        } catch (err) {
          copied = false;
        }
      }

      if (copied) {
        if (!button.dataset.originalHtml) {
          button.dataset.originalHtml = button.innerHTML;
          button.dataset.originalClass = button.className;
        }

        button.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;
        button.className = 'btncopy flex items-center justify-center rounded-xl border border-emerald-500 bg-emerald-500 p-1.5 text-white transition cursor-pointer';
        button.title = 'Copied!';

        if (window.AdminShared && typeof window.AdminShared.showToast === 'function') {
          window.AdminShared.showToast('URL copied to clipboard!', 'success');
        }

        clearTimeout(button._resetTimeout);
        button._resetTimeout = setTimeout(() => {
          button.innerHTML = button.dataset.originalHtml;
          button.className = button.dataset.originalClass;
          button.title = 'Copy URL';
        }, 1500);
      } else {
        if (window.AdminShared && typeof window.AdminShared.showToast === 'function') {
          window.AdminShared.showToast('Failed to copy URL', 'error');
        }
      }
    });

    const toggleAllBtn = document.getElementById('toggle-all-urls');
    const toggleAllLabel = document.getElementById('toggle-all-label');

    if (toggleAllBtn) {
      toggleAllBtn.addEventListener('click', () => {
        const rootLis = urlStatusList.querySelectorAll('li.root-url-item');
        if (!rootLis.length) return;

        // Determine if we should collapse or expand based on current state
        const childLists = urlStatusList.querySelectorAll('.child-list');
        const anyVisible = Array.from(childLists).some((cl) => !cl.classList.contains('hidden'));
        const shouldCollapse = anyVisible;

        rootLis.forEach((rootLi) => {
          const childList = rootLi.querySelector('.child-list');
          if (!childList) return;
          const toggleBtn = rootLi.querySelector('.tree-toggle');
          const header = rootLi.querySelector('.root-header');
          const url = (header && header.dataset.url) || (toggleBtn && toggleBtn.dataset.url);

          if (shouldCollapse) {
            childList.classList.add('hidden');
            if (toggleBtn) {
              toggleBtn.setAttribute('aria-expanded', 'false');
              toggleBtn.innerHTML = chevronIcon(false);
            }
            if (url) {
              collapsedRoots.add(url);
              expandedRoots.delete(url);
            }
          } else {
            childList.classList.remove('hidden');
            if (toggleBtn) {
              toggleBtn.setAttribute('aria-expanded', 'true');
              toggleBtn.innerHTML = chevronIcon(true);
            }
            if (url) {
              expandedRoots.add(url);
              collapsedRoots.delete(url);
            }
          }
        });

        if (toggleAllLabel) {
          toggleAllLabel.textContent = shouldCollapse ? 'Expand All' : 'Collapse All';
        }
      });
    }

    urlStatusList.addEventListener('click', (e) => {
      // Don't toggle when clicking copy button, hyperlinks, or inputs
      if (e.target.closest('.btncopy') || e.target.closest('a') || e.target.closest('button:not(.tree-toggle)')) return;

      const headerOrToggle = e.target.closest('.tree-toggle') || e.target.closest('.root-header');
      if (!headerOrToggle) return;

      const rootLi = headerOrToggle.closest('li.root-url-item') || headerOrToggle.closest('li');
      if (!rootLi) return;

      const childList = rootLi.querySelector('.child-list');
      if (!childList) return;

      const toggleBtn = rootLi.querySelector('.tree-toggle');
      const url = (headerOrToggle.dataset && headerOrToggle.dataset.url) || (toggleBtn && toggleBtn.dataset.url);

      // Direct DOM state check: if currently hidden, we are expanding; if open, collapsing
      const isCurrentlyHidden = childList.classList.contains('hidden');
      const willBeExpanded = isCurrentlyHidden;

      if (willBeExpanded) {
        childList.classList.remove('hidden');
      } else {
        childList.classList.add('hidden');
      }

      if (toggleBtn) {
        toggleBtn.setAttribute('aria-expanded', String(willBeExpanded));
        toggleBtn.innerHTML = chevronIcon(willBeExpanded);
      }

      if (url) {
        if (willBeExpanded) {
          expandedRoots.add(url);
          collapsedRoots.delete(url);
        } else {
          collapsedRoots.add(url);
          expandedRoots.delete(url);
        }
      }
    });
  }

  // Initial bootstrap on /scraperpage
  const initPage = async () => {
    // 1. Immediately render default placeholders so UI is never blank
    renderSummaryPills({});
    renderUrlTreeList([]);
    updateControls({ running: false, status: 'IDLE' });

    // 2. Resolve scraper fileId if not in URL params
    if (!fileScraperId) {
      await resolveFileScraperId();
    }

    // 3. Preload cached state if available
    loadStateFromLocalStorage();

    // 4. Fetch live server progress
    await refreshProgress();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPage);
  } else {
    initPage();
  }
})();

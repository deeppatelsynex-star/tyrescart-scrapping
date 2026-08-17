// ==============================================================================
// Scraper Live Progress Controller (with User-Ownership & Global Lock Support)
// ==============================================================================

(function () {
  const urlStatusList = document.getElementById('url-status-list');
  const scraperBlockedScreen = document.getElementById('scraper-blocked-screen');
  const scraperMainContent = document.getElementById('scraper-main-content');

  // Only run this script if on the scraper live progress page
  if (!urlStatusList && !scraperBlockedScreen) {
    return;
  }

  const stopButton = document.getElementById('stop-scraper');
  const downloadButton = document.getElementById('download-report');
  const statusElement = document.getElementById('scraper-status');
  const urlSummaryElement = document.getElementById('url-summary');
  const progressBar = document.getElementById('progress-bar');
  const progressPercentage = document.getElementById('progress-percentage');
  const fileScraperSwitcher = document.getElementById('file-scraper-switcher');
  const fileScraperNameEl = document.getElementById('file-scraper-name');

  // Extract fileId strictly from query parameters (no cross-session localStorage)
  const fileScraperId = new URLSearchParams(window.location.search).get('fileId');

  let currentJobId = null;
  let isCurrentRunning = false;
  let statusIntervalId = null;
  let fileScraperCsrfToken = null;
  const expandedRoots = new Set();

  const stopStatusPolling = () => {
    if (statusIntervalId !== null) {
      clearInterval(statusIntervalId);
      statusIntervalId = null;
    }
  };

  const startStatusPolling = () => {
    if (statusIntervalId === null) {
      statusIntervalId = setInterval(refreshProgress, 2000);
    }
  };

  const setStatus = (text, classes) => {
    if (!statusElement) return;
    statusElement.textContent = text;
    statusElement.className = `ml-2 px-3 py-0.5 rounded-full font-bold ${classes}`;
  };

  const showBlockedScreen = () => {
    if (scraperBlockedScreen) scraperBlockedScreen.classList.remove('hidden');
    if (scraperMainContent) scraperMainContent.classList.add('hidden');
  };

  const showMainProgress = () => {
    if (scraperBlockedScreen) scraperBlockedScreen.classList.add('hidden');
    if (scraperMainContent) scraperMainContent.classList.remove('hidden');
  };

  const updateControls = (state) => {
    const isRunning = state.status === 'RUNNING' || state.running === true;
    if (stopButton) {
      stopButton.disabled = !isRunning;
      stopButton.style.display = isRunning ? '' : 'none';
    }
    if (downloadButton) {
      const downloadUrl = fileScraperId ? `/api/files/${fileScraperId}/download` : '/download-output';
      if (state.output_available || state.outputAvailable) {
        downloadButton.href = downloadUrl;
        downloadButton.style.removeProperty('display');
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
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="transition-transform duration-200 ${expanded ? 'rotate-90' : ''}">
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

  const renderRootNode = (root) => {
    let status = (root.status || 'pending').toLowerCase();
    const hasChildren = root.children && root.children.length > 0;
    const expanded = hasChildren && expandedRoots.has(root.url);
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

    const pct = Math.min(100, Math.max(0, state.progress_percent || 0));
    if (progressBar) progressBar.style.width = `${pct}%`;
    if (progressPercentage) progressPercentage.textContent = `${pct}%`;
  };

  const refreshProgress = async () => {
    try {
      if (fileScraperId) {
        const activeRes = await fetch(`/api/scraper/file/${fileScraperId}/active-job`);
        if (activeRes.ok) {
          const activeInfo = await activeRes.json();
          // If scraper is actively running by another user, show blocked screen and keep polling
          if (activeInfo.already_running && !activeInfo.is_owner) {
            showBlockedScreen();
            startStatusPolling();
            return;
          }

          // If not running by anyone, show idle screen
          if (!activeInfo.has_active_job) {
            showMainProgress();
            stopStatusPolling();
            setStatus('Idle', 'bg-slate-100 text-slate-700');
            updateControls({ running: false, status: 'IDLE' });
            return;
          }

          // Active job belongs to current user
          showMainProgress();
          currentJobId = activeInfo.job_id;
        }
      }

      if (!currentJobId && !fileScraperId) {
        stopStatusPolling();
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
        fetch(statusEndpoint).then((r) => r.ok ? r.json() : null),
        fetch(urlsEndpoint).then((r) => r.ok ? r.json() : null),
      ]);

      if (!statusRes) {
        stopStatusPolling();
        setStatus('Idle', 'bg-slate-100 text-slate-700');
        return;
      }

      if (fileScraperSwitcher && (statusRes.site_name || statusRes.siteName)) {
        fileScraperNameEl.textContent = `Scraper: ${statusRes.site_name || statusRes.siteName}`;
        fileScraperSwitcher.classList.remove('hidden');
      }

      const st = (statusRes.status || '').toUpperCase();
      isCurrentRunning = st === 'RUNNING' || statusRes.running === true;

      if (isCurrentRunning) {
        setStatus('Running', 'bg-emerald-100 text-emerald-700');
        startStatusPolling();
      } else if (st === 'STOPPED') {
        setStatus('Stopped', 'bg-amber-100 text-amber-800 border border-amber-200');
        stopStatusPolling();
      } else if (st === 'SUCCESS' || statusRes.done) {
        setStatus('Finished', 'bg-emerald-50 text-emerald-800 border border-emerald-200');
        stopStatusPolling();
      } else if (st === 'FAILED') {
        setStatus('Failed', 'bg-rose-100 text-rose-800 border border-rose-200');
        stopStatusPolling();
      } else {
        setStatus('Idle', 'bg-slate-100 text-slate-700');
        stopStatusPolling();
      }

      updateControls(statusRes);
      renderSummaryPills(statusRes);

      // Render URL Tree
      if (urlStatusList) {
        const statuses = (urlsRes && urlsRes.statuses) ? urlsRes.statuses : [];
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
                  <p class="text-xs text-amber-700">The crawler is actively running on the server. URLs and progress will appear below.</p>
                </div>
              </li>
            `;
          } else {
            urlStatusList.innerHTML = '<li class="rounded-2xl border border-dashed border-slate-200 px-4 py-3 text-sm text-slate-500">No URLs have been reported yet.</li>';
          }
        } else {
          const tree = buildUrlTree(statuses);
          urlStatusList.innerHTML = tree.map(renderRootNode).join('');
        }
      }
    } catch (error) {
      console.error('[TyresCart Scraper Polling Error]:', error);
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

  if (stopButton) {
    stopButton.addEventListener('click', async (e) => {
      e.preventDefault();
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

      const url = button.dataset.url;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(url);
        } else {
          const textarea = document.createElement('textarea');
          textarea.value = url;
          textarea.style.position = 'fixed';
          textarea.style.left = '-9999px';
          document.body.appendChild(textarea);
          textarea.focus();
          textarea.select();
          document.execCommand('copy');
          document.body.removeChild(textarea);
        }

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

        if (window.AdminShared) {
          window.AdminShared.showToast('URL copied to clipboard!', 'success');
        }

        clearTimeout(button._resetTimeout);
        button._resetTimeout = setTimeout(() => {
          button.innerHTML = button.dataset.originalHtml;
          button.className = button.dataset.originalClass;
          button.title = 'Copy URL';
        }, 1500);
      } catch (error) {
        if (window.AdminShared) {
          window.AdminShared.showToast('Failed to copy URL', 'error');
        }
      }
    });

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

  // Initial bootstrap on /scraperpage
  refreshProgress();
})();

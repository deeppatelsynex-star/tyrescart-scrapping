// SuperAdmin Scraping Reports page (/reports).
// Displays live and historical logs from logTbl of who triggered scraping, start/end times,
// URLs found, success/blocked counts, and records scraped.
(function () {
  const tableEl = document.getElementById('reports-table');
  if (!tableEl) return;

  const Shared = window.AdminShared;
  const errorEl = document.getElementById('reports-error');
  const loadingEl = document.getElementById('reports-loading');
  const refreshBtn = document.getElementById('reports-refresh-btn');
  const refreshIcon = document.getElementById('reports-refresh-icon');
  const statusFilterEl = document.getElementById('reports-status-filter');

  const statTotalRunsEl = document.getElementById('stat-total-runs');
  const statDataScrapedEl = document.getElementById('stat-data-scraped');
  const statPagesCrawledEl = document.getElementById('stat-pages-crawled');
  const statActiveRunsEl = document.getElementById('stat-active-runs');

  let table = null;
  let reports = [];
  let pollInterval = null;

  function userCellHtml(row) {
    const name = row.userName || 'Admin';
    const email = row.userEmail || '';
    const userId = row.userId ? `ID #${row.userId}` : '';
    const safeName = Shared.escapeHtml(name);
    const safeEmail = Shared.escapeHtml(email);
    const initial = (name.trim()[0] || 'U').toUpperCase();

    const avatarHtml = row.userAvatar
      ? `<img src="${Shared.escapeHtml(row.userAvatar)}" alt="" class="w-8 h-8 rounded-full object-cover border border-slate-200 shrink-0" onerror="this.replaceWith(Object.assign(document.createElement('span'),{className:'w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-semibold shrink-0',textContent:'${initial}'}))" />`
      : `<span class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-semibold shrink-0 border border-emerald-200">${initial}</span>`;

    return `
      <div class="flex items-center gap-3">
        ${avatarHtml}
        <div class="min-w-0">
          <div class="flex items-center gap-1.5">
            <span class="font-semibold text-slate-800 text-sm truncate">${safeName}</span>
            ${userId ? `<span class="inline-flex items-center rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-mono text-slate-500">${userId}</span>` : ''}
          </div>
          <div class="text-[11px] text-slate-400 truncate">${safeEmail}</div>
        </div>
      </div>
    `;
  }

  function scraperCellHtml(row) {
    const scraperName = row.scraper || row.siteName || 'Scraper';
    const safeSite = Shared.escapeHtml(scraperName);
    const safeScript = Shared.escapeHtml(row.pythonFilePath || '');
    return `
      <div>
        <div class="font-semibold text-slate-800 text-sm">${safeSite}</div>
        ${safeScript ? `<div class="font-mono text-[11px] text-slate-400 truncate max-w-[180px]">${safeScript}</div>` : ''}
      </div>
    `;
  }

  function statusBadgeHtml(row) {
    const st = (row.status || '').toUpperCase();
    switch (st) {
      case 'RUNNING':
        return `<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 border border-emerald-200/60"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>Running</span>`;
      case 'FINISHED':
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-100 text-sky-700 border border-sky-200/60">Finished</span>`;
      case 'STOPPED':
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 border border-amber-200/60">Stopped</span>`;
      case 'FAILED':
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-700 border border-rose-200/60">Failed</span>`;
      default:
        return `<span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">${st}</span>`;
    }
  }

  function actionsCellHtml(row) {
    const isRunning = (row.status || '').toUpperCase() === 'RUNNING';
    const viewLiveBtn = isRunning && row.fileId
      ? `<a href="/scraperpage?fileId=${row.fileId}" class="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:underline cursor-pointer">Live Progress</a>`
      : '';
    const downloadBtn = row.outputAvailable
      ? `<a href="/api/reports/${row.id}/download" class="inline-flex items-center gap-1 text-xs font-semibold text-emerald-600 hover:text-emerald-800 hover:underline cursor-pointer" title="Download report Excel">Download</a>`
      : '';

    return `
      <div class="flex items-center justify-end gap-3">
        ${viewLiveBtn}
        ${downloadBtn}
      </div>
    `;
  }

  function updateStatsCards(stats) {
    if (!stats) return;
    if (statTotalRunsEl) statTotalRunsEl.textContent = (stats.totalRuns || 0).toLocaleString();
    if (statDataScrapedEl) statDataScrapedEl.textContent = (stats.totalDataScraped || 0).toLocaleString();
    if (statPagesCrawledEl) statPagesCrawledEl.textContent = (stats.totalUrlsFound || 0).toLocaleString();
    if (statActiveRunsEl) statActiveRunsEl.textContent = (stats.activeRuns || 0).toLocaleString();
  }

  function initTable() {
    table = $(tableEl).DataTable(Shared.commonDataTableOptions({
      data: [],
      order: [[0, 'desc']], // newest run first
      language: {
        search: '',
        searchPlaceholder: 'Search by scraper, user, site…',
        lengthMenu: 'Show _MENU_ logs per page',
        info: 'Showing _START_ to _END_ of _TOTAL_ logs',
        infoEmpty: 'No scraping logs recorded yet',
        infoFiltered: '(filtered from _MAX_ total logs)',
        paginate: { first: 'First', last: 'Last', next: 'Next', previous: 'Previous' },
      },
      columns: [
        {
          data: 'id',
          className: 'font-mono text-xs text-slate-500 font-semibold',
          render: (data) => `#${data}`,
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? scraperCellHtml(row) : (row.scraper || '')),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? userCellHtml(row) : (row.userName || '')),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? Shared.dateTimeHtml(row.startTimeRaw) : (row.startTimeRaw || '')),
        },
        {
          data: null,
          render: (data, type, row) => {
            if (type === 'display') {
              return row.endTimeRaw
                ? Shared.dateTimeHtml(row.endTimeRaw)
                : '<span class="inline-flex items-center gap-1.5 text-xs text-emerald-600 font-semibold"><span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>Running</span>';
            }
            return row.endTimeRaw || '';
          },
        },
        {
          data: null,
          className: 'font-mono text-xs text-slate-700',
          render: (data, type, row) => (type === 'display' ? `<span class="font-semibold text-slate-700">${Shared.escapeHtml(row.duration || '—')}</span>` : (row.durationSeconds || 0)),
        },
        {
          data: 'noOfUrlFound',
          render: (data, type) => (type === 'display' ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200/60">${(data || 0).toLocaleString()}</span>` : (data || 0)),
        },
        {
          data: 'totalSuccessUrl',
          render: (data, type) => (type === 'display' ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">${(data || 0).toLocaleString()}</span>` : (data || 0)),
        },
        {
          data: 'totalBlockUrl',
          render: (data, type) => (type === 'display' ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200/60">${(data || 0).toLocaleString()}</span>` : (data || 0)),
        },
        {
          data: 'dataScraped',
          render: (data, type) => (type === 'display' ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200/60">${(data || 0).toLocaleString()} rows</span>` : (data || 0)),
        },
        {
          data: null,
          render: (data, type, row) => (type === 'display' ? statusBadgeHtml(row) : (row.status || '')),
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

  async function loadReports({ silent } = {}) {
    if (!silent) Shared.hideError(errorEl);
    if (refreshBtn) {
      refreshBtn.disabled = true;
      refreshIcon.classList.add('animate-spin');
    }

    try {
      const statusParam = statusFilterEl ? statusFilterEl.value : '';
      const url = `/api/reports?perPage=200${statusParam ? `&status=${encodeURIComponent(statusParam)}` : ''}`;
      const response = await fetch(url);
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const msg = data.error || 'Failed to load scraper logs.';
        Shared.showError(errorEl, msg);
        if (!silent) Shared.showToast(msg, 'error');
        return;
      }

      reports = data.reports || [];
      updateStatsCards(data.stats);

      table.clear();
      table.rows.add(reports);
      table.draw(false);

      // If active runs exist, ensure polling is running
      if (data.stats && data.stats.activeRuns > 0) {
        startPolling();
      } else {
        stopPolling();
      }
    } catch (err) {
      Shared.logError('Reports Module Fetch', err);
      Shared.showError(errorEl, 'Network error while loading logs.');
      if (!silent) Shared.showToast('Network error while loading logs.', 'error');
    } finally {
      showTable();
      if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshIcon.classList.remove('animate-spin');
      }
    }
  }

  function startPolling() {
    if (!pollInterval) {
      pollInterval = setInterval(() => {
        loadReports({ silent: true });
      }, 5000);
    }
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTable();

    refreshBtn?.addEventListener('click', () => {
      Shared.showToast('Refreshing scraper audit logs…', 'info');
      loadReports();
    });

    statusFilterEl?.addEventListener('change', () => {
      const val = statusFilterEl.value;
      Shared.showToast(val ? `Filtering logs: ${val}` : 'Showing all logs', 'info');
      loadReports();
    });

    $(tableEl.tBodies[0]).on('click', 'a[href*="/download"]', function () {
      Shared.showToast('Starting report download…', 'info');
    });

    loadReports();
  });
})();

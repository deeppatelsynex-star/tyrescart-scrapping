// global-search.js - VisionAdmin CMS Fast Command Search & Autocomplete
(function() {
  'use strict';

  let selectedIndex = -1;
  let currentResults = [];
  let searchDebounceTimeout = null;
  let latestQuery = '';

  const RECENT_SEARCHES_KEY = 'va_recent_searches';
  const DEFAULT_RECENT = ['About Us', 'Privacy Policy', 'Blog', 'Sections'];

  // Initialize Search Component
  function initGlobalSearch() {
    const container = document.getElementById('va-global-search-container');
    const input = document.getElementById('va-global-search-input');
    const dropdown = document.getElementById('va-global-search-dropdown');
    const resultsBox = document.getElementById('va-global-search-results');
    const footer = document.getElementById('va-global-search-footer');
    const footerText = document.getElementById('va-global-search-footer-text');
    const clearBtn = document.getElementById('va-global-search-clear');

    if (!input || !dropdown || !resultsBox) return;

    // 1. Input event handlers (5-second debounce after user stops typing)
    input.addEventListener('input', () => {
      const query = input.value.trim();
      if (clearBtn) {
        if (query.length > 0) {
          clearBtn.classList.remove('hidden');
        } else {
          clearBtn.classList.add('hidden');
        }
      }
      
      clearTimeout(searchDebounceTimeout);
      if (!query) {
        performSearch('');
      } else {
        renderTypingState(query);
        searchDebounceTimeout = setTimeout(() => {
          performSearch(query);
        }, 5000); // 5 seconds of inactivity before calling backend API
      }
    });

    input.addEventListener('focus', () => {
      const query = input.value.trim();
      if (!query) {
        performSearch('');
      }
    });

    // 2. Clear Button Handler
    if (clearBtn) {
      clearBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        clearTimeout(searchDebounceTimeout);
        input.value = '';
        clearBtn.classList.add('hidden');
        input.focus();
        performSearch('');
      });
    }

    // 3. Keyboard Shortcut (Ctrl+K / Cmd+K) & Navigation Handlers
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
        e.preventDefault();
        input.focus();
        input.select();
        if (!input.value.trim()) {
          performSearch('');
        }
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        clearTimeout(searchDebounceTimeout);
        const query = input.value.trim();
        if (selectedIndex >= 0) {
          triggerSelected();
        } else if (query) {
          performSearch(query);
        }
        return;
      }

      if (dropdown.classList.contains('hidden')) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        navigateResults(1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        navigateResults(-1);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        clearTimeout(searchDebounceTimeout);
        closeDropdown();
        input.blur();
      }
    });

    // 4. Click outside to close
    document.addEventListener('click', (e) => {
      if (container && !container.contains(e.target)) {
        closeDropdown();
      }
    });

    // 5. Footer Click Handler
    if (footer) {
      footer.addEventListener('click', () => {
        const query = input.value.trim();
        saveRecentSearch(query || 'Pages');
        window.location.href = `/admin/search?q=${encodeURIComponent(query)}`;
      });
    }
  }

  // Perform search query (Deep Search across Pages, Sections, Blogs)
  async function performSearch(query) {
    const dropdown = document.getElementById('va-global-search-dropdown');
    const resultsBox = document.getElementById('va-global-search-results');
    const footer = document.getElementById('va-global-search-footer');
    const footerText = document.getElementById('va-global-search-footer-text');

    if (!dropdown || !resultsBox) return;
    selectedIndex = -1;
    latestQuery = query;

    // Case 1: Empty Query -> Show Recent Searches
    if (!query) {
      renderRecentSearches();
      if (footer) footer.classList.add('hidden');
      dropdown.classList.remove('hidden');
      return;
    }

    try {
      const res = await fetch(`/visionadmin/api/global-search?q=${encodeURIComponent(query)}`);
      const data = await res.json();

      // Guard against race conditions if query changed while fetching
      if (latestQuery !== query) return;

      const pages = (data.results && data.results.pages) || [];
      const sections = (data.results && data.results.sections) || [];
      const blogs = (data.results && data.results.blogs) || [];
      const total = data.total || (pages.length + sections.length + blogs.length);

      currentResults = [...pages, ...sections, ...blogs];

      if (total > 0) {
        renderCategorizedResults(pages, sections, blogs, query);
        if (footer && footerText) {
          footerText.textContent = `View all results for "${query}"`;
          footer.classList.remove('hidden');
        }
      } else {
        renderNoResults(query);
        if (footer && footerText) {
          footerText.textContent = `Search all content for "${query}"`;
          footer.classList.remove('hidden');
        }
      }

      dropdown.classList.remove('hidden');
    } catch (err) {
      console.warn('Search error:', err);
    }
  }

  // Render Categorized Results (Pages, Sections, Blogs)
  function renderCategorizedResults(pages, sections, blogs, query) {
    const resultsBox = document.getElementById('va-global-search-results');
    if (!resultsBox) return;

    let html = '';
    let globalIndex = 0;

    // 1. Pages Group
    if (pages.length > 0) {
      html += `
        <div class="px-4 pt-3 pb-1.5 flex items-center justify-between">
          <span class="text-xs font-black text-[var(--ink)] tracking-tight">Pages</span>
          <span class="text-[11px] font-bold text-slate-400">${pages.length} ${pages.length === 1 ? 'result' : 'results'}</span>
        </div>
        <div class="px-2 pb-2 space-y-1">
      `;

      pages.forEach(item => {
        const highlightedTitle = highlightMatch(item.title, query);
        const highlightedSnippet = item.snippet && item.snippet !== item.title ? highlightMatch(item.snippet, query) : '';
        const badgeHtml = item.is_active
          ? `<span class="va-search-badge-active"><span class="w-1.5 h-1.5 rounded-full bg-[var(--green)]"></span>Active (Live)</span>`
          : `<span class="va-search-badge-inactive"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Inactive</span>`;

        html += `
          <div 
            class="va-search-item group" 
            data-index="${globalIndex++}" 
            data-url="${escapeHtml(item.url)}"
            data-title="${escapeHtml(item.title)}"
          >
            <div class="flex items-center gap-3 min-w-0 pr-3">
              <div class="w-8 h-8 rounded-lg bg-[var(--green-tint)] text-[var(--green)] flex items-center justify-center shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div class="min-w-0">
                <p class="va-search-title text-xs font-bold text-[var(--ink)] truncate transition-colors">
                  ${highlightedTitle}
                </p>
                <p class="text-[11px] font-mono text-[var(--slate)] truncate mt-0.5">
                  ${highlightedSnippet || escapeHtml(item.slug)}
                </p>
              </div>
            </div>
            <div class="shrink-0">
              ${badgeHtml}
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }

    // 2. Sections Group
    if (sections.length > 0) {
      html += `
        <div class="px-4 pt-3 pb-1.5 flex items-center justify-between border-t border-[var(--line)]">
          <span class="text-xs font-black text-[var(--ink)] tracking-tight">Page Sections</span>
          <span class="text-[11px] font-bold text-slate-400">${sections.length} ${sections.length === 1 ? 'result' : 'results'}</span>
        </div>
        <div class="px-2 pb-2 space-y-1">
      `;

      sections.forEach(item => {
        const highlightedTitle = highlightMatch(item.title, query);
        const highlightedSnippet = item.snippet ? highlightMatch(item.snippet, query) : '';
        const badgeHtml = item.is_active
          ? `<span class="va-search-badge-active"><span class="w-1.5 h-1.5 rounded-full bg-[var(--green)]"></span>Active</span>`
          : `<span class="va-search-badge-inactive"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Inactive</span>`;

        html += `
          <div 
            class="va-search-item group" 
            data-index="${globalIndex++}" 
            data-url="${escapeHtml(item.url)}"
            data-title="${escapeHtml(item.title)}"
          >
            <div class="flex items-center gap-3 min-w-0 pr-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-50 text-[#35760F] flex items-center justify-center shrink-0 border border-[#D1E7C4]">
                <svg class="w-4 h-4 text-[var(--green)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
              </div>
              <div class="min-w-0">
                <p class="va-search-title text-xs font-bold text-[var(--ink)] truncate transition-colors">
                  ${highlightedTitle}
                </p>
                <p class="text-[11px] text-[var(--slate)] truncate mt-0.5">
                  ${highlightedSnippet || `<span class="font-mono">${escapeHtml(item.slug)}</span>`}
                </p>
              </div>
            </div>
            <div class="shrink-0">
              ${badgeHtml}
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }

    // 3. Blogs & Articles Group
    if (blogs.length > 0) {
      html += `
        <div class="px-4 pt-3 pb-1.5 flex items-center justify-between border-t border-[var(--line)]">
          <span class="text-xs font-black text-[var(--ink)] tracking-tight">Blogs & Articles</span>
          <span class="text-[11px] font-bold text-slate-400">${blogs.length} ${blogs.length === 1 ? 'result' : 'results'}</span>
        </div>
        <div class="px-2 pb-2 space-y-1">
      `;

      blogs.forEach(item => {
        const highlightedTitle = highlightMatch(item.title, query);
        const highlightedSnippet = item.snippet && item.snippet !== item.title ? highlightMatch(item.snippet, query) : '';
        const badgeHtml = item.is_active
          ? `<span class="va-search-badge-active"><span class="w-1.5 h-1.5 rounded-full bg-[var(--green)]"></span>Published</span>`
          : `<span class="va-search-badge-inactive"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Draft</span>`;

        html += `
          <div 
            class="va-search-item group" 
            data-index="${globalIndex++}" 
            data-url="${escapeHtml(item.url)}"
            data-title="${escapeHtml(item.title)}"
          >
            <div class="flex items-center gap-3 min-w-0 pr-3">
              <div class="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center shrink-0">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                </svg>
              </div>
              <div class="min-w-0">
                <p class="va-search-title text-xs font-bold text-[var(--ink)] truncate transition-colors">
                  ${highlightedTitle}
                </p>
                <p class="text-[11px] text-[var(--slate)] truncate mt-0.5">
                  ${highlightedSnippet || `<span class="font-mono">${escapeHtml(item.slug)}</span>`}
                </p>
              </div>
            </div>
            <div class="shrink-0">
              ${badgeHtml}
            </div>
          </div>
        `;
      });
      html += `</div>`;
    }

    resultsBox.innerHTML = html;

    // Attach click listeners to all rows
    resultsBox.querySelectorAll('.va-search-item').forEach(el => {
      el.addEventListener('click', () => {
        const title = el.dataset.title;
        const url = el.dataset.url;
        saveRecentSearch(title);
        closeDropdown();
        window.location.href = url;
      });
    });
  }

  // Render Recent Searches
  function renderRecentSearches() {
    const resultsBox = document.getElementById('va-global-search-results');
    if (!resultsBox) return;

    let recent = [];
    try {
      recent = JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY)) || DEFAULT_RECENT;
    } catch (e) {
      recent = DEFAULT_RECENT;
    }

    if (!recent || recent.length === 0) {
      resultsBox.innerHTML = `
        <div class="p-6 text-center text-xs font-medium text-slate-400">
          Start typing to search pages, sections, or articles...
        </div>
      `;
      currentResults = [];
      return;
    }

    currentResults = recent.map((title, idx) => ({
      id: idx,
      type: 'recent',
      title: title,
      url: `/visionadmin/pages?q=${encodeURIComponent(title)}`
    }));

    let html = `
      <div class="px-4 pt-3.5 pb-2 flex items-center justify-between">
        <span class="text-xs font-black text-[var(--ink)] tracking-tight">Recent Searches</span>
        <button type="button" id="va-clear-recent-btn" class="text-[10px] font-bold text-slate-400 hover:text-slate-700 cursor-pointer">Clear</button>
      </div>
      <div class="px-2 pb-2 space-y-1">
    `;

    recent.forEach((item, index) => {
      html += `
        <div 
          class="va-search-item group" 
          data-index="${index}" 
          data-title="${escapeHtml(item)}"
        >
          <div class="flex items-center gap-3">
            <div class="w-7 h-7 rounded-lg bg-slate-100 text-slate-500 flex items-center justify-center shrink-0">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <span class="va-search-title text-xs font-bold text-[var(--ink)] truncate">
              ${escapeHtml(item)}
            </span>
          </div>
          <svg class="w-3.5 h-3.5 text-slate-300 group-hover:text-[var(--green)] transition" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
      `;
    });

    html += `</div>`;
    resultsBox.innerHTML = html;

    // Attach click listeners to recent items
    resultsBox.querySelectorAll('.va-search-item').forEach(el => {
      el.addEventListener('click', () => {
        const title = el.dataset.title;
        const input = document.getElementById('va-global-search-input');
        if (input) {
          input.value = title;
          const clearBtn = document.getElementById('va-global-search-clear');
          if (clearBtn) clearBtn.classList.remove('hidden');
          performSearch(title);
        }
      });
    });

    const clearRecentBtn = document.getElementById('va-clear-recent-btn');
    if (clearRecentBtn) {
      clearRecentBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        localStorage.removeItem(RECENT_SEARCHES_KEY);
        renderRecentSearches();
      });
    }
  }

  // Render No Results
  function renderNoResults(query) {
    const resultsBox = document.getElementById('va-global-search-results');
    if (!resultsBox) return;

    currentResults = [];
    resultsBox.innerHTML = `
      <div class="py-7 px-4 text-center">
        <div class="w-10 h-10 rounded-2xl bg-slate-100 text-slate-400 mx-auto flex items-center justify-center mb-2.5">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </div>
        <p class="text-xs font-black text-[var(--ink)]">No results found</p>
        <p class="text-[11px] font-medium text-slate-400 mt-0.5">No content matched &ldquo;${escapeHtml(query)}&rdquo; across pages, sections, or blogs.</p>
      </div>
    `;
  }

  // Render Typing State (waiting 5 seconds)
  function renderTypingState(query) {
    const dropdown = document.getElementById('va-global-search-dropdown');
    const resultsBox = document.getElementById('va-global-search-results');
    const footer = document.getElementById('va-global-search-footer');
    if (!dropdown || !resultsBox) return;

    resultsBox.innerHTML = `
      <div class="py-6 px-4 text-center">
        <div class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[var(--green-tint)] text-[var(--green)] mb-2">
          <svg class="w-4 h-4 animate-spin text-[var(--green)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
        </div>
        <p class="text-xs font-black text-[var(--ink)]">Waiting for you to finish typing...</p>
        <p class="text-[11px] font-medium text-slate-400 mt-0.5">Searching in 5s &bull; Press <kbd class="px-1.5 py-0.5 rounded bg-slate-100 font-mono text-[10px] text-slate-700 font-bold border border-slate-200">Enter</kbd> to search immediately for &ldquo;${escapeHtml(query)}&rdquo;</p>
      </div>
    `;
    if (footer) footer.classList.add('hidden');
    dropdown.classList.remove('hidden');
  }

  // Keyboard navigation through results list
  function navigateResults(direction) {
    const items = document.querySelectorAll('#va-global-search-results .va-search-item');
    if (!items || items.length === 0) return;

    items.forEach(el => el.classList.remove('va-search-selected'));

    selectedIndex += direction;
    if (selectedIndex >= items.length) selectedIndex = 0;
    if (selectedIndex < 0) selectedIndex = items.length - 1;

    const selectedItem = items[selectedIndex];
    if (selectedItem) {
      selectedItem.classList.add('va-search-selected');
      selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }

  // Trigger action for currently highlighted item
  function triggerSelected() {
    const items = document.querySelectorAll('#va-global-search-results .va-search-item');
    if (items && items[selectedIndex]) {
      items[selectedIndex].click();
      return;
    }

    const input = document.getElementById('va-global-search-input');
    const query = input ? input.value.trim() : '';
    if (query) {
      saveRecentSearch(query);
      closeDropdown();
      window.location.href = `/admin/search?q=${encodeURIComponent(query)}`;
    }
  }

  // Helper to save recent search string
  function saveRecentSearch(term) {
    if (!term || typeof term !== 'string') return;
    term = term.trim();
    if (!term) return;

    try {
      let recent = JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY)) || DEFAULT_RECENT;
      recent = recent.filter(t => t.toLowerCase() !== term.toLowerCase());
      recent.unshift(term);
      if (recent.length > 6) recent = recent.slice(0, 6);
      localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(recent));
    } catch (e) {}
  }

  function closeDropdown() {
    const dropdown = document.getElementById('va-global-search-dropdown');
    if (dropdown) dropdown.classList.add('hidden');
    selectedIndex = -1;
  }

  function highlightMatch(text, query) {
    if (!text) return '';
    if (!query) return escapeHtml(text);
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedQuery})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark class="va-search-match">$1</mark>');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, m => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    })[m]);
  }

  // Initialize on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlobalSearch);
  } else {
    initGlobalSearch();
  }
})();

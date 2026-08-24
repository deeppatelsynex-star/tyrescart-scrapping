// pages.js - VisionAdmin Pages & Policies CRUD Controller
document.addEventListener('DOMContentLoaded', () => {
  let pagesData = [];
  let currentFilter = 'all';
  let currentSearch = '';
  let activeLocaleTab = 'en';

  const tableBody = document.getElementById('pages-table-body');
  const searchInput = document.getElementById('pages-search-input');
  const modal = document.getElementById('page-modal');
  const modalTitle = document.getElementById('modal-title');
  const pageForm = document.getElementById('page-form');
  const editIdInput = document.getElementById('edit-page-id');
  const saveBtn = document.getElementById('btn-save-page');
  const saveBtnText = document.getElementById('save-btn-text');

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

  // ---------------------------------------------------------------------------
  // 1. Fetch & Render Pages Table
  // ---------------------------------------------------------------------------
  async function loadPages() {
    try {
      const isTrash = currentFilter === 'trash';
      const url = `/visionadmin/api/pages?status=${currentFilter}&trash=${isTrash ? '1' : '0'}&q=${encodeURIComponent(currentSearch)}`;
      const res = await fetch(url);
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Failed to load pages');

      pagesData = data.pages || [];
      updateMetrics(data.metrics || {});
      renderTable(pagesData);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-rose-500 font-bold">Error loading pages: ${err.message}</td></tr>`;
    }
  }

  function updateMetrics(metrics) {
    document.getElementById('stat-total').textContent = metrics.total || 0;
    document.getElementById('stat-published').textContent = metrics.published || 0;
    document.getElementById('stat-draft').textContent = metrics.draft || 0;
    document.getElementById('stat-navigation').textContent = (metrics.in_header || 0) + (metrics.in_footer || 0);
  }

  function renderTable(pages) {
    if (!pages.length) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="py-12 text-center text-slate-400">
            <svg class="w-8 h-8 mx-auto text-slate-300 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <p class="font-bold text-sm text-slate-600">No static pages found</p>
            <p class="text-xs text-slate-400 mt-0.5">${currentFilter === 'trash' ? 'Trash is empty.' : 'Click "+ Create New Page" to add one.'}</p>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = pages.map(p => {
      const enTitle = (typeof p.title === 'object' ? p.title?.en : p.title) || 'Untitled';
      const arTitle = (typeof p.title === 'object' ? p.title?.ar : '') || '';

      const statusBadge = p.status === 'published' 
        ? '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold va-badge-published">Published</span>'
        : (p.status === 'draft'
          ? '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold va-badge-draft">Draft</span>'
          : '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold va-badge-archived">Archived</span>');

      const isTrash = currentFilter === 'trash';

      return `
        <tr class="hover:bg-slate-50/70 transition">
          <td class="py-3.5 px-4 sm:px-6">
            <div class="space-y-0.5">
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900">${escapeHtml(enTitle)}</span>
                ${arTitle ? `<span class="text-xs text-slate-400" dir="rtl">(${escapeHtml(arTitle)})</span>` : ''}
              </div>
              <div class="flex items-center gap-2 text-xs">
                <a href="/${p.slug}" target="_blank" class="text-emerald-600 font-mono hover:underline inline-flex items-center gap-1">
                  <span>/${p.slug}</span>
                  <svg class="w-3 h-3 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </a>
              </div>
            </div>
          </td>
          <td class="py-3.5 px-4">
            <span class="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-xs font-mono font-medium">${p.template || 'default'}</span>
          </td>
          <td class="py-3.5 px-4">
            <div class="flex items-center gap-1.5 flex-wrap">
              ${p.show_in_header ? '<span class="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-[10px] font-extrabold">Header</span>' : ''}
              ${p.show_in_footer ? '<span class="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 text-[10px] font-extrabold">Footer</span>' : ''}
              ${!p.show_in_header && !p.show_in_footer ? '<span class="text-xs text-slate-400">—</span>' : ''}
            </div>
          </td>
          <td class="py-3.5 px-4">
            ${statusBadge}
          </td>
          <td class="py-3.5 px-4 font-mono text-xs text-slate-500">
            ${p.sort_order || 0}
          </td>
          <td class="py-3.5 px-4 sm:px-6 text-right space-x-2">
            ${!isTrash ? `
              <button type="button" onclick="window.editPage(${p.id})" class="px-3 py-1 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer">
                Edit
              </button>
              <button type="button" onclick="window.deletePage(${p.id}, '${escapeHtml(enTitle)}')" class="px-3 py-1 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-bold transition cursor-pointer">
                Trash
              </button>
            ` : `
              <button type="button" onclick="window.restorePage(${p.id})" class="px-3 py-1 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold transition cursor-pointer">
                Restore
              </button>
            `}
          </td>
        </tr>
      `;
    }).join('');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  }

  // ---------------------------------------------------------------------------
  // 2. Filter Tabs & Search Handler
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.tab-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-filter').forEach(b => {
        b.className = 'tab-filter px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 transition';
      });
      btn.className = 'tab-filter px-3 py-1.5 rounded-lg bg-white shadow-xs text-slate-900 transition font-bold';
      currentFilter = btn.dataset.status;
      loadPages();
    });
  });

  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentSearch = e.target.value.trim();
        loadPages();
      }, 250);
    });
  }

  // ---------------------------------------------------------------------------
  // 3. Multi-Locale Tab Switcher
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.locale-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const loc = tab.dataset.locale;
      activeLocaleTab = loc;
      document.querySelectorAll('.locale-tab').forEach(t => {
        t.className = 'locale-tab px-3.5 py-1.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition';
      });
      tab.className = 'locale-tab px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-900 text-white shadow-xs transition';

      if (loc === 'en') {
        document.getElementById('locale-block-en').classList.remove('hidden');
        document.getElementById('locale-block-ar').classList.add('hidden');
      } else {
        document.getElementById('locale-block-en').classList.add('hidden');
        document.getElementById('locale-block-ar').classList.remove('hidden');
      }
    });
  });

  // ---------------------------------------------------------------------------
  // 4. Modal Open / Close & Auto Slugify
  // ---------------------------------------------------------------------------
  function openModal(isEdit = false, page = null) {
    pageForm.reset();
    editIdInput.value = isEdit && page ? page.id : '';
    modalTitle.textContent = isEdit ? 'Edit Static Page' : 'Create New Static Page';
    saveBtnText.textContent = isEdit ? 'Save Changes' : 'Create Page';

    // Reset locale tabs to English
    document.querySelector('.locale-tab[data-locale="en"]')?.click();

    if (isEdit && page) {
      document.getElementById('title_en').value = page.title?.en || (typeof page.title === 'string' ? page.title : '');
      document.getElementById('title_ar').value = page.title?.ar || '';
      document.getElementById('excerpt_en').value = page.excerpt?.en || '';
      document.getElementById('excerpt_ar').value = page.excerpt?.ar || '';
      document.getElementById('content_en').value = page.content?.en || '';
      document.getElementById('content_ar').value = page.content?.ar || '';
      document.getElementById('slug').value = page.slug || '';
      document.getElementById('template').value = page.template || 'default';
      document.getElementById('status').value = page.status || 'published';
      document.getElementById('show_in_header').checked = Boolean(page.show_in_header);
      document.getElementById('show_in_footer').checked = Boolean(page.show_in_footer);
      document.getElementById('sort_order').value = page.sort_order || 0;
      document.getElementById('meta_title_en').value = page.meta_title?.en || '';
      document.getElementById('meta_desc_en').value = page.meta_desc?.en || '';
    } else {
      document.getElementById('status').value = 'published';
      document.getElementById('show_in_footer').checked = true;
    }

    modal.classList.remove('hidden');
  }

  function closeModal() {
    modal.classList.add('hidden');
  }

  document.getElementById('btn-create-page')?.addEventListener('click', () => openModal(false));
  document.getElementById('btn-close-modal')?.addEventListener('click', closeModal);
  document.getElementById('btn-cancel-modal')?.addEventListener('click', closeModal);
  document.getElementById('modal-backdrop')?.addEventListener('click', closeModal);

  // Auto slug generator on English title change
  const titleEnInput = document.getElementById('title_en');
  const slugInput = document.getElementById('slug');
  titleEnInput?.addEventListener('input', () => {
    if (!editIdInput.value) { // Only auto-slugify on Create mode
      const slugified = titleEnInput.value.toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
      slugInput.value = slugified;
    }
  });

  // ---------------------------------------------------------------------------
  // 5. Submit Form (Create / Update)
  // ---------------------------------------------------------------------------
  saveBtn?.addEventListener('click', async () => {
    const editId = editIdInput.value;
    const title_en = document.getElementById('title_en').value.trim();
    const title_ar = document.getElementById('title_ar').value.trim();
    const slug = document.getElementById('slug').value.trim();

    if (!title_en) {
      alert('Please provide an English page title.');
      document.querySelector('.locale-tab[data-locale="en"]')?.click();
      document.getElementById('title_en').focus();
      return;
    }

    const payload = {
      title: { en: title_en, ar: title_ar },
      excerpt: {
        en: document.getElementById('excerpt_en').value.trim(),
        ar: document.getElementById('excerpt_ar').value.trim()
      },
      content: {
        en: document.getElementById('content_en').value.trim(),
        ar: document.getElementById('content_ar').value.trim()
      },
      slug: slug,
      template: document.getElementById('template').value,
      status: document.getElementById('status').value,
      show_in_header: document.getElementById('show_in_header').checked,
      show_in_footer: document.getElementById('show_in_footer').checked,
      sort_order: parseInt(document.getElementById('sort_order').value, 10) || 0,
      meta_title: {
        en: document.getElementById('meta_title_en').value.trim(),
        ar: ''
      },
      meta_desc: {
        en: document.getElementById('meta_desc_en').value.trim(),
        ar: ''
      }
    };

    saveBtn.disabled = true;
    saveBtnText.textContent = 'Saving…';

    try {
      const url = editId ? `/visionadmin/api/pages/${editId}` : '/visionadmin/api/pages';
      const method = editId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to save page');

      window.vaShowToast(data.message || 'Page saved successfully!');
      closeModal();
      loadPages();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      saveBtn.disabled = false;
      saveBtnText.textContent = editId ? 'Save Changes' : 'Create Page';
    }
  });

  // ---------------------------------------------------------------------------
  // 6. Global Action Helpers
  // ---------------------------------------------------------------------------
  window.editPage = async function(id) {
    try {
      const res = await fetch(`/visionadmin/api/pages/${id}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch page data');
      openModal(true, data.page);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  window.deletePage = async function(id, title) {
    if (!confirm(`Are you sure you want to move page "${title}" to Trash?`)) return;

    try {
      const res = await fetch(`/visionadmin/api/pages/${id}`, {
        method: 'DELETE',
        headers: { 'X-CSRF-Token': csrfToken }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to delete page');

      window.vaShowToast(data.message || 'Page moved to Trash.');
      loadPages();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  window.restorePage = async function(id) {
    try {
      const res = await fetch(`/visionadmin/api/pages/${id}/restore`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to restore page');

      window.vaShowToast('Page restored successfully.');
      loadPages();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // Initial Load
  loadPages();
});

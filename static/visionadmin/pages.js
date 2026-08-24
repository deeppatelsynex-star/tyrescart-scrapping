// pages.js - VisionAdmin Pages & Policies CRUD Controller with CKEditor 5 & Banner Upload
document.addEventListener('DOMContentLoaded', () => {
  let pagesData = [];
  let currentFilter = 'all';
  let currentSearch = '';
  let activeLocaleTab = 'en';

  let editorEn = null;
  let editorAr = null;

  const tableBody = document.getElementById('pages-table-body');
  const searchInput = document.getElementById('pages-search-input');
  const modal = document.getElementById('page-modal');
  const modalTitle = document.getElementById('modal-title');
  const pageForm = document.getElementById('page-form');
  const editIdInput = document.getElementById('edit-page-id');
  const saveBtn = document.getElementById('btn-save-page');
  const saveBtnText = document.getElementById('save-btn-text');

  const bannerFileInput = document.getElementById('banner_file_input');
  const bannerImageInput = document.getElementById('banner_image');
  const bannerPreviewImg = document.getElementById('banner-preview-img');
  const bannerPlaceholderIcon = document.getElementById('banner-placeholder-icon');
  const bannerRemoveBtn = document.getElementById('btn-remove-banner');
  const bannerStatusText = document.getElementById('banner-file-status');

  // ---------------------------------------------------------------------------
  // 1. Initialize CKEditor 5 SuperBuild with Code / Source Editing
  // ---------------------------------------------------------------------------
  const ckeditorConfig = {
    toolbar: {
      items: [
        'sourceEditing', '|',
        'heading', '|',
        'bold', 'italic', 'underline', 'strikethrough', 'code', '|',
        'link', 'bulletedList', 'numberedList', 'blockQuote', 'codeBlock', '|',
        'alignment', '|',
        'insertTable', 'horizontalLine', '|',
        'undo', 'redo'
      ],
      shouldNotGroupWhenFull: true
    },
    removePlugins: [
      'CKBox', 'CKFinder', 'EasyImage', 'RealTimeCollaborativeComments',
      'RealTimeCollaborativeTrackChanges', 'RealTimeCollaborativeRevisionHistory',
      'PresenceList', 'Comments', 'TrackChanges', 'TrackChangesData', 'RevisionHistory',
      'Pagination', 'WProofreader', 'MathType', 'SlashCommand', 'Template', 'DocumentOutline',
      'FormatPainter', 'TableOfContents', 'PasteFromOfficeEnhanced'
    ]
  };

  async function initEditors() {
    try {
      if (window.CKEDITOR && CKEDITOR.ClassicEditor) {
        // English Editor
        if (document.getElementById('content_en') && !editorEn) {
          editorEn = await CKEDITOR.ClassicEditor.create(
            document.getElementById('content_en'),
            { ...ckeditorConfig }
          );
        }

        // Arabic Editor
        if (document.getElementById('content_ar') && !editorAr) {
          editorAr = await CKEDITOR.ClassicEditor.create(
            document.getElementById('content_ar'),
            {
              ...ckeditorConfig,
              language: { content: 'ar' }
            }
          );
        }
      }
    } catch (err) {
      console.warn('CKEditor initialization notice:', err);
    }
  }

  initEditors();

  // ---------------------------------------------------------------------------
  // 2. Banner Image File Upload Handler
  // ---------------------------------------------------------------------------
  function setBannerPreview(url) {
    if (url) {
      bannerImageInput.value = url;
      bannerPreviewImg.src = url;
      bannerPreviewImg.classList.remove('hidden');
      bannerPlaceholderIcon.classList.add('hidden');
      bannerRemoveBtn.classList.remove('hidden');
      bannerStatusText.textContent = url.split('/').pop();
    } else {
      bannerImageInput.value = '';
      bannerPreviewImg.src = '';
      bannerPreviewImg.classList.add('hidden');
      bannerPlaceholderIcon.classList.remove('hidden');
      bannerRemoveBtn.classList.add('hidden');
      bannerFileInput.value = '';
      bannerStatusText.textContent = 'PNG, JPG, WEBP, SVG or AVIF up to 10MB.';
    }
  }

  bannerFileInput?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    bannerStatusText.textContent = `Uploading "${file.name}"…`;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/visionadmin/api/upload-banner', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Failed to upload banner');

      setBannerPreview(data.url);
      window.vaShowToast('Banner image uploaded successfully!');
    } catch (err) {
      alert(`Upload error: ${err.message}`);
      setBannerPreview('');
    }
  });

  bannerRemoveBtn?.addEventListener('click', () => setBannerPreview(''));

  // ---------------------------------------------------------------------------
  // 3. Fetch & Render Pages Table
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
      tableBody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-rose-500 font-bold">Error loading pages: ${err.message}</td></tr>`;
    }
  }

  function updateMetrics(metrics) {
    document.getElementById('stat-total').textContent = metrics.total || 0;
    document.getElementById('stat-active').textContent = metrics.active || 0;
    document.getElementById('stat-inactive').textContent = metrics.inactive || 0;
    document.getElementById('stat-trash').textContent = metrics.trash || 0;
  }

  function renderTable(pages) {
    if (!pages.length) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="py-12 text-center text-slate-400">
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

      const statusBadge = p.is_active 
        ? '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold va-badge-published">Active (Live)</span>'
        : '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold va-badge-draft">Inactive</span>';

      const isTrash = currentFilter === 'trash';
      const updatedDate = p.updated_at ? p.updated_at.split('T')[0] : (p.created_at ? p.created_at.split('T')[0] : '—');

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
            ${p.banner_image ? `
              <div class="flex items-center gap-2">
                <img src="${escapeHtml(p.banner_image)}" alt="Banner" class="w-9 h-6 object-cover rounded-md border border-slate-200 shadow-2xs shrink-0" />
                <a href="${escapeHtml(p.banner_image)}" target="_blank" class="text-[11px] text-indigo-600 font-bold hover:underline truncate max-w-[120px]">View</a>
              </div>
            ` : '<span class="text-xs text-slate-400">None</span>'}
          </td>
          <td class="py-3.5 px-4">
            ${statusBadge}
          </td>
          <td class="py-3.5 px-4 font-mono text-xs text-slate-500">
            ${updatedDate}
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
  // 4. Filter Tabs & Search Handler
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
  // 5. Multi-Locale Tab Switcher
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
  // 6. Modal Open / Close & Auto Slugify
  // ---------------------------------------------------------------------------
  function openModal(isEdit = false, page = null) {
    pageForm.reset();
    editIdInput.value = isEdit && page ? page.id : '';
    modalTitle.textContent = isEdit ? 'Edit Static Page' : 'Create New Static Page';
    saveBtnText.textContent = isEdit ? 'Save Changes' : 'Create Page';

    document.querySelector('.locale-tab[data-locale="en"]')?.click();

    if (isEdit && page) {
      document.getElementById('title_en').value = page.title?.en || (typeof page.title === 'string' ? page.title : '');
      document.getElementById('title_ar').value = page.title?.ar || '';
      document.getElementById('slug').value = page.slug || '';
      document.getElementById('is_active').checked = Boolean(page.is_active);
      document.getElementById('seo_title_en').value = page.seo_title?.en || '';
      document.getElementById('seo_title_ar').value = page.seo_title?.ar || '';
      document.getElementById('meta_description_en').value = page.meta_description?.en || '';
      document.getElementById('meta_description_ar').value = page.meta_description?.ar || '';

      setBannerPreview(page.banner_image || '');

      const contentEnVal = page.content?.en || (typeof page.content === 'string' ? page.content : '');
      const contentArVal = page.content?.ar || '';

      if (editorEn) editorEn.setData(contentEnVal);
      else document.getElementById('content_en').value = contentEnVal;

      if (editorAr) editorAr.setData(contentArVal);
      else document.getElementById('content_ar').value = contentArVal;

    } else {
      document.getElementById('is_active').checked = true;
      setBannerPreview('');

      if (editorEn) editorEn.setData('');
      if (editorAr) editorAr.setData('');
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
    if (!editIdInput.value) {
      const slugified = titleEnInput.value.toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
      slugInput.value = slugified;
    }
  });

  // ---------------------------------------------------------------------------
  // 7. Submit Form (Create / Update)
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

    const content_en = editorEn ? editorEn.getData() : document.getElementById('content_en').value;
    const content_ar = editorAr ? editorAr.getData() : document.getElementById('content_ar').value;

    const payload = {
      title: { en: title_en, ar: title_ar },
      content: { en: content_en, ar: content_ar },
      slug: slug,
      banner_image: bannerImageInput.value.trim() || null,
      is_active: document.getElementById('is_active').checked,
      seo_title: {
        en: document.getElementById('seo_title_en').value.trim(),
        ar: document.getElementById('seo_title_ar').value.trim()
      },
      meta_description: {
        en: document.getElementById('meta_description_en').value.trim(),
        ar: document.getElementById('meta_description_ar').value.trim()
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
          'Content-Type': 'application/json'
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
  // 8. Global Action Helpers
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
        method: 'DELETE'
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
        method: 'POST'
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

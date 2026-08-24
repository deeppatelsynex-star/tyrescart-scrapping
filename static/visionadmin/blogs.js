// blogs.js - VisionAdmin Blogs & Articles CRUD Controller
document.addEventListener('DOMContentLoaded', () => {
  let blogsData = [];
  let currentFilter = 'all';
  let currentSearch = '';
  let activeLocaleTab = 'en';

  const tableBody = document.getElementById('blogs-table-body');
  const searchInput = document.getElementById('blogs-search-input');
  const modal = document.getElementById('blog-modal');
  const modalTitle = document.getElementById('blog-modal-title');
  const blogForm = document.getElementById('blog-form');
  const editIdInput = document.getElementById('edit-blog-id');
  const saveBtn = document.getElementById('btn-save-blog');
  const saveBtnText = document.getElementById('save-blog-btn-text');

  const fileInput = document.getElementById('blog_file_input');
  const imageInput = document.getElementById('blog_image');
  const previewImg = document.getElementById('blog-preview-img');
  const placeholderIcon = document.getElementById('blog-placeholder-icon');
  const removeBtn = document.getElementById('btn-remove-blog-img');
  const fileStatusText = document.getElementById('blog-file-status');

  // ---------------------------------------------------------------------------
  // 1. Flask-CKEditor Helper Functions
  // ---------------------------------------------------------------------------
  function getEditorContent(name) {
    if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances[name]) {
      try {
        CKEDITOR.instances[name].updateElement();
        return CKEDITOR.instances[name].getData() || '';
      } catch (err) {
        console.warn(`Error reading CKEditor "${name}":`, err);
      }
    }
    const el = document.getElementById(name);
    return el ? el.value : '';
  }

  function setEditorContent(name, val) {
    val = val || '';
    const el = document.getElementById(name);
    if (el) el.value = val;

    if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances[name]) {
      try {
        const inst = CKEDITOR.instances[name];
        if (inst.status === 'ready' || inst.instanceReady) {
          inst.setData(val);
        } else {
          inst.on('instanceReady', function() {
            this.setData(val);
          });
        }
      } catch (err) {
        console.warn(`Error setting CKEditor "${name}":`, err);
      }
    }
  }

  // Hook change events to automatically sync to textarea
  if (window.CKEDITOR) {
    CKEDITOR.on('instanceReady', function(evt) {
      evt.editor.on('change', function() {
        this.updateElement();
      });
      evt.editor.on('mode', function() {
        if (this.mode === 'source') {
          const editable = this.editable();
          editable.attachListener(editable, 'input', () => {
            this.updateElement();
          });
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 2. Featured Image Upload Handler
  // ---------------------------------------------------------------------------
  function setImagePreview(url) {
    if (url) {
      imageInput.value = url;
      previewImg.src = url;
      previewImg.classList.remove('hidden');
      placeholderIcon.classList.add('hidden');
      removeBtn.classList.remove('hidden');
      fileStatusText.textContent = url.split('/').pop();
    } else {
      imageInput.value = '';
      previewImg.src = '';
      previewImg.classList.add('hidden');
      placeholderIcon.classList.remove('hidden');
      removeBtn.classList.add('hidden');
      fileInput.value = '';
      fileStatusText.textContent = 'PNG, JPG, WEBP, SVG or AVIF up to 10MB.';
    }
  }

  fileInput?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    fileStatusText.textContent = `Uploading "${file.name}"…`;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/visionadmin/api/upload-blog-image', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Failed to upload image');

      setImagePreview(data.url);
      window.vaShowToast('Featured image uploaded successfully!');
    } catch (err) {
      alert(`Upload error: ${err.message}`);
      setImagePreview('');
    }
  });

  removeBtn?.addEventListener('click', () => setImagePreview(''));

  // ---------------------------------------------------------------------------
  // 3. Fetch & Render Blogs Table
  // ---------------------------------------------------------------------------
  async function loadBlogs() {
    try {
      const isTrash = currentFilter === 'trash';
      const statusParam = (currentFilter !== 'all' && currentFilter !== 'trash') ? currentFilter : '';
      const url = `/visionadmin/api/blogs?status=${statusParam}&trash=${isTrash ? '1' : '0'}&q=${encodeURIComponent(currentSearch)}`;
      const res = await fetch(url);
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || 'Failed to load blogs');

      blogsData = data.blogs || [];
      updateMetrics(data.metrics || {});
      renderTable(blogsData);
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-rose-500 font-bold">Error loading articles: ${err.message}</td></tr>`;
    }
  }

  function updateMetrics(metrics) {
    document.getElementById('stat-total').textContent = metrics.total || 0;
    document.getElementById('stat-published').textContent = metrics.published || 0;
    document.getElementById('stat-draft').textContent = metrics.draft || 0;
    document.getElementById('stat-archived').textContent = metrics.archived || 0;
    document.getElementById('stat-trash').textContent = metrics.trash || 0;
  }

  function renderTable(blogs) {
    if (!blogs.length) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" class="py-12 text-center text-slate-400">
            <svg class="w-8 h-8 mx-auto text-slate-300 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="9" y1="6" x2="16" y2="6"/><line x1="9" y1="10" x2="16" y2="10"/></svg>
            <p class="font-bold text-sm text-slate-600">No blog articles found</p>
            <p class="text-xs text-slate-400 mt-0.5">${currentFilter === 'trash' ? 'Trash is empty.' : 'Click "+ Create New Article" to publish one.'}</p>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = blogs.map(b => {
      const enTitle = (typeof b.title === 'object' ? b.title?.en : b.title) || 'Untitled Article';
      const arTitle = (typeof b.title === 'object' ? b.title?.ar : '') || '';

      let statusBadge = '';
      if (b.status === 'published') {
        statusBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">Published</span>';
      } else if (b.status === 'archived') {
        statusBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">Archived</span>';
      } else {
        statusBadge = '<span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">Draft</span>';
      }

      const isTrash = currentFilter === 'trash';
      const pubDate = b.published_at ? b.published_at.split('T')[0] : (b.created_at ? b.created_at.split('T')[0] : '—');

      return `
        <tr class="hover:bg-slate-50/70 transition">
          <td class="py-3.5 px-4 sm:px-6">
            <div class="space-y-0.5">
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900">${escapeHtml(enTitle)}</span>
                ${arTitle ? `<span class="text-xs text-slate-400" dir="rtl">(${escapeHtml(arTitle)})</span>` : ''}
              </div>
              <div class="flex items-center gap-2 text-xs">
                <a href="/blog/${b.slug}" target="_blank" class="text-emerald-600 font-mono hover:underline inline-flex items-center gap-1">
                  <span>/blog/${b.slug}</span>
                  <svg class="w-3 h-3 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </a>
              </div>
            </div>
          </td>
          <td class="py-3.5 px-4">
            ${b.image ? `
              <div class="flex items-center gap-2">
                <img src="${escapeHtml(b.image)}" alt="Thumbnail" class="w-10 h-7 object-cover rounded-lg border border-slate-200 shadow-2xs shrink-0" />
                <a href="${escapeHtml(b.image)}" target="_blank" class="text-[11px] text-indigo-600 font-bold hover:underline truncate max-w-[100px]">View</a>
              </div>
            ` : '<span class="text-xs text-slate-400">No Image</span>'}
          </td>
          <td class="py-3.5 px-4">
            ${statusBadge}
          </td>
          <td class="py-3.5 px-4 font-mono text-xs text-slate-500">
            ${pubDate}
          </td>
          <td class="py-3.5 px-4 sm:px-6 text-right space-x-2">
            ${!isTrash ? `
              <button type="button" onclick="window.editBlog(${b.id})" class="px-3 py-1 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition cursor-pointer">
                Edit
              </button>
              <button type="button" onclick="window.deleteBlog(${b.id}, '${escapeHtml(enTitle)}', false)" class="px-3 py-1 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-600 text-xs font-bold transition cursor-pointer">
                Trash
              </button>
            ` : `
              <button type="button" onclick="window.restoreBlog(${b.id})" class="px-3 py-1 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold transition cursor-pointer">
                Restore
              </button>
              <button type="button" onclick="window.deleteBlog(${b.id}, '${escapeHtml(enTitle)}', true)" class="px-3 py-1 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition cursor-pointer shadow-xs">
                Delete Permanently
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
      loadBlogs();
    });
  });

  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentSearch = e.target.value.trim();
        loadBlogs();
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

      // Refresh/resize CKEditor on tab switch
      setTimeout(() => {
        if (window.CKEDITOR && CKEDITOR.instances) {
          if (loc === 'ar' && CKEDITOR.instances.blog_content_ar) {
            CKEDITOR.instances.blog_content_ar.resize();
          } else if (loc === 'en' && CKEDITOR.instances.blog_content_en) {
            CKEDITOR.instances.blog_content_en.resize();
          }
        }
      }, 50);
    });
  });

  // ---------------------------------------------------------------------------
  // 6. Modal Open / Close & Auto Slugify
  // ---------------------------------------------------------------------------
  function openModal(isEdit = false, blog = null) {
    blogForm.reset();
    editIdInput.value = isEdit && blog ? blog.id : '';
    modalTitle.textContent = isEdit ? 'Edit Blog Article' : 'Create New Blog Article';
    saveBtnText.textContent = isEdit ? 'Save Changes' : 'Publish Article';

    document.querySelector('.locale-tab[data-locale="en"]')?.click();

    if (isEdit && blog) {
      document.getElementById('title_en').value = (typeof blog.title === 'object' ? blog.title?.en : blog.title) || '';
      document.getElementById('title_ar').value = (typeof blog.title === 'object' ? blog.title?.ar : '') || '';
      document.getElementById('slug').value = blog.slug || '';
      document.getElementById('status').value = blog.status || 'draft';
      document.getElementById('short_description_en').value = (typeof blog.short_description === 'object' ? blog.short_description?.en : blog.short_description) || '';
      document.getElementById('short_description_ar').value = (typeof blog.short_description === 'object' ? blog.short_description?.ar : '') || '';
      document.getElementById('meta_title_en').value = (typeof blog.meta_title === 'object' ? blog.meta_title?.en : '') || '';
      document.getElementById('meta_title_ar').value = (typeof blog.meta_title === 'object' ? blog.meta_title?.ar : '') || '';
      document.getElementById('meta_desc_en').value = (typeof blog.meta_desc === 'object' ? blog.meta_desc?.en : '') || '';
      document.getElementById('meta_desc_ar').value = (typeof blog.meta_desc === 'object' ? blog.meta_desc?.ar : '') || '';

      setImagePreview(blog.image || '');

      const contentEnVal = (typeof blog.content === 'object' ? blog.content?.en : blog.content) || '';
      const contentArVal = (typeof blog.content === 'object' ? blog.content?.ar : '') || '';

      setEditorContent('blog_content_en', contentEnVal);
      setEditorContent('blog_content_ar', contentArVal);

    } else {
      document.getElementById('status').value = 'published';
      setImagePreview('');

      setEditorContent('blog_content_en', '');
      setEditorContent('blog_content_ar', '');
    }

    modal.classList.remove('hidden');

    // Resize active editor after modal animation
    setTimeout(() => {
      if (window.CKEDITOR && CKEDITOR.instances) {
        if (CKEDITOR.instances.blog_content_en) CKEDITOR.instances.blog_content_en.resize();
        if (CKEDITOR.instances.blog_content_ar) CKEDITOR.instances.blog_content_ar.resize();
      }
    }, 100);
  }

  function closeModal() {
    modal.classList.add('hidden');
  }

  document.getElementById('btn-create-blog')?.addEventListener('click', () => openModal(false));
  document.getElementById('btn-close-blog-modal')?.addEventListener('click', closeModal);
  document.getElementById('btn-cancel-blog-modal')?.addEventListener('click', closeModal);
  document.getElementById('blog-modal-backdrop')?.addEventListener('click', closeModal);

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
      alert('Please provide an English article title.');
      document.querySelector('.locale-tab[data-locale="en"]')?.click();
      document.getElementById('title_en').focus();
      return;
    }

    // Force update from all CKEditor instances
    if (window.CKEDITOR && CKEDITOR.instances) {
      for (const instName in CKEDITOR.instances) {
        try {
          CKEDITOR.instances[instName].updateElement();
        } catch (e) {}
      }
    }

    const content_en = getEditorContent('blog_content_en');
    const content_ar = getEditorContent('blog_content_ar');

    const payload = {
      title: { en: title_en, ar: title_ar },
      content: { en: content_en, ar: content_ar },
      short_description: {
        en: document.getElementById('short_description_en').value.trim(),
        ar: document.getElementById('short_description_ar').value.trim()
      },
      slug: slug,
      image: imageInput.value.trim() || null,
      status: document.getElementById('status').value,
      meta_title: {
        en: document.getElementById('meta_title_en').value.trim(),
        ar: document.getElementById('meta_title_ar').value.trim()
      },
      meta_desc: {
        en: document.getElementById('meta_desc_en').value.trim(),
        ar: document.getElementById('meta_desc_ar').value.trim()
      }
    };

    saveBtn.disabled = true;
    saveBtnText.textContent = 'Saving…';

    try {
      const url = editId ? `/visionadmin/api/blogs/${editId}` : '/visionadmin/api/blogs';
      const method = editId ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to save article');

      window.vaShowToast(data.message || 'Article saved successfully!');
      closeModal();
      loadBlogs();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      saveBtn.disabled = false;
      saveBtnText.textContent = editId ? 'Save Changes' : 'Publish Article';
    }
  });

  // ---------------------------------------------------------------------------
  // 8. Global Action Helpers
  // ---------------------------------------------------------------------------
  window.editBlog = async function(id) {
    try {
      const res = await fetch(`/visionadmin/api/blogs/${id}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to fetch article data');
      openModal(true, data.blog);
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  window.deleteBlog = async function(id, title, isHard = false) {
    const confirmMsg = isHard
      ? `Are you sure you want to PERMANENTLY delete article "${title}"?\n\nThis will remove the record completely from the database and cannot be undone.`
      : `Are you sure you want to move article "${title}" to Trash?`;

    if (!confirm(confirmMsg)) return;

    try {
      const url = isHard ? `/visionadmin/api/blogs/${id}?hard=1` : `/visionadmin/api/blogs/${id}`;
      const res = await fetch(url, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to delete article');

      window.vaShowToast(data.message || (isHard ? 'Article deleted permanently.' : 'Article moved to Trash.'));
      loadBlogs();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  window.restoreBlog = async function(id) {
    try {
      const res = await fetch(`/visionadmin/api/blogs/${id}/restore`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to restore article');

      window.vaShowToast('Article restored successfully.');
      loadBlogs();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  // Initial Load
  loadBlogs();
});

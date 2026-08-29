/**
 * static/visionadmin/sections.js
 * VisionAdmin CMS — Dynamic About Us Page Sections Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  let allSections = [];
  let currentLocaleTab = 'en';
  let deleteSectionId = null;
  let repeaterItems = [];

  const TYPE_METADATA = {
    hero: { 
      label: 'Hero Banner', 
      shortLabel: 'Hero', 
      emoji: '🦸', 
      badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-200/80',
      tagColor: 'bg-emerald-500',
      desc: 'Cinematic Dark Showroom + 4 Feature Points' 
    },
    content_image: { 
      label: 'Content + Image', 
      shortLabel: '2-Column', 
      emoji: '🖼️', 
      badgeBg: 'bg-blue-50 text-blue-800 border-blue-200/80',
      tagColor: 'bg-blue-500',
      desc: 'Narrative Story with Warehouse Media & Floating Badge' 
    },
    features: { 
      label: 'Features / Values', 
      shortLabel: 'Features', 
      emoji: '✨', 
      badgeBg: 'bg-purple-50 text-purple-800 border-purple-200/80',
      tagColor: 'bg-purple-500',
      desc: 'Multi-card Value Pillars Grid' 
    },
    stats: { 
      label: 'Statistics Band', 
      shortLabel: 'Stats', 
      emoji: '📊', 
      badgeBg: 'bg-indigo-50 text-indigo-800 border-indigo-200/80',
      tagColor: 'bg-indigo-500',
      desc: 'Atmospheric Dark 4-Metric Stats Band' 
    },
    mission_vision: { 
      label: 'Mission & Team', 
      shortLabel: 'Mission', 
      emoji: '🎯', 
      badgeBg: 'bg-amber-50 text-amber-800 border-amber-200/80',
      tagColor: 'bg-amber-500',
      desc: 'Specialist Team / Mission 2-Column Split' 
    },
    cta: { 
      label: 'CTA Action Box', 
      shortLabel: 'CTA Box', 
      emoji: '🚀', 
      badgeBg: 'bg-rose-50 text-rose-800 border-rose-200/80',
      tagColor: 'bg-rose-500',
      desc: 'Bottom Action Card with Wheel Visual & Button' 
    }
  };

  // Target Page handling (Query param ?page=...)
  const urlParams = new URLSearchParams(window.location.search);
  let currentPageSlug = urlParams.get('page') || 'about-us';

  const selectTargetPage = document.getElementById('select-target-page');
  const badgePageSlug = document.getElementById('badge-page-slug');
  const pageSectionsTitle = document.getElementById('page-sections-title');
  const linkViewLivePage = document.getElementById('link-view-live-page');

  // DOM Elements
  const sectionsContainer = document.getElementById('sections-container');
  const statTotal = document.getElementById('stat-total-sections');
  const statActive = document.getElementById('stat-active-sections');
  const statInactive = document.getElementById('stat-inactive-sections');

  // Modal Elements
  const sectionModal = document.getElementById('section-modal');
  const sectionModalBox = document.getElementById('section-modal-box');
  const modalTitle = document.getElementById('modal-title');
  const sectionForm = document.getElementById('section-form');
  const btnAddSection = document.getElementById('btn-add-section');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnCancelModal = document.getElementById('btn-cancel-modal');
  const btnSaveSection = document.getElementById('btn-save-section');

  // Language Tabs
  const tabEn = document.getElementById('tab-en');
  const tabAr = document.getElementById('tab-ar');

  // Form Fields
  const formSectionId = document.getElementById('form-section-id');
  const formPageSlug = document.getElementById('form-page-slug');
  const formTitleEn = document.getElementById('form-title-en');
  const formTitleAr = document.getElementById('form-title-ar');
  const formSubtitleEn = document.getElementById('form-subtitle-en');
  const formSubtitleAr = document.getElementById('form-subtitle-ar');
  const formMetaTitleEn = document.getElementById('form-meta-title-en');
  const formMetaTitleAr = document.getElementById('form-meta-title-ar');
  const formMetaDescEn = document.getElementById('form-meta-desc-en');
  const formMetaDescAr = document.getElementById('form-meta-desc-ar');
  const formContentEn = document.getElementById('form-content-en');
  const formContentAr = document.getElementById('form-content-ar');
  const formImageUrl = document.getElementById('form-image-url');
  const imageFileInput = document.getElementById('image-file-input');
  const previewImageBox = document.getElementById('preview-image-box');
  const btnClearImage = document.getElementById('btn-clear-image');
  const formBtnTextEn = document.getElementById('form-btn-text-en');
  const formBtnTextAr = document.getElementById('form-btn-text-ar');
  const formBtnUrl = document.getElementById('form-btn-url');
  const formIsActive = document.getElementById('form-is-active');
  const formSortOrder = document.getElementById('form-sort-order');

  // Repeater Items List
  const repeaterList = document.getElementById('repeater-items-list');
  const btnAddRepeaterItem = document.getElementById('btn-add-repeater-item');

  // Delete Modal
  const deleteModal = document.getElementById('delete-modal');
  const btnCancelDelete = document.getElementById('btn-cancel-delete');
  const btnConfirmDelete = document.getElementById('btn-confirm-delete');

  // ---------------------------------------------------------------------------
  // 1. Flask-CKEditor Helper Functions
  // ---------------------------------------------------------------------------
  function getEditorContent(name) {
    if (window.CKEDITOR && CKEDITOR.instances && CKEDITOR.instances[name]) {
      try {
        CKEDITOR.instances[name].updateElement();
        return CKEDITOR.instances[name].getData() || '';
      } catch (err) {
        console.warn(`Error getting data from CKEditor "${name}":`, err);
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
        console.warn(`Error setting data in CKEditor "${name}":`, err);
      }
    }
  }

  function stripHtml(html) {
    if (!html) return '';
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return (doc.body.textContent || '').trim();
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
          if (editable) {
            editable.attachListener(editable, 'input', () => {
              evt.editor.updateElement();
            });
          }
        }
      });
    });
  }

  function showToast(msg, type = 'success') {
    const toast = document.getElementById('va-toast');
    if (!toast) return;
    toast.className = `fixed bottom-5 right-5 z-50 transform transition-all duration-300 px-4 py-3 rounded-2xl shadow-xl border text-sm font-semibold flex items-center gap-3 ${
      type === 'success'
        ? 'bg-slate-900 text-emerald-400 border-slate-800'
        : 'bg-rose-900 text-rose-200 border-rose-800'
    }`;
    toast.innerHTML = `<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg><span>${msg}</span>`;
    toast.classList.remove('translate-y-20', 'opacity-0', 'pointer-events-none');
    setTimeout(() => {
      toast.classList.add('translate-y-20', 'opacity-0', 'pointer-events-none');
    }, 3500);
  }

  function updateTargetPageUI(slug) {
    currentPageSlug = slug || 'about-us';
    if (badgePageSlug) badgePageSlug.textContent = currentPageSlug.toUpperCase();
    if (formPageSlug) formPageSlug.value = currentPageSlug;

    if (pageSectionsTitle) {
      pageSectionsTitle.textContent = 'Page Sections';
    }
    if (linkViewLivePage) {
      linkViewLivePage.href = `/en/${currentPageSlug}`;
    }
  }

  async function loadAvailablePages() {
    try {
      const resp = await fetch('/visionadmin/api/pages?status=all');
      const data = await resp.json();
      const pages = data.pages || [];

      const pageList = [{ slug: 'about-us', title: 'About Us' }];
      pages.forEach(p => {
        const titleEn = typeof p.title === 'object' ? (p.title.en || p.title.ar) : p.title;
        if (!pageList.some(x => x.slug === p.slug)) {
          pageList.push({ slug: p.slug, title: titleEn || p.slug });
        }
      });

      if (!pageList.some(x => x.slug === currentPageSlug)) {
        pageList.push({ slug: currentPageSlug, title: currentPageSlug });
      }

      if (selectTargetPage) {
        selectTargetPage.innerHTML = pageList.map(p => `
          <option value="${p.slug}" ${p.slug === currentPageSlug ? 'selected' : ''}>
            ${p.title} (${p.slug})
          </option>
        `).join('');
      }
    } catch (e) {
      console.warn('Could not load pages list:', e);
    }
  }

  if (selectTargetPage) {
    selectTargetPage.addEventListener('change', () => {
      updateTargetPageUI(selectTargetPage.value);
      const newUrl = window.location.pathname + '?page=' + encodeURIComponent(currentPageSlug);
      window.history.pushState({ page: currentPageSlug }, '', newUrl);
      fetchSections();
    });
  }

  async function fetchSections() {
    try {
      updateTargetPageUI(currentPageSlug);
      const resp = await fetch(`/visionadmin/api/sections?page=${encodeURIComponent(currentPageSlug)}`);
      const data = await resp.json();
      allSections = data.sections || [];
      renderSectionsList();
      updateStats();
    } catch (err) {
      console.error(err);
      sectionsContainer.innerHTML = '<div class="p-8 text-center text-rose-500 bg-white rounded-3xl border border-rose-100 font-bold">Failed to load sections. Please refresh the page.</div>';
    }
  }

  function updateStats() {
    statTotal.textContent = allSections.length;
    statActive.textContent = allSections.filter(s => s.is_active).length;
    statInactive.textContent = allSections.filter(s => !s.is_active).length;
  }

  function renderSectionsList() {
    if (allSections.length === 0) {
      const pageName = currentPageSlug.split(/[-_]/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
      sectionsContainer.innerHTML = `
        <div class="p-12 text-center text-slate-400 bg-white rounded-3xl border border-slate-200/80 shadow-2xs">
          <div class="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto mb-3 text-xl">📄</div>
          <p class="text-sm font-black text-slate-800">No Sections Configured for "${pageName}"</p>
          <p class="text-xs text-slate-400 mt-1">Click "+ Add Section" or choose a predefined layout above to start building this page.</p>
        </div>
      `;
      return;
    }

    sectionsContainer.innerHTML = allSections.map((sec, idx) => {
      const meta = TYPE_METADATA[sec.section_type] || { 
        label: sec.section_type, 
        shortLabel: 'Section', 
        emoji: '📄', 
        badgeBg: 'bg-slate-100 text-slate-800 border-slate-200', 
        tagColor: 'bg-slate-500', 
        desc: '' 
      };

      const titleEn = typeof sec.section_title === 'object' ? (sec.section_title.en || sec.section_title.ar || '') : (sec.section_title || '');
      const titleAr = typeof sec.section_title === 'object' ? (sec.section_title.ar || '') : '';

      const subtitleEn = typeof sec.section_subtitle === 'object' ? (sec.section_subtitle.en || sec.section_subtitle.ar || '') : (sec.section_subtitle || '');
      const subtitleAr = typeof sec.section_subtitle === 'object' ? (sec.section_subtitle.ar || '') : '';

      const contentEn = typeof sec.content === 'object' ? (sec.content.en || sec.content.ar || '') : (sec.content || '');
      const contentAr = typeof sec.content === 'object' ? (sec.content.ar || '') : '';

      const btnText = typeof sec.button_text === 'object' ? (sec.button_text.en || sec.button_text.ar || '') : (sec.button_text || '');
      const btnUrl = sec.button_url || '';

      const seqNum = String(idx + 1).padStart(2, '0');
      const isFirst = idx === 0;
      const isLast = idx === allSections.length - 1;

      // Extract repeater count and render miniature structured preview chips
      let itemsCount = 0;
      let renderedItemsChips = '';

      if (sec.section_data) {
        let chipList = [];
        if (Array.isArray(sec.section_data.metrics) && sec.section_data.metrics.length > 0) {
          itemsCount = sec.section_data.metrics.length;
          chipList = sec.section_data.metrics.map(m => {
            const heading = typeof m.heading === 'object' ? (m.heading.en || m.heading.ar || '') : (m.heading || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-bold border border-slate-200/80"><span class="font-black text-slate-900">${m.number || ''}</span> ${heading}</span>`;
          });
        } else if (Array.isArray(sec.section_data.cards) && sec.section_data.cards.length > 0) {
          itemsCount = sec.section_data.cards.length;
          chipList = sec.section_data.cards.map(c => {
            const title = typeof c.title === 'object' ? (c.title.en || c.title.ar || '') : (c.title || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-semibold border border-slate-200/80 truncate max-w-[160px]">${title}</span>`;
          });
        } else if (Array.isArray(sec.section_data.features) && sec.section_data.features.length > 0) {
          itemsCount = sec.section_data.features.length;
          chipList = sec.section_data.features.map(f => {
            const heading = typeof f.heading === 'object' ? (f.heading.en || f.heading.ar || '') : (f.heading || f.title || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-semibold border border-slate-200/80 truncate max-w-[160px]">${heading}</span>`;
          });
        } else if (Array.isArray(sec.section_data.items) && sec.section_data.items.length > 0) {
          itemsCount = sec.section_data.items.length;
          chipList = sec.section_data.items.map(it => {
            const title = typeof it.title === 'object' ? (it.title.en || it.title.ar || '') : (it.title || it.heading || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-semibold border border-slate-200/80 truncate max-w-[160px]">${title}</span>`;
          });
        } else if (Array.isArray(sec.section_data)) {
          itemsCount = sec.section_data.length;
        }

        if (chipList.length > 0) {
          renderedItemsChips = chipList.slice(0, 4).join(' ') + (chipList.length > 4 ? `<span class="text-[10px] text-slate-400 font-bold px-1">+${chipList.length - 4} more</span>` : '');
        }
      }

      return `
        <div class="group relative bg-white hover:bg-slate-50/50 rounded-2xl sm:rounded-3xl p-4 sm:p-5 border border-[#E8EDE4] shadow-2xs hover:shadow-md transition-all duration-200" data-id="${sec.id}">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            
            <!-- Left Area: Media Preview + Meta + Content -->
            <div class="flex items-center gap-3.5 sm:gap-5 min-w-0 flex-1">
              
              <!-- 1. Visual Thumbnail Preview -->
              <div class="relative shrink-0 w-28 h-20 sm:w-36 sm:h-24 rounded-2xl overflow-hidden bg-slate-900 border border-slate-100 shadow-2xs">
                ${sec.image ? `
                  <img src="${sec.image}" alt="Preview" class="w-full h-full object-cover" loading="lazy" />
                ` : `
                  <div class="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-950 text-white p-2 text-center">
                    <span class="text-xl mb-0.5">${meta.emoji}</span>
                    <span class="text-[9px] font-bold text-slate-300 uppercase">${meta.shortLabel}</span>
                  </div>
                `}
              </div>

              <!-- 2. Typography Body -->
              <div class="min-w-0 flex-1 space-y-1">
                
                <!-- Type + Live Badge -->
                <div class="flex items-center gap-2">
                  <span class="text-xs font-extrabold text-[#0E1108]">${meta.label}</span>
                  ${sec.is_active 
                    ? '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-[#EAF7E2] text-[#35760F]">Live</span>'
                    : '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-500">Disabled</span>'
                  }
                </div>

                <!-- Main Section Title -->
                <h3 class="text-sm sm:text-base font-black text-[#0E1108] tracking-tight truncate">
                  ${titleEn || 'Untitled Section'}
                </h3>

                <!-- Summary Description -->
                <p class="text-xs text-slate-500 font-medium line-clamp-2 leading-relaxed max-w-3xl">
                  ${stripHtml(contentEn) || stripHtml(subtitleEn) || 'TyresVision dynamic responsive layout component.'}
                </p>

              </div>
            </div>

            <!-- Right Area: Status Badge + Edit + Delete -->
            <div class="flex items-center gap-3 shrink-0 self-end md:self-center">
              <span class="px-3 py-1 rounded-full text-xs font-bold ${sec.is_active ? 'bg-[#EAF7E2] text-[#35760F]' : 'bg-slate-100 text-slate-500'}">
                ${sec.is_active ? 'Active' : 'Disabled'}
              </span>

              <!-- Edit Button -->
              <button type="button" class="btn-edit-section inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#00A650] hover:bg-[#008f45] text-white text-xs font-bold shadow-xs hover:shadow transition active:scale-95 cursor-pointer" data-id="${sec.id}">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                <span>Edit</span>
              </button>

              <!-- Delete Button -->
              <button type="button" class="btn-delete-section w-8 h-8 rounded-xl border border-rose-200 hover:border-rose-300 text-rose-500 hover:bg-rose-50 flex items-center justify-center transition cursor-pointer" data-id="${sec.id}" title="Delete Section">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
              </button>
            </div>

          </div>
        </div>
      `;
    }).join('');

    attachRowEvents();
  }

  function attachRowEvents() {
    document.querySelectorAll('.btn-edit-section').forEach(b => {
      b.addEventListener('click', () => openEditModal(parseInt(b.dataset.id)));
    });

    document.querySelectorAll('.btn-toggle-active').forEach(b => {
      b.addEventListener('click', () => toggleActive(parseInt(b.dataset.id)));
    });

    document.querySelectorAll('.btn-delete-section').forEach(b => {
      b.addEventListener('click', () => openDeleteModal(parseInt(b.dataset.id)));
    });

    document.querySelectorAll('.btn-move-up').forEach(b => {
      b.addEventListener('click', () => moveSection(parseInt(b.dataset.id), -1));
    });

    document.querySelectorAll('.btn-move-down').forEach(b => {
      b.addEventListener('click', () => moveSection(parseInt(b.dataset.id), 1));
    });
  }

  async function moveSection(secId, direction) {
    const idx = allSections.findIndex(s => s.id === secId);
    if (idx < 0) return;
    const targetIdx = idx + direction;
    if (targetIdx < 0 || targetIdx >= allSections.length) return;

    const temp = allSections[idx];
    allSections[idx] = allSections[targetIdx];
    allSections[targetIdx] = temp;

    renderSectionsList();

    const orderedIds = allSections.map(s => s.id);
    try {
      const resp = await fetch('/visionadmin/api/sections/reorder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ordered_ids: orderedIds })
      });
      const res = await resp.json();
      if (res.success) {
        showToast('Section order updated.');
      } else {
        showToast(res.error || 'Failed to reorder', 'error');
        fetchSections();
      }
    } catch (e) {
      showToast('Error saving section order', 'error');
      fetchSections();
    }
  }

  async function toggleActive(secId) {
    try {
      const resp = await fetch(`/visionadmin/api/sections/${secId}/toggle`, { method: 'POST' });
      const data = await resp.json();
      if (data.success) {
        showToast(data.message || 'Status updated');
        fetchSections();
      } else {
        showToast(data.error || 'Failed to toggle status', 'error');
      }
    } catch (e) {
      showToast('Network error', 'error');
    }
  }

  function openDeleteModal(secId) {
    deleteSectionId = secId;
    deleteModal.classList.remove('hidden');
    setTimeout(() => {
      deleteModal.classList.remove('opacity-0');
      deleteModal.firstElementChild.classList.remove('scale-95');
    }, 10);
  }

  function closeDeleteModal() {
    deleteModal.classList.add('opacity-0');
    deleteModal.firstElementChild.classList.add('scale-95');
    setTimeout(() => {
      deleteModal.classList.add('hidden');
      deleteSectionId = null;
    }, 200);
  }

  btnCancelDelete.addEventListener('click', closeDeleteModal);

  btnConfirmDelete.addEventListener('click', async () => {
    if (!deleteSectionId) return;
    try {
      const resp = await fetch(`/visionadmin/api/sections/${deleteSectionId}`, { method: 'DELETE' });
      const data = await resp.json();
      if (data.success) {
        showToast('Section deleted successfully.');
        closeDeleteModal();
        fetchSections();
      } else {
        showToast(data.error || 'Failed to delete', 'error');
      }
    } catch (e) {
      showToast('Network error', 'error');
    }
  });

  function getSelectedType() {
    const checked = document.querySelector('input[name="section_type"]:checked');
    return checked ? checked.value : 'content_image';
  }

  function setSelectedType(type) {
    const radio = document.querySelector(`input[name="section_type"][value="${type}"]`);
    if (radio) {
      radio.checked = true;
      document.querySelectorAll('.type-card').forEach(c => {
        c.className = 'type-card flex items-center gap-2.5 p-3 rounded-2xl border-2 border-[#E8EDE4] bg-white hover:bg-[#F8FAF7] cursor-pointer transition';
      });
      const card = radio.closest('.type-card');
      if (card) {
        card.className = 'type-card flex items-center gap-2.5 p-3 rounded-2xl border-2 border-[#58B31B] bg-[#EAF7E2]/50 cursor-pointer transition';
      }
      applyTypeFormRules(type);
    }
  }

  document.querySelectorAll('input[name="section_type"]').forEach(r => {
    r.addEventListener('change', () => {
      setSelectedType(r.value);
    });
  });

  function applyTypeFormRules(type) {
    const imageWrap = document.getElementById('field-image-wrap');
    const imagePosWrap = document.getElementById('field-image-pos-wrap');
    const btnWrap = document.getElementById('field-button-wrap');
    const structWrap = document.getElementById('field-structured-data-wrap');
    const structTitle = document.getElementById('structured-data-title');

    imageWrap.classList.remove('hidden');
    imagePosWrap.classList.remove('hidden');
    btnWrap.classList.remove('hidden');
    structWrap.classList.remove('hidden');

    if (type === 'hero') {
      structTitle.textContent = 'Hero 4 Feature Highlights (Pillars)';
      imagePosWrap.classList.add('hidden');
    } else if (type === 'content_image') {
      structTitle.textContent = 'Floating Badge Info (Customer First, etc.)';
      imagePosWrap.classList.remove('hidden');
    } else if (type === 'features') {
      structTitle.textContent = 'Feature / Value Cards List';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'stats') {
      structTitle.textContent = 'Statistics Metric Counters (4 Numbers)';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'mission_vision') {
      structTitle.textContent = 'Extra Highlights (Optional)';
      imagePosWrap.classList.remove('hidden');
    } else if (type === 'cta') {
      structTitle.textContent = 'Additional CTA Data (Optional)';
      imagePosWrap.classList.add('hidden');
    }

    renderRepeaterItems();
  }

  function renderRepeaterItems() {
    const type = getSelectedType();
    if (repeaterItems.length === 0) {
      repeaterList.innerHTML = '<div class="p-4 text-center text-slate-400 bg-white rounded-xl border border-dashed border-[#E8EDE4] text-xs">No structured items added yet. Click "+ Add Item" above.</div>';
      return;
    }

    const ICON_CHOICES = [
      { val: 'disc', label: 'Tyre / Disc' },
      { val: 'award', label: 'Award / Brands' },
      { val: 'clock', label: 'Clock / 24-7' },
      { val: 'users', label: 'Users / Customer' },
      { val: 'truck', label: 'Truck / Delivery' },
      { val: 'shield', label: 'Shield / Warranty' },
      { val: 'dollar-sign', label: 'Dollar / Price' },
      { val: 'headset', label: 'Headset / Support' },
      { val: 'globe', label: 'Globe / Network' },
      { val: 'zap', label: 'Zap / Fast' },
      { val: 'heart', label: 'Heart / Care' }
    ];

    repeaterList.innerHTML = repeaterItems.map((item, i) => {
      const currentIcon = String(item.icon || '').toLowerCase();
      let matchedIcon = 'disc';
      if (currentIcon.includes('brand') || currentIcon.includes('award') || currentIcon.includes('quality') || currentIcon.includes('star')) matchedIcon = 'award';
      else if (currentIcon.includes('clock') || currentIcon.includes('time') || currentIcon.includes('24') || currentIcon.includes('access') || currentIcon.includes('online')) matchedIcon = 'clock';
      else if (currentIcon.includes('user') || currentIcon.includes('customer') || currentIcon.includes('team') || currentIcon.includes('heart')) matchedIcon = 'users';
      else if (currentIcon.includes('truck') || currentIcon.includes('delivery') || currentIcon.includes('ship')) matchedIcon = 'truck';
      else if (currentIcon.includes('shield') || currentIcon.includes('warrant') || currentIcon.includes('safe')) matchedIcon = 'shield';
      else if (currentIcon.includes('dollar') || currentIcon.includes('price') || currentIcon.includes('cost')) matchedIcon = 'dollar-sign';
      else if (currentIcon.includes('headset') || currentIcon.includes('support') || currentIcon.includes('call')) matchedIcon = 'headset';
      else if (currentIcon.includes('globe') || currentIcon.includes('network') || currentIcon.includes('uae')) matchedIcon = 'globe';
      else if (currentIcon.includes('zap') || currentIcon.includes('fast') || currentIcon.includes('speed')) matchedIcon = 'zap';
      else if (currentIcon.includes('tyre') || currentIcon.includes('wheel') || currentIcon.includes('disc')) matchedIcon = 'disc';
      else if (['disc', 'award', 'clock', 'users', 'truck', 'shield', 'dollar-sign', 'headset', 'globe', 'zap', 'heart'].includes(currentIcon)) matchedIcon = currentIcon;

      if (type === 'stats') {
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>Statistic Metric #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            
            <!-- Row 1: Number & Icon -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Metric Number / Stat *</label>
                <input type="text" placeholder="e.g. 10K+ or 24/7 or 100%" class="rep-num w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${item.number || ''}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Select Icon *</label>
                <select class="rep-icon w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition">
                  ${ICON_CHOICES.map(opt => `<option value="${opt.val}" ${matchedIcon === opt.val ? 'selected' : ''}>${opt.label}</option>`).join('')}
                </select>
              </div>
            </div>

            <!-- Row 2: Heading EN & AR -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Heading / Label (English) *</label>
                <input type="text" placeholder="e.g. Tyres Available" class="rep-head-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.heading === 'object' ? (item.heading.en || '') : (item.heading || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Heading / Label (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="مثال: إطارات متوفرة" class="rep-head-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.heading === 'object' ? (item.heading.ar || '') : ''}" />
              </div>
            </div>

            <!-- Row 3: Subtext EN & AR -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Subtext / Description (English)</label>
                <input type="text" placeholder="e.g. Quality options for different vehicles" class="rep-sub-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-medium bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.subtext === 'object' ? (item.subtext.en || '') : (item.subtext || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Subtext / Description (Arabic)</label>
                <input type="text" dir="rtl" placeholder="مثال: خيارات عالية الجودة لكافة المركبات" class="rep-sub-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-medium text-right bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.subtext === 'object' ? (item.subtext.ar || '') : ''}" />
              </div>
            </div>
          </div>
        `;
      } else {
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>Card Item #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            
            <!-- Row 1: Icon & Titles -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Select Icon *</label>
                <select class="rep-icon w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition">
                  ${ICON_CHOICES.map(opt => `<option value="${opt.val}" ${matchedIcon === opt.val ? 'selected' : ''}>${opt.label}</option>`).join('')}
                </select>
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Card Title (English) *</label>
                <input type="text" placeholder="e.g. Genuine Tyres" class="rep-title-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.title === 'object' ? (item.title.en || '') : (item.title || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Card Title (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="مثال: إطارات أصلية معتمدة" class="rep-title-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.title === 'object' ? (item.title.ar || '') : ''}" />
              </div>
            </div>

            <!-- Row 2: Descriptions -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Description (English)</label>
                <input type="text" placeholder="e.g. 100% certified authentic tyre brands" class="rep-desc-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-medium bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.desc === 'object' ? (item.desc.en || '') : (item.desc || item.sub || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Description (Arabic)</label>
                <input type="text" dir="rtl" placeholder="مثال: إطارات مضمونة وموثوقة لجميع الطرقات" class="rep-desc-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-medium text-right bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 focus:border-[#58B31B] outline-none transition" value="${typeof item.desc === 'object' ? (item.desc.ar || '') : ''}" />
              </div>
            </div>
          </div>
        `;
      }
    }).join('');

    document.querySelectorAll('.btn-remove-repeater').forEach(b => {
      b.addEventListener('click', () => {
        const idx = parseInt(b.dataset.index);
        repeaterItems.splice(idx, 1);
        renderRepeaterItems();
      });
    });
  }

  btnAddRepeaterItem.addEventListener('click', () => {
    const type = getSelectedType();
    if (type === 'stats') {
      repeaterItems.push({ number: '10K+', icon: 'users', heading: { en: 'Metric', ar: 'إحصائية' }, subtext: { en: 'Subtext', ar: 'نص' } });
    } else {
      repeaterItems.push({ icon: 'shield', title: { en: 'Card Title', ar: 'عنوان البطاقة' }, desc: { en: 'Card description text', ar: 'وصف البطاقة' } });
    }
    renderRepeaterItems();
  });

  function collectRepeaterItems() {
    const type = getSelectedType();
    const items = [];
    const rows = repeaterList.querySelectorAll('.bg-white');

    rows.forEach(row => {
      if (type === 'stats') {
        const num = row.querySelector('.rep-num')?.value.trim() || '';
        const icon = row.querySelector('.rep-icon')?.value.trim() || 'users';
        const headEn = row.querySelector('.rep-head-en')?.value.trim() || '';
        const headAr = row.querySelector('.rep-head-ar')?.value.trim() || '';
        const subEn = row.querySelector('.rep-sub-en')?.value.trim() || '';
        const subAr = row.querySelector('.rep-sub-ar')?.value.trim() || '';
        if (num || headEn) {
          items.push({
            number: num,
            icon: icon,
            heading: { en: headEn, ar: headAr || headEn },
            subtext: { en: subEn, ar: subAr || subEn }
          });
        }
      } else {
        const icon = row.querySelector('.rep-icon')?.value.trim() || 'shield';
        const titleEn = row.querySelector('.rep-title-en')?.value.trim() || '';
        const titleAr = row.querySelector('.rep-title-ar')?.value.trim() || '';
        const descEn = row.querySelector('.rep-desc-en')?.value.trim() || '';
        const descAr = row.querySelector('.rep-desc-ar')?.value.trim() || '';
        if (titleEn || titleAr) {
          items.push({
            icon: icon,
            title: { en: titleEn, ar: titleAr || titleEn },
            desc: { en: descEn, ar: descAr || descEn }
          });
        }
      }
    });
    return items;
  }

  function setLocaleTab(locale) {
    currentLocaleTab = locale;
    if (locale === 'en') {
      tabEn.className = 'px-3 py-1 rounded-lg bg-white text-[#0E1108] shadow-2xs transition';
      tabAr.className = 'px-3 py-1 rounded-lg text-slate-500 hover:text-[#0E1108] transition';

      document.getElementById('wrap-title-en').classList.remove('hidden');
      document.getElementById('wrap-title-ar').classList.add('hidden');
      document.getElementById('wrap-subtitle-en').classList.remove('hidden');
      document.getElementById('wrap-subtitle-ar').classList.add('hidden');
      const metaTitleEnWrap = document.getElementById('wrap-meta-title-en');
      const metaTitleArWrap = document.getElementById('wrap-meta-title-ar');
      const metaDescEnWrap = document.getElementById('wrap-meta-desc-en');
      const metaDescArWrap = document.getElementById('wrap-meta-desc-ar');
      if (metaTitleEnWrap) metaTitleEnWrap.classList.remove('hidden');
      if (metaTitleArWrap) metaTitleArWrap.classList.add('hidden');
      if (metaDescEnWrap) metaDescEnWrap.classList.remove('hidden');
      if (metaDescArWrap) metaDescArWrap.classList.add('hidden');
      document.getElementById('wrap-content-en').classList.remove('hidden');
      document.getElementById('wrap-content-ar').classList.add('hidden');
      document.getElementById('wrap-btn-text-en').classList.remove('hidden');
      document.getElementById('wrap-btn-text-ar').classList.add('hidden');
    } else {
      tabAr.className = 'px-3 py-1 rounded-lg bg-white text-[#0E1108] shadow-2xs transition';
      tabEn.className = 'px-3 py-1 rounded-lg text-slate-500 hover:text-[#0E1108] transition';

      document.getElementById('wrap-title-ar').classList.remove('hidden');
      document.getElementById('wrap-title-en').classList.add('hidden');
      document.getElementById('wrap-subtitle-ar').classList.remove('hidden');
      document.getElementById('wrap-subtitle-en').classList.add('hidden');
      const metaTitleEnWrap = document.getElementById('wrap-meta-title-en');
      const metaTitleArWrap = document.getElementById('wrap-meta-title-ar');
      const metaDescEnWrap = document.getElementById('wrap-meta-desc-en');
      const metaDescArWrap = document.getElementById('wrap-meta-desc-ar');
      if (metaTitleArWrap) metaTitleArWrap.classList.remove('hidden');
      if (metaTitleEnWrap) metaTitleEnWrap.classList.add('hidden');
      if (metaDescArWrap) metaDescArWrap.classList.remove('hidden');
      if (metaDescEnWrap) metaDescEnWrap.classList.add('hidden');
      document.getElementById('wrap-content-ar').classList.remove('hidden');
      document.getElementById('wrap-content-en').classList.add('hidden');
      document.getElementById('wrap-btn-text-ar').classList.remove('hidden');
      document.getElementById('wrap-btn-text-en').classList.add('hidden');
    }

    // Refresh and resize active CKEditor instance
    if (window.CKEDITOR && CKEDITOR.instances) {
      setTimeout(() => {
        if (locale === 'ar' && CKEDITOR.instances['form-content-ar']) {
          CKEDITOR.instances['form-content-ar'].resize();
        } else if (locale === 'en' && CKEDITOR.instances['form-content-en']) {
          CKEDITOR.instances['form-content-en'].resize();
        }
      }, 50);
    }
  }

  tabEn.addEventListener('click', () => setLocaleTab('en'));
  tabAr.addEventListener('click', () => setLocaleTab('ar'));

  imageFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      showToast('Uploading image…');
      const resp = await fetch('/visionadmin/api/upload-banner', {
        method: 'POST',
        body: formData
      });
      const data = await resp.json();
      if (data.url) {
        formImageUrl.value = data.url;
        updateImagePreview(data.url);
        showToast('Image uploaded successfully.');
      } else {
        showToast(data.error || 'Upload failed', 'error');
      }
    } catch (err) {
      showToast('Network error during upload', 'error');
    }
  });

  formImageUrl.addEventListener('input', () => {
    updateImagePreview(formImageUrl.value.trim());
  });

  btnClearImage.addEventListener('click', () => {
    formImageUrl.value = '';
    updateImagePreview('');
  });

  function updateImagePreview(url) {
    if (url) {
      previewImageBox.innerHTML = `<img src="${url}" alt="Preview" class="w-full h-full object-cover rounded-xl" />`;
    } else {
      previewImageBox.innerHTML = '<span class="text-[10px] text-slate-400 text-center font-bold">No Image</span>';
    }
  }

  btnAddSection.addEventListener('click', () => {
    formSectionId.value = '';
    modalTitle.textContent = 'Add Predefined Section';
    sectionForm.reset();
    if (formPageSlug) formPageSlug.value = currentPageSlug;
    setSelectedType('content_image');
    setLocaleTab('en');
    setEditorContent('form-content-en', '');
    setEditorContent('form-content-ar', '');
    if (formMetaTitleEn) formMetaTitleEn.value = '';
    if (formMetaTitleAr) formMetaTitleAr.value = '';
    if (formMetaDescEn) formMetaDescEn.value = '';
    if (formMetaDescAr) formMetaDescAr.value = '';
    updateImagePreview('');
    repeaterItems = [];
    formSortOrder.value = allSections.length + 1;
    formIsActive.checked = true;
    renderRepeaterItems();
    openModal();
  });

  // Quick Add from Predefined Layouts Catalog
  document.querySelectorAll('.btn-quick-add-layout').forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.dataset.type || 'content_image';
      formSectionId.value = '';
      modalTitle.textContent = `Add Predefined Section (${TYPE_METADATA[type]?.label || type})`;
      sectionForm.reset();
      if (formPageSlug) formPageSlug.value = currentPageSlug;
      setSelectedType(type);
      setLocaleTab('en');
      setEditorContent('form-content-en', '');
      setEditorContent('form-content-ar', '');
      if (formMetaTitleEn) formMetaTitleEn.value = '';
      if (formMetaTitleAr) formMetaTitleAr.value = '';
      if (formMetaDescEn) formMetaDescEn.value = '';
      if (formMetaDescAr) formMetaDescAr.value = '';
      updateImagePreview('');
      repeaterItems = [];
      formSortOrder.value = allSections.length + 1;
      formIsActive.checked = true;
      renderRepeaterItems();
      openModal();
    });
  });

  function openEditModal(secId) {
    const sec = allSections.find(s => s.id === secId);
    if (!sec) return;

    formSectionId.value = sec.id;
    modalTitle.textContent = `Edit ${TYPE_METADATA[sec.section_type]?.label || 'Section'}`;
    if (formPageSlug) formPageSlug.value = sec.page_slug || currentPageSlug;

    formTitleEn.value = typeof sec.section_title === 'object' ? (sec.section_title.en || '') : (sec.section_title || '');
    formTitleAr.value = typeof sec.section_title === 'object' ? (sec.section_title.ar || '') : '';

    formSubtitleEn.value = typeof sec.section_subtitle === 'object' ? (sec.section_subtitle.en || '') : (sec.section_subtitle || '');
    formSubtitleAr.value = typeof sec.section_subtitle === 'object' ? (sec.section_subtitle.ar || '') : '';

    if (formMetaTitleEn) formMetaTitleEn.value = typeof sec.meta_title === 'object' ? (sec.meta_title?.en || '') : (sec.meta_title || '');
    if (formMetaTitleAr) formMetaTitleAr.value = typeof sec.meta_title === 'object' ? (sec.meta_title?.ar || '') : '';

    if (formMetaDescEn) formMetaDescEn.value = typeof sec.meta_description === 'object' ? (sec.meta_description?.en || '') : (sec.meta_description || '');
    if (formMetaDescAr) formMetaDescAr.value = typeof sec.meta_description === 'object' ? (sec.meta_description?.ar || '') : '';

    const rawContentEn = typeof sec.content === 'object' ? (sec.content.en || '') : (sec.content || '');
    const rawContentAr = typeof sec.content === 'object' ? (sec.content.ar || '') : '';
    setEditorContent('form-content-en', rawContentEn);
    setEditorContent('form-content-ar', rawContentAr);

    formImageUrl.value = sec.image || '';
    updateImagePreview(sec.image || '');

    const imgPosRadio = document.querySelector(`input[name="image_position"][value="${sec.image_position || 'right'}"]`);
    if (imgPosRadio) imgPosRadio.checked = true;

    formBtnTextEn.value = typeof sec.button_text === 'object' ? (sec.button_text.en || '') : (sec.button_text || '');
    formBtnTextAr.value = typeof sec.button_text === 'object' ? (sec.button_text.ar || '') : '';
    formBtnUrl.value = sec.button_url || '';

    formSortOrder.value = sec.sort_order || 1;
    formIsActive.checked = Boolean(sec.is_active);

    const sData = sec.section_data || {};
    if (sData.metrics && Array.isArray(sData.metrics)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.metrics));
    } else if (sData.cards && Array.isArray(sData.cards)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.cards));
    } else if (sData.features && Array.isArray(sData.features)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.features));
    } else {
      repeaterItems = [];
    }

    setSelectedType(sec.section_type);
    setLocaleTab('en');
    openModal();
  }

  function openModal() {
    sectionModal.classList.remove('hidden');
    setTimeout(() => {
      sectionModal.classList.remove('opacity-0');
      sectionModalBox.classList.remove('scale-95');
      if (window.CKEDITOR && CKEDITOR.instances) {
        if (CKEDITOR.instances['form-content-en']) CKEDITOR.instances['form-content-en'].resize();
        if (CKEDITOR.instances['form-content-ar']) CKEDITOR.instances['form-content-ar'].resize();
      }
    }, 100);
  }

  function closeModal() {
    sectionModal.classList.add('opacity-0');
    sectionModalBox.classList.add('scale-95');
    setTimeout(() => {
      sectionModal.classList.add('hidden');
    }, 200);
  }

  btnCloseModal.addEventListener('click', closeModal);
  btnCancelModal.addEventListener('click', closeModal);

  btnSaveSection.addEventListener('click', async () => {
    const secId = formSectionId.value;
    const isEdit = Boolean(secId);
    const sectionType = getSelectedType();

    // Force update from all CKEditor instances
    if (window.CKEDITOR && CKEDITOR.instances) {
      for (const instName in CKEDITOR.instances) {
        try {
          CKEDITOR.instances[instName].updateElement();
        } catch (e) {}
      }
    }

    const titleEn = formTitleEn.value.trim();
    const titleAr = formTitleAr.value.trim() || titleEn;
    if (!titleEn && !titleAr) {
      showToast('Section title is required.', 'error');
      setLocaleTab('en');
      formTitleEn.focus();
      return;
    }

    const subtitleEn = formSubtitleEn.value.trim();
    const subtitleAr = formSubtitleAr.value.trim() || subtitleEn;

    const metaTitleEn = formMetaTitleEn ? formMetaTitleEn.value.trim() : '';
    const metaTitleAr = formMetaTitleAr ? formMetaTitleAr.value.trim() : '';

    const metaDescEn = formMetaDescEn ? formMetaDescEn.value.trim() : '';
    const metaDescAr = formMetaDescAr ? formMetaDescAr.value.trim() : '';

    const contentEn = getEditorContent('form-content-en').trim();
    const contentAr = getEditorContent('form-content-ar').trim() || contentEn;

    const btnTextEn = formBtnTextEn.value.trim();
    const btnTextAr = formBtnTextAr.value.trim() || btnTextEn;
    const btnUrl = formBtnUrl.value.trim();

    const imgPos = document.querySelector('input[name="image_position"]:checked')?.value || 'right';

    const repData = collectRepeaterItems();
    const sectionData = {};
    if (sectionType === 'stats') {
      sectionData.metrics = repData;
    } else if (sectionType === 'features') {
      sectionData.cards = repData;
    } else if (sectionType === 'hero') {
      sectionData.features = repData;
    } else {
      if (repData.length > 0) sectionData.items = repData;
    }

    const targetSlug = formPageSlug?.value?.trim() || currentPageSlug || 'about-us';

    const payload = {
      page_slug: targetSlug,
      section_type: sectionType,
      section_title: { en: titleEn, ar: titleAr },
      section_subtitle: { en: subtitleEn, ar: subtitleAr },
      meta_title: { en: metaTitleEn, ar: metaTitleAr },
      meta_description: { en: metaDescEn, ar: metaDescAr },
      content: { en: contentEn, ar: contentAr },
      image: formImageUrl.value.trim() || null,
      image_position: imgPos,
      button_text: { en: btnTextEn, ar: btnTextAr },
      button_url: btnUrl || null,
      section_data: sectionData,
      sort_order: parseInt(formSortOrder.value) || 1,
      is_active: formIsActive.checked
    };

    btnSaveSection.disabled = true;
    btnSaveSection.innerHTML = '<div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div><span>Saving…</span>';

    try {
      const url = isEdit ? `/visionadmin/api/sections/${secId}` : '/visionadmin/api/sections';
      const method = isEdit ? 'PUT' : 'POST';

      const resp = await fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await resp.json();

      if (data.success) {
        showToast(isEdit ? 'Section updated successfully.' : 'Section created successfully.');
        closeModal();
        fetchSections();
      } else {
        showToast(data.error || 'Failed to save section', 'error');
      }
    } catch (e) {
      showToast('Network error while saving', 'error');
    } finally {
      btnSaveSection.disabled = false;
      btnSaveSection.innerHTML = '<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg><span>Save Section</span>';
    }
  });

  loadAvailablePages();
  fetchSections();
});

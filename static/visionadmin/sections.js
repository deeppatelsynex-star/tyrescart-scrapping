/**
 * static/visionadmin/sections.js
 * VisionAdmin CMS — Dynamic Page Sections Controller (Home & Custom Pages)
 */

document.addEventListener('DOMContentLoaded', () => {
  let allSections = [];
  let currentLocaleTab = 'en';
  let deleteSectionId = null;
  let repeaterItems = [];
  let extraSectionData = {};

  const TYPE_METADATA = {
    hero: { 
      label: 'Hero Banner', 
      shortLabel: 'Hero', 
      emoji: '🦸', 
      badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-200/80',
      tagColor: 'bg-emerald-500',
      desc: 'Hero Banner with Quote Card & Trust Badges' 
    },
    stats: { 
      label: 'Statistics Grid', 
      shortLabel: 'Stats', 
      emoji: '📊', 
      badgeBg: 'bg-indigo-50 text-indigo-800 border-indigo-200/80',
      tagColor: 'bg-indigo-500',
      desc: 'Atmospheric 4-Metric Stats Band' 
    },
    features: { 
      label: 'Why / Features', 
      shortLabel: 'Features', 
      emoji: '✨', 
      badgeBg: 'bg-purple-50 text-purple-800 border-purple-200/80',
      tagColor: 'bg-purple-500',
      desc: '6 Value Cards with Icons + WhatsApp/Call' 
    },
    services: { 
      label: 'Car Care Services', 
      shortLabel: 'Services', 
      emoji: '🛠️', 
      badgeBg: 'bg-teal-50 text-teal-800 border-teal-200/80',
      tagColor: 'bg-teal-500',
      desc: '16 Car Care Services Grid' 
    },
    how_it_works: { 
      label: 'How It Works', 
      shortLabel: 'Steps', 
      emoji: '🔢', 
      badgeBg: 'bg-cyan-50 text-cyan-800 border-cyan-200/80',
      tagColor: 'bg-cyan-500',
      desc: '4-Step Process Flow with WhatsApp/Call' 
    },
    brands: { 
      label: 'Brands List', 
      shortLabel: 'Brands', 
      emoji: '🏷️', 
      badgeBg: 'bg-amber-50 text-amber-800 border-amber-200/80',
      tagColor: 'bg-amber-500',
      desc: '60+ Brand Pills & Logos' 
    },
    testimonials: { 
      label: 'Customer Reviews', 
      shortLabel: 'Reviews', 
      emoji: '⭐', 
      badgeBg: 'bg-yellow-50 text-yellow-800 border-yellow-200/80',
      tagColor: 'bg-yellow-500',
      desc: 'Customer Star Reviews Grid' 
    },
    faq: { 
      label: 'FAQ Accordion', 
      shortLabel: 'FAQ', 
      emoji: '❓', 
      badgeBg: 'bg-sky-50 text-sky-800 border-sky-200/80',
      tagColor: 'bg-sky-500',
      desc: 'Collapsible Q&A Accordion List' 
    },
    cta: { 
      label: 'CTA Action Box', 
      shortLabel: 'CTA Box', 
      emoji: '🚀', 
      badgeBg: 'bg-rose-50 text-rose-800 border-rose-200/80',
      tagColor: 'bg-rose-500',
      desc: 'Bottom Action Card with Buttons & Footer Note' 
    },
    content_image: { 
      label: 'Content + Image', 
      shortLabel: '2-Column', 
      emoji: '🖼️', 
      badgeBg: 'bg-blue-50 text-blue-800 border-blue-200/80',
      tagColor: 'bg-blue-500',
      desc: 'Narrative Story with Media & Floating Badge' 
    },
    mission_vision: { 
      label: 'Mission & Team', 
      shortLabel: 'Mission', 
      emoji: '🎯', 
      badgeBg: 'bg-orange-50 text-orange-800 border-orange-200/80',
      tagColor: 'bg-orange-500',
      desc: 'Specialist Team / Mission 2-Column Split' 
    }
  };

  // Target Page handling (Query param ?page=...)
  const urlParams = new URLSearchParams(window.location.search);
  let currentPageSlug = urlParams.get('page') || 'home';

  const selectTargetPage = document.getElementById('select-target-page');
  const btnTargetPageDropdown = document.getElementById('btn-target-page-dropdown');
  const targetPageDropdownMenu = document.getElementById('target-page-dropdown-menu');
  const targetPageCurrentLabel = document.getElementById('target-page-current-label');
  const targetPageChevron = document.getElementById('target-page-chevron');
  const targetPageOptionsList = document.getElementById('target-page-options-list');
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

  function updateTargetPageUI(slug, title) {
    currentPageSlug = slug || 'home';
    if (badgePageSlug) badgePageSlug.textContent = currentPageSlug.toUpperCase();
    if (formPageSlug) formPageSlug.value = currentPageSlug;

    if (targetPageCurrentLabel) {
      if (title) {
        targetPageCurrentLabel.textContent = `${title} (${currentPageSlug})`;
      } else {
        const prettySlug = currentPageSlug === 'home' ? 'Home Page' : currentPageSlug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        targetPageCurrentLabel.textContent = `${prettySlug} (${currentPageSlug})`;
      }
    }

    if (pageSectionsTitle) {
      pageSectionsTitle.textContent = currentPageSlug === 'home' ? 'Home Page Sections' : 'Page Sections';
    }
    if (linkViewLivePage) {
      linkViewLivePage.href = currentPageSlug === 'home' ? '/en' : (currentPageSlug === 'about-us' ? '/en/about-us' : `/en/${currentPageSlug}`);
    }
  }

  function selectPage(slug, title) {
    if (targetPageDropdownMenu) targetPageDropdownMenu.classList.add('hidden');
    if (targetPageChevron) {
      targetPageChevron.classList.remove('rotate-180');
      targetPageChevron.classList.remove('text-[#35760F]');
    }
    if (btnTargetPageDropdown) btnTargetPageDropdown.setAttribute('aria-expanded', 'false');

    updateTargetPageUI(slug, title);
    if (selectTargetPage) selectTargetPage.value = slug;

    const newUrl = window.location.pathname + '?page=' + encodeURIComponent(currentPageSlug);
    window.history.pushState({ page: currentPageSlug }, '', newUrl);

    loadAvailablePages();
    fetchSections();
  }

  async function loadAvailablePages() {
    try {
      const resp = await fetch('/visionadmin/api/pages?status=all');
      if (resp.status === 401 || resp.status === 403) {
        window.location.href = `/visionadmin/login?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }
      const data = await resp.json();
      const pages = data.pages || [];

      const pageList = [
        { slug: 'home', title: 'Home Page' },
        { slug: 'about-us', title: 'About Us' }
      ];

      pages.forEach(p => {
        const titleEn = typeof p.title === 'object' ? (p.title.en || p.title.ar) : p.title;
        if (!pageList.some(x => x.slug === p.slug)) {
          pageList.push({ slug: p.slug, title: titleEn || p.slug });
        }
      });

      if (!pageList.some(x => x.slug === currentPageSlug)) {
        pageList.push({ slug: currentPageSlug, title: currentPageSlug });
      }

      const activePage = pageList.find(p => p.slug === currentPageSlug) || { slug: currentPageSlug, title: currentPageSlug };
      updateTargetPageUI(activePage.slug, activePage.title);

      if (targetPageOptionsList) {
        targetPageOptionsList.innerHTML = pageList.map(p => {
          const isSelected = p.slug === currentPageSlug;
          return `
            <button 
              type="button" 
              class="w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all text-left cursor-pointer ${
                isSelected 
                  ? 'bg-[#EAF7E2] text-[#0E1108] font-extrabold' 
                  : 'text-slate-700 hover:bg-slate-50 hover:text-[#0E1108]'
              }"
              data-slug="${p.slug}"
              data-title="${p.title}"
            >
              <div class="flex items-center gap-2 min-w-0">
                <span class="w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-[#58B31B]' : 'bg-slate-300'} shrink-0"></span>
                <span class="truncate">${p.title} <span class="text-[11px] text-slate-400 font-semibold">(${p.slug})</span></span>
              </div>
              ${isSelected ? '<svg class="w-4 h-4 text-[#35760F] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>' : ''}
            </button>
          `;
        }).join('');

        targetPageOptionsList.querySelectorAll('button[data-slug]').forEach(btn => {
          btn.addEventListener('click', () => {
            const slug = btn.getAttribute('data-slug');
            const title = btn.getAttribute('data-title');
            selectPage(slug, title);
          });
        });
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

  if (btnTargetPageDropdown && targetPageDropdownMenu) {
    btnTargetPageDropdown.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = targetPageDropdownMenu.classList.toggle('hidden');
      btnTargetPageDropdown.setAttribute('aria-expanded', !isHidden);
      if (targetPageChevron) {
        targetPageChevron.classList.toggle('rotate-180', !isHidden);
        targetPageChevron.classList.toggle('text-[#35760F]', !isHidden);
      }
    });

    document.addEventListener('click', (e) => {
      if (!targetPageDropdownMenu.contains(e.target) && !btnTargetPageDropdown.contains(e.target)) {
        targetPageDropdownMenu.classList.add('hidden');
        btnTargetPageDropdown.setAttribute('aria-expanded', 'false');
        if (targetPageChevron) {
          targetPageChevron.classList.remove('rotate-180', 'text-[#35760F]');
        }
      }
    });
  }

  async function fetchSections() {
    try {
      updateTargetPageUI(currentPageSlug);
      const resp = await fetch(`/visionadmin/api/sections?page=${encodeURIComponent(currentPageSlug)}`);
      if (resp.status === 401 || resp.status === 403) {
        window.location.href = `/visionadmin/login?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }
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
      const pageName = currentPageSlug === 'home' ? 'Home Page' : currentPageSlug.split(/[-_]/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
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
      const contentEn = typeof sec.content === 'object' ? (sec.content.en || sec.content.ar || '') : (sec.content || '');

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
            const heading = typeof m.label === 'object' ? (m.label.en || m.label.ar || '') : (m.heading?.en || m.heading || m.label || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-bold border border-slate-200/80"><span class="font-black text-slate-900">${m.number || ''}</span> ${heading}</span>`;
          });
        } else if (Array.isArray(sec.section_data.cards) && sec.section_data.cards.length > 0) {
          itemsCount = sec.section_data.cards.length;
          chipList = sec.section_data.cards.map(c => {
            const title = typeof c.title === 'object' ? (c.title.en || c.title.ar || '') : (c.title || '');
            return `<span class="px-2 py-0.5 rounded-md bg-slate-100/90 text-slate-700 text-[10px] font-semibold border border-slate-200/80 truncate max-w-[160px]">${title}</span>`;
          });
        } else if (Array.isArray(sec.section_data.services) && sec.section_data.services.length > 0) {
          itemsCount = sec.section_data.services.length;
          chipList = sec.section_data.services.map(s => {
            const name = typeof s.name === 'object' ? (s.name.en || s.name.ar || '') : (s.name || s || '');
            return `<span class="px-2 py-0.5 rounded-md bg-teal-50 text-teal-800 text-[10px] font-semibold border border-teal-200/80 truncate max-w-[160px]">${name}</span>`;
          });
        } else if (Array.isArray(sec.section_data.steps) && sec.section_data.steps.length > 0) {
          itemsCount = sec.section_data.steps.length;
          chipList = sec.section_data.steps.map(st => {
            const title = typeof st.title === 'object' ? (st.title.en || st.title.ar || '') : (st.title || '');
            return `<span class="px-2 py-0.5 rounded-md bg-cyan-50 text-cyan-800 text-[10px] font-semibold border border-cyan-200/80 truncate max-w-[160px]">Step ${st.step_number || ''}: ${title}</span>`;
          });
        } else if (Array.isArray(sec.section_data.brands) && sec.section_data.brands.length > 0) {
          itemsCount = sec.section_data.brands.length;
          chipList = sec.section_data.brands.map(b => `<span class="px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 text-[10px] font-semibold border border-amber-200/80">${b}</span>`);
        } else if (Array.isArray(sec.section_data.reviews) && sec.section_data.reviews.length > 0) {
          itemsCount = sec.section_data.reviews.length;
          chipList = sec.section_data.reviews.map(r => {
            const auth = typeof r.author === 'object' ? (r.author.en || r.author.ar || '') : (r.author || 'Review');
            return `<span class="px-2 py-0.5 rounded-md bg-yellow-50 text-yellow-800 text-[10px] font-semibold border border-yellow-200/80">★ 5 - ${auth}</span>`;
          });
        } else if (Array.isArray(sec.section_data.faqs) && sec.section_data.faqs.length > 0) {
          itemsCount = sec.section_data.faqs.length;
          chipList = sec.section_data.faqs.map(f => {
            const q = typeof f.question === 'object' ? (f.question.en || f.question.ar || '') : (f.question || '');
            return `<span class="px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 text-[10px] font-semibold border border-sky-200/80 truncate max-w-[180px]">? ${q}</span>`;
          });
        } else if (Array.isArray(sec.section_data.badges) && sec.section_data.badges.length > 0) {
          itemsCount = sec.section_data.badges.length;
          chipList = sec.section_data.badges.map(b => {
            const txt = typeof b.text === 'object' ? (b.text.en || b.text.ar || '') : (b.text || b || '');
            return `<span class="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 text-[10px] font-semibold border border-emerald-200/80">✓ ${txt}</span>`;
          });
        } else if (Array.isArray(sec.section_data.features) && sec.section_data.features.length > 0) {
          itemsCount = sec.section_data.features.length;
        }

        if (chipList.length > 0) {
          renderedItemsChips = chipList.slice(0, 4).join(' ') + (chipList.length > 4 ? `<span class="text-[10px] text-slate-400 font-bold px-1">+${chipList.length - 4} more</span>` : '');
        }
      }

      return `
        <div class="section-row bg-white rounded-3xl border border-slate-200/80 hover:border-slate-300 shadow-xs hover:shadow-md transition-all duration-200 overflow-hidden group" data-id="${sec.id}" data-type="${sec.section_type}">
          <div class="p-5 sm:p-6 flex flex-col md:flex-row md:items-center gap-5 justify-between">
            
            <!-- Left Side: Order Handle, Icon & Details -->
            <div class="flex items-start gap-4 min-w-0 flex-1">
              
              <!-- Reorder Buttons -->
              <div class="flex flex-col items-center justify-center gap-1 shrink-0 pt-0.5">
                <button type="button" class="btn-move-up w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition disabled:opacity-30 disabled:pointer-events-none cursor-pointer" data-id="${sec.id}" ${isFirst ? 'disabled' : ''} title="Move Up">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>
                </button>
                <span class="text-[11px] font-black text-slate-400 select-none">${seqNum}</span>
                <button type="button" class="btn-move-down w-6 h-6 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 flex items-center justify-center transition disabled:opacity-30 disabled:pointer-events-none cursor-pointer" data-id="${sec.id}" ${isLast ? 'disabled' : ''} title="Move Down">
                  <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
                </button>
              </div>

              <!-- Layout Icon Badge -->
              <div class="w-12 h-12 rounded-2xl ${meta.badgeBg} border flex items-center justify-center text-xl shrink-0 shadow-2xs">
                ${meta.emoji}
              </div>

              <!-- Title, Subtitle & Meta -->
              <div class="min-w-0 flex-1 space-y-1.5">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold tracking-wider uppercase ${meta.badgeBg} border">
                    ${meta.label}
                  </span>
                  ${subtitleEn ? `<span class="text-xs font-bold text-[#00A650] tracking-wide uppercase">· ${subtitleEn}</span>` : ''}
                  ${!sec.is_active ? '<span class="px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 text-[10px] font-bold">Inactive / Hidden</span>' : ''}
                </div>

                <h3 class="text-base font-black text-[#0E1108] truncate tracking-tight">
                  ${titleEn || '<span class="text-slate-400 italic">Untitled Section</span>'}
                </h3>

                ${titleAr ? `<p class="text-xs font-bold text-slate-500 truncate" dir="rtl">${titleAr}</p>` : ''}

                ${contentEn ? `<p class="text-xs text-slate-500 line-clamp-1">${contentEn.replace(/<[^>]*>/g, '')}</p>` : ''}

                ${renderedItemsChips ? `<div class="flex flex-wrap items-center gap-1.5 pt-1">${renderedItemsChips}</div>` : ''}
              </div>

            </div>

            <!-- Right Side Actions -->
            <div class="flex items-center gap-2.5 shrink-0 self-end md:self-center pt-2 md:pt-0 border-t md:border-t-0 border-slate-100 w-full md:w-auto justify-end">
              
              <!-- Toggle Active Switch -->
              <span class="inline-flex items-center gap-2 mr-2">
                <button type="button" class="btn-toggle-active relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${sec.is_active ? 'bg-[#00A650]' : 'bg-slate-200'}" data-id="${sec.id}" role="switch" aria-checked="${sec.is_active}">
                  <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${sec.is_active ? 'translate-x-5' : 'translate-x-0'}"></span>
                </button>
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
    return checked ? checked.value : 'hero';
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
      structTitle.textContent = 'Hero Badges & Trust Highlights';
      imageWrap.classList.add('hidden');
      imagePosWrap.classList.add('hidden');
    } else if (type === 'stats') {
      structTitle.textContent = 'Statistics Metric Counters (4 Numbers)';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'features') {
      structTitle.textContent = 'Why / Value Cards (6 Cards)';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'services') {
      structTitle.textContent = 'Car Care Services List';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'how_it_works') {
      structTitle.textContent = 'How It Works Steps (4 Steps)';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'brands') {
      structTitle.textContent = 'Brand Names List';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'testimonials') {
      structTitle.textContent = 'Customer Star Reviews';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'faq') {
      structTitle.textContent = 'FAQ Accordion Questions & Answers';
      imageWrap.classList.add('hidden');
      btnWrap.classList.add('hidden');
    } else if (type === 'cta') {
      structTitle.textContent = 'Extra CTA Info & Note';
      imageWrap.classList.add('hidden');
      imagePosWrap.classList.add('hidden');
    } else if (type === 'content_image') {
      structTitle.textContent = 'Additional Highlights';
      imagePosWrap.classList.remove('hidden');
    } else if (type === 'mission_vision') {
      structTitle.textContent = 'Extra Highlights (Optional)';
      imagePosWrap.classList.remove('hidden');
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
      { val: 'shield', label: 'Shield / Warranty' },
      { val: 'dollar', label: 'Dollar / Price' },
      { val: 'truck', label: 'Truck / Delivery' },
      { val: 'clock', label: 'Clock / 24-7' },
      { val: 'award', label: 'Award / Brands' },
      { val: 'zap', label: 'Zap / Fast' },
      { val: 'phone', label: 'Phone / Contact' },
      { val: 'globe', label: 'Globe / Network' },
      { val: 'tyre', label: 'Tyre / Wheel' }
    ];

    repeaterList.innerHTML = repeaterItems.map((item, i) => {
      const currentIcon = String(item.icon || '').toLowerCase();
      let matchedIcon = 'shield';
      if (currentIcon.includes('dollar') || currentIcon.includes('price')) matchedIcon = 'dollar';
      else if (currentIcon.includes('truck') || currentIcon.includes('deliver') || currentIcon.includes('van')) matchedIcon = 'truck';
      else if (currentIcon.includes('clock') || currentIcon.includes('time')) matchedIcon = 'clock';
      else if (currentIcon.includes('award') || currentIcon.includes('brand')) matchedIcon = 'award';
      else if (currentIcon.includes('zap') || currentIcon.includes('fast')) matchedIcon = 'zap';
      else if (currentIcon.includes('phone') || currentIcon.includes('call')) matchedIcon = 'phone';
      else if (currentIcon.includes('globe') || currentIcon.includes('network') || currentIcon.includes('uae')) matchedIcon = 'globe';
      else if (currentIcon.includes('tyre') || currentIcon.includes('wheel')) matchedIcon = 'tyre';
      else if (currentIcon.includes('shield') || currentIcon.includes('warrant')) matchedIcon = 'shield';

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
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Metric Number *</label>
                <input type="text" placeholder="e.g. 60+ or 7,000+" class="rep-num w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 outline-none" value="${item.number || ''}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Label (English) *</label>
                <input type="text" placeholder="e.g. Tyre brands" class="rep-head-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 outline-none" value="${typeof item.label === 'object' ? (item.label.en || '') : (item.heading?.en || item.label || item.heading || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Label (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="مثال: علامة تجارية" class="rep-head-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white focus:ring-2 focus:ring-[#58B31B]/15 outline-none" value="${typeof item.label === 'object' ? (item.label.ar || '') : (item.heading?.ar || '')}" />
              </div>
            </div>
          </div>
        `;
      } else if (type === 'services') {
        return `
          <div class="p-3 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs flex items-center gap-3">
            <span class="w-2 h-2 rounded-full bg-[#58B31B] shrink-0"></span>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 flex-1">
              <input type="text" placeholder="Service Name (English)" class="rep-svc-en px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.name === 'object' ? (item.name.en || '') : (item.name || item || '')}" />
              <input type="text" dir="rtl" placeholder="اسم الخدمة (عربي)" class="rep-svc-ar px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.name === 'object' ? (item.name.ar || '') : ''}" />
            </div>
            <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">✕</button>
          </div>
        `;
      } else if (type === 'brands') {
        return `
          <div class="p-3 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs flex items-center gap-3">
            <span class="text-xs font-black text-slate-400">#${i + 1}</span>
            <input type="text" placeholder="Brand Name (e.g. Michelin)" class="rep-brand-name flex-1 px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item === 'string' ? item : (item.name || '')}" />
            <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">✕</button>
          </div>
        `;
      } else if (type === 'faq') {
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>FAQ Question #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Question (English) *</label>
                <input type="text" placeholder="e.g. How do I find my tyre size?" class="rep-q-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.question === 'object' ? (item.question.en || '') : (item.question || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Question (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="مثال: كيف أجد مقاس إطاري؟" class="rep-q-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.question === 'object' ? (item.question.ar || '') : ''}" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Answer (English) *</label>
                <textarea rows="2" placeholder="Answer content..." class="rep-a-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs bg-[#F8FAF7] focus:bg-white outline-none">${typeof item.answer === 'object' ? (item.answer.en || '') : (item.answer || '')}</textarea>
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Answer (Arabic) *</label>
                <textarea rows="2" dir="rtl" placeholder="نص الإجابة..." class="rep-a-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs text-right bg-[#F8FAF7] focus:bg-white outline-none">${typeof item.answer === 'object' ? (item.answer.ar || '') : ''}</textarea>
              </div>
            </div>
          </div>
        `;
      } else if (type === 'testimonials') {
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>Customer Review #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Author Name (English)</label>
                <input type="text" placeholder="Verified customer" class="rep-rev-auth-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.author === 'object' ? (item.author.en || '') : (item.author || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Author Name (Arabic)</label>
                <input type="text" dir="rtl" placeholder="عميل موثوق" class="rep-rev-auth-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.author === 'object' ? (item.author.ar || '') : ''}" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Customer Quote (English) *</label>
                <textarea rows="2" placeholder="Quote text..." class="rep-rev-quote-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs bg-[#F8FAF7] focus:bg-white outline-none">${typeof item.quote === 'object' ? (item.quote.en || '') : (item.quote || '')}</textarea>
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Customer Quote (Arabic) *</label>
                <textarea rows="2" dir="rtl" placeholder="نص التقييم..." class="rep-rev-quote-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs text-right bg-[#F8FAF7] focus:bg-white outline-none">${typeof item.quote === 'object' ? (item.quote.ar || '') : ''}</textarea>
              </div>
            </div>
          </div>
        `;
      } else if (type === 'how_it_works') {
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>Step #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Icon</label>
                <select class="rep-icon w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none">
                  ${ICON_CHOICES.map(opt => `<option value="${opt.val}" ${matchedIcon === opt.val ? 'selected' : ''}>${opt.label}</option>`).join('')}
                </select>
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Step Title (English) *</label>
                <input type="text" placeholder="Send your size" class="rep-title-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.title === 'object' ? (item.title.en || '') : (item.title || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Step Title (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="أرسل مقاس إطارك" class="rep-title-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.title === 'object' ? (item.title.ar || '') : ''}" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Step Description (English)</label>
                <input type="text" placeholder="WhatsApp us..." class="rep-desc-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.description === 'object' ? (item.description.en || '') : (item.description || item.desc || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Step Description (Arabic)</label>
                <input type="text" dir="rtl" placeholder="راسلنا على واتساب..." class="rep-desc-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.description === 'object' ? (item.description.ar || '') : ''}" />
              </div>
            </div>
          </div>
        `;
      } else {
        // Default Cards (Why / Features / Hero Badges)
        return `
          <div class="p-4 bg-white rounded-2xl border border-[#E8EDE4] shadow-2xs space-y-3">
            <div class="flex items-center justify-between pb-2 border-b border-[#E8EDE4]">
              <span class="text-[11px] font-black uppercase tracking-wider text-[#0E1108] flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-[#58B31B]"></span>
                <span>Item / Card #${i + 1}</span>
              </span>
              <button type="button" class="btn-remove-repeater text-rose-600 hover:text-rose-800 text-xs font-bold transition cursor-pointer" data-index="${i}">Remove</button>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Icon</label>
                <select class="rep-icon w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none">
                  ${ICON_CHOICES.map(opt => `<option value="${opt.val}" ${matchedIcon === opt.val ? 'selected' : ''}>${opt.label}</option>`).join('')}
                </select>
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Title / Text (English) *</label>
                <input type="text" placeholder="e.g. Genuine tyres only" class="rep-title-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.title === 'object' ? (item.title.en || '') : (item.title || item.text?.en || item.text || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Title / Text (Arabic) *</label>
                <input type="text" dir="rtl" placeholder="مثال: إطارات أصلية 100%" class="rep-title-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs font-bold text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.title === 'object' ? (item.title.ar || '') : (item.text?.ar || '')}" />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Description (English)</label>
                <input type="text" placeholder="Details..." class="rep-desc-en w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.description === 'object' ? (item.description.en || '') : (item.description || item.desc?.en || item.desc || '')}" />
              </div>
              <div>
                <label class="block text-[10px] font-black uppercase tracking-wider text-slate-600 mb-1">Description (Arabic)</label>
                <input type="text" dir="rtl" placeholder="التفاصيل..." class="rep-desc-ar w-full px-3 py-2 rounded-xl border border-[#E8EDE4] text-xs text-right bg-[#F8FAF7] focus:bg-white outline-none" value="${typeof item.description === 'object' ? (item.description.ar || '') : (item.desc?.ar || '')}" />
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
      repeaterItems.push({ number: '10+', label: { en: 'New Metric', ar: 'إحصائية جديدة' }, icon: 'award' });
    } else if (type === 'services') {
      repeaterItems.push({ name: { en: 'New Service', ar: 'خدمة جديدة' } });
    } else if (type === 'brands') {
      repeaterItems.push({ name: 'Brand Name' });
    } else if (type === 'faq') {
      repeaterItems.push({ question: { en: 'Question?', ar: 'سؤال؟' }, answer: { en: 'Answer text', ar: 'نص الإجابة' } });
    } else if (type === 'testimonials') {
      repeaterItems.push({ rating: 5, author: { en: 'Verified customer', ar: 'عميل موثوق' }, quote: { en: 'Great service!', ar: 'خدمة ممتازة!' } });
    } else if (type === 'how_it_works') {
      repeaterItems.push({ step_number: repeaterItems.length + 1, icon: 'phone', title: { en: 'Step Title', ar: 'عنوان الخطوة' }, description: { en: 'Description', ar: 'الوصف' } });
    } else {
      repeaterItems.push({ icon: 'shield', title: { en: 'Card Title', ar: 'عنوان البطاقة' }, description: { en: 'Description', ar: 'الوصف' } });
    }
    renderRepeaterItems();
  });

  function collectRepeaterItems() {
    const type = getSelectedType();
    const items = [];
    const rows = repeaterList.querySelectorAll('.p-3, .p-4');

    rows.forEach(row => {
      if (type === 'stats') {
        const num = row.querySelector('.rep-num')?.value.trim() || '';
        const icon = row.querySelector('.rep-icon')?.value.trim() || 'award';
        const headEn = row.querySelector('.rep-head-en')?.value.trim() || '';
        const headAr = row.querySelector('.rep-head-ar')?.value.trim() || '';
        if (num || headEn) {
          items.push({
            number: num,
            icon: icon,
            label: { en: headEn, ar: headAr || headEn }
          });
        }
      } else if (type === 'services') {
        const nameEn = row.querySelector('.rep-svc-en')?.value.trim() || '';
        const nameAr = row.querySelector('.rep-svc-ar')?.value.trim() || '';
        if (nameEn || nameAr) {
          items.push({ name: { en: nameEn, ar: nameAr || nameEn } });
        }
      } else if (type === 'brands') {
        const bName = row.querySelector('.rep-brand-name')?.value.trim() || '';
        if (bName) items.push(bName);
      } else if (type === 'faq') {
        const qEn = row.querySelector('.rep-q-en')?.value.trim() || '';
        const qAr = row.querySelector('.rep-q-ar')?.value.trim() || '';
        const aEn = row.querySelector('.rep-a-en')?.value.trim() || '';
        const aAr = row.querySelector('.rep-a-ar')?.value.trim() || '';
        if (qEn || qAr) {
          items.push({
            question: { en: qEn, ar: qAr || qEn },
            answer: { en: aEn, ar: aAr || aEn }
          });
        }
      } else if (type === 'testimonials') {
        const authEn = row.querySelector('.rep-rev-auth-en')?.value.trim() || '';
        const authAr = row.querySelector('.rep-rev-auth-ar')?.value.trim() || '';
        const qEn = row.querySelector('.rep-rev-quote-en')?.value.trim() || '';
        const qAr = row.querySelector('.rep-rev-quote-ar')?.value.trim() || '';
        if (qEn || authEn) {
          items.push({
            rating: 5,
            author: { en: authEn || 'Verified customer', ar: authAr || 'عميل موثوق' },
            quote: { en: qEn, ar: qAr || qEn }
          });
        }
      } else if (type === 'how_it_works') {
        const icon = row.querySelector('.rep-icon')?.value.trim() || 'phone';
        const titleEn = row.querySelector('.rep-title-en')?.value.trim() || '';
        const titleAr = row.querySelector('.rep-title-ar')?.value.trim() || '';
        const descEn = row.querySelector('.rep-desc-en')?.value.trim() || '';
        const descAr = row.querySelector('.rep-desc-ar')?.value.trim() || '';
        if (titleEn || titleAr) {
          items.push({
            step_number: items.length + 1,
            icon: icon,
            title: { en: titleEn, ar: titleAr || titleEn },
            description: { en: descEn, ar: descAr || descEn }
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
            description: { en: descEn, ar: descAr || descEn }
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
    modalTitle.textContent = 'Add Section';
    sectionForm.reset();
    if (formPageSlug) formPageSlug.value = currentPageSlug;
    setSelectedType('features');
    setLocaleTab('en');
    setEditorContent('form-content-en', '');
    setEditorContent('form-content-ar', '');
    if (formMetaTitleEn) formMetaTitleEn.value = '';
    if (formMetaTitleAr) formMetaTitleAr.value = '';
    if (formMetaDescEn) formMetaDescEn.value = '';
    if (formMetaDescAr) formMetaDescAr.value = '';
    updateImagePreview('');
    repeaterItems = [];
    extraSectionData = {};
    formSortOrder.value = allSections.length + 1;
    formIsActive.checked = true;
    renderRepeaterItems();
    openModal();
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
    extraSectionData = JSON.parse(JSON.stringify(sData));

    if (sData.metrics && Array.isArray(sData.metrics)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.metrics));
    } else if (sData.cards && Array.isArray(sData.cards)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.cards));
    } else if (sData.services && Array.isArray(sData.services)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.services));
    } else if (sData.steps && Array.isArray(sData.steps)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.steps));
    } else if (sData.brands && Array.isArray(sData.brands)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.brands));
    } else if (sData.reviews && Array.isArray(sData.reviews)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.reviews));
    } else if (sData.faqs && Array.isArray(sData.faqs)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.faqs));
    } else if (sData.badges && Array.isArray(sData.badges)) {
      repeaterItems = JSON.parse(JSON.stringify(sData.badges));
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
    }, 50);
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
    const sectionData = Object.assign({}, extraSectionData);

    if (sectionType === 'stats') {
      sectionData.metrics = repData;
    } else if (sectionType === 'features') {
      sectionData.cards = repData;
    } else if (sectionType === 'services') {
      sectionData.services = repData;
    } else if (sectionType === 'how_it_works') {
      sectionData.steps = repData;
    } else if (sectionType === 'brands') {
      sectionData.brands = repData;
    } else if (sectionType === 'testimonials') {
      sectionData.reviews = repData;
    } else if (sectionType === 'faq') {
      sectionData.faqs = repData;
    } else if (sectionType === 'hero') {
      if (repData.length > 0) sectionData.badges = repData;
    } else {
      if (repData.length > 0) sectionData.items = repData;
    }

    const targetSlug = formPageSlug?.value?.trim() || currentPageSlug || 'home';

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

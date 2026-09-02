/**
 * VisionAdmin Universal Custom Dropdown Engine
 * Transforms all <select> elements in VisionAdmin to match the signature
 * pill design: green border, green status dot, bold typography,
 * animated green chevron, and floating card menu with pale green active selection & checkmark.
 */

(function () {
  'use strict';

  function parseOptionText(text) {
    const raw = (text || '').trim();
    const match = raw.match(/^(.*?)\s*(\([\s\S]*?\))$/);
    if (match) {
      return {
        main: match[1].trim(),
        sub: match[2].trim()
      };
    }
    return {
      main: raw,
      sub: ''
    };
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function enhanceSelect(select) {
    if (!select || select.dataset.vaDropdownInit === 'true') return;
    if (select.classList.contains('no-custom-dropdown') || select.classList.contains('hidden') || select.dataset.vaSkip === 'true') return;
    if (select.id === 'select-target-page') return; // Handled specifically by sections.js

    // Mark as initialized
    select.dataset.vaDropdownInit = 'true';

    // Hide native select visually but keep in DOM for forms/Alpine/DataTables
    select.style.setProperty('display', 'none', 'important');

    // Create custom wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'va-custom-dropdown-wrap relative inline-block text-left';
    
    // Copy width styling from original select
    if (select.classList.contains('w-full')) {
      wrapper.classList.add('w-full');
    }
    if (select.style.width) {
      wrapper.style.width = select.style.width;
    }

    // Trigger button
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'va-custom-dropdown-trigger w-full flex items-center justify-between gap-3 pl-4 pr-3.5 py-2.5 rounded-full bg-white hover:bg-[#F8FAF7] border border-[#58B31B] hover:border-[#35760F] text-xs font-bold text-[#0E1108] shadow-2xs transition-all cursor-pointer select-none';
    trigger.setAttribute('aria-expanded', 'false');
    trigger.setAttribute('aria-haspopup', 'true');

    if (select.disabled) {
      trigger.disabled = true;
      trigger.classList.add('opacity-50', 'cursor-not-allowed', 'bg-slate-50');
    }

    trigger.innerHTML = `
      <div class="flex items-center gap-2 min-w-0">
        <span class="va-custom-dropdown-dot w-2 h-2 rounded-full bg-[#58B31B] shrink-0"></span>
        <span class="va-custom-dropdown-current-label truncate font-extrabold text-[#0E1108]">Select...</span>
      </div>
      <svg class="va-custom-dropdown-chevron w-4 h-4 text-[#35760F] transition-transform duration-200 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    `;

    // Dropdown floating menu card
    const menu = document.createElement('div');
    menu.className = 'va-custom-dropdown-menu hidden absolute left-0 right-0 top-full mt-2 min-w-[200px] bg-white rounded-2xl shadow-[0_12px_36px_-8px_rgba(0,0,0,0.15)] border border-slate-100 p-1.5 z-50 transform origin-top transition-all duration-200 max-h-72 overflow-y-auto';

    const optionsList = document.createElement('div');
    optionsList.className = 'va-custom-dropdown-options-list space-y-0.5';
    menu.appendChild(optionsList);

    wrapper.appendChild(trigger);
    wrapper.appendChild(menu);

    // Insert wrapper next to select
    select.parentNode.insertBefore(wrapper, select.nextSibling);

    const labelSpan = trigger.querySelector('.va-custom-dropdown-current-label');
    const chevron = trigger.querySelector('.va-custom-dropdown-chevron');

    function renderOptions() {
      const options = Array.from(select.options);
      const currentVal = select.value;

      // Update trigger label
      const selectedOpt = select.selectedOptions[0] || options[0];
      if (selectedOpt) {
        const parsed = parseOptionText(selectedOpt.textContent);
        if (parsed.sub) {
          labelSpan.innerHTML = `${escapeHtml(parsed.main)} <span class="text-[11px] text-slate-400 font-semibold">(${escapeHtml(parsed.sub.replace(/^\(|\)$/g, ''))})</span>`;
        } else {
          labelSpan.textContent = parsed.main || 'Select...';
        }
      } else {
        labelSpan.textContent = 'Select...';
      }

      // Render menu options
      optionsList.innerHTML = options.map((opt, idx) => {
        const isSelected = opt.value === currentVal || (!currentVal && idx === 0 && !select.multiple && opt.value === '');
        const parsed = parseOptionText(opt.textContent);
        
        return `
          <button 
            type="button" 
            class="va-option-btn w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs transition-all text-left cursor-pointer ${
              isSelected 
                ? 'bg-[#EAF7E2] text-[#0E1108] font-extrabold' 
                : 'text-slate-700 hover:bg-[#F8FAF7] hover:text-[#0E1108] font-bold'
            }"
            data-value="${escapeHtml(opt.value)}"
            data-index="${idx}"
          >
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-1.5 h-1.5 rounded-full ${isSelected ? 'bg-[#58B31B]' : 'bg-slate-300'} shrink-0"></span>
              <span class="truncate">
                ${escapeHtml(parsed.main)}
                ${parsed.sub ? `<span class="text-[11px] text-slate-400 font-semibold ml-1">${escapeHtml(parsed.sub)}</span>` : ''}
              </span>
            </div>
            ${isSelected ? '<svg class="w-4 h-4 text-[#35760F] shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>' : ''}
          </button>
        `;
      }).join('');

      // Wire option clicks
      optionsList.querySelectorAll('.va-option-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const val = btn.getAttribute('data-value');
          if (select.value !== val) {
            select.value = val;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            select.dispatchEvent(new Event('input', { bubbles: true }));
          }
          closeDropdown();
        });
      });
    }

    function openDropdown() {
      // Close all other dropdowns first
      document.querySelectorAll('.va-custom-dropdown-menu:not(.hidden)').forEach(m => {
        if (m !== menu) {
          m.classList.add('hidden');
          const t = m.parentElement?.querySelector('.va-custom-dropdown-trigger');
          if (t) {
            t.setAttribute('aria-expanded', 'false');
            t.querySelector('.va-custom-dropdown-chevron')?.classList.remove('rotate-180');
          }
        }
      });

      renderOptions();
      menu.classList.remove('hidden');
      trigger.setAttribute('aria-expanded', 'true');
      chevron?.classList.add('rotate-180');
    }

    function closeDropdown() {
      menu.classList.add('hidden');
      trigger.setAttribute('aria-expanded', 'false');
      chevron?.classList.remove('rotate-180');
    }

    function toggleDropdown(e) {
      e.stopPropagation();
      if (select.disabled) return;
      if (menu.classList.contains('hidden')) {
        openDropdown();
      } else {
        closeDropdown();
      }
    }

    trigger.addEventListener('click', toggleDropdown);

    // Sync when native select value changes from outside (e.g. Alpine.js / JS assignment)
    select.addEventListener('change', () => {
      renderOptions();
    });

    // Observe changes to options in select
    const observer = new MutationObserver(() => {
      if (select.disabled) {
        trigger.disabled = true;
        trigger.classList.add('opacity-50', 'cursor-not-allowed', 'bg-slate-50');
      } else {
        trigger.disabled = false;
        trigger.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-slate-50');
      }
      renderOptions();
    });

    observer.observe(select, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['disabled', 'value', 'class']
    });

    // Initial render
    renderOptions();
  }

  // Global click-outside listener
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.va-custom-dropdown-wrap')) {
      document.querySelectorAll('.va-custom-dropdown-menu:not(.hidden)').forEach(m => {
        m.classList.add('hidden');
        const t = m.parentElement?.querySelector('.va-custom-dropdown-trigger');
        if (t) {
          t.setAttribute('aria-expanded', 'false');
          t.querySelector('.va-custom-dropdown-chevron')?.classList.remove('rotate-180');
        }
      });
    }
  });

  // Global Escape key listener
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.va-custom-dropdown-menu:not(.hidden)').forEach(m => {
        m.classList.add('hidden');
        const t = m.parentElement?.querySelector('.va-custom-dropdown-trigger');
        if (t) {
          t.setAttribute('aria-expanded', 'false');
          t.querySelector('.va-custom-dropdown-chevron')?.classList.remove('rotate-180');
        }
      });
    }
  });

  // Scan & enhance all selects in a container
  function initVisionDropdowns(root = document) {
    if (!root) return;
    const selects = root.querySelectorAll('select:not([data-va-dropdown-init="true"]):not(.hidden):not(.no-custom-dropdown)');
    selects.forEach(enhanceSelect);
  }

  // Export to window
  window.initVisionDropdowns = initVisionDropdowns;
  window.enhanceVisionSelect = enhanceSelect;

  // Auto-init on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initVisionDropdowns());
  } else {
    initVisionDropdowns();
  }

  window.addEventListener('load', () => initVisionDropdowns());

  // Observe dynamically added selects (e.g. inside modals, Alpine components)
  const bodyObserver = new MutationObserver((mutations) => {
    let shouldScan = false;
    for (const m of mutations) {
      if (m.addedNodes.length > 0) {
        for (const n of m.addedNodes) {
          if (n.nodeType === 1) {
            if (n.tagName === 'SELECT' || n.querySelector?.('select')) {
              shouldScan = true;
              break;
            }
          }
        }
      }
      if (shouldScan) break;
    }
    if (shouldScan) {
      initVisionDropdowns();
    }
  });

  if (document.body) {
    bodyObserver.observe(document.body, { childList: true, subtree: true });
  } else {
    document.addEventListener('DOMContentLoaded', () => {
      bodyObserver.observe(document.body, { childList: true, subtree: true });
    });
  }

})();

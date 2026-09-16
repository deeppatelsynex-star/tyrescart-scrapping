(function(){
  var WA = "971505069575";
  var yrEl = document.getElementById('yr');
  if(yrEl) yrEl.textContent = new Date().getFullYear();

  var form = document.getElementById('quoteForm');
  if(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var sizeEl = document.getElementById('tyreSize');
      var size = sizeEl ? sizeEl.value.trim() : '';
      if(!size){ if(sizeEl){ sizeEl.focus(); sizeEl.style.borderColor = '#C0392B'; } return; }

      var makeEl = document.getElementById('carMake');
      var make = makeEl ? makeEl.value.trim() : '';
      var emirateEl = document.getElementById('emirate');
      var emirate = emirateEl ? emirateEl.value : '';
      var fittingEl = document.getElementById('fitting');
      var fitting = fittingEl ? fittingEl.value : '';

      var lines = ["Hi Online Tyre Shop, I'd like a tyre quote.", "Tyre size: " + size];
      if(make) lines.push("Car: " + make);
      if(emirate) lines.push("Emirate: " + emirate);
      if(fitting) lines.push("Fitting: " + fitting);

      // Save enquiry record in existing hdweb_enquiry table
      try {
        fetch('/api/v1/enquiry', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            tyre_size: size,
            vehicle: make,
            city: emirate,
            spec: fitting,
            enquiry_for: 'Tyre Quote (WhatsApp Home Banner)',
            form_type: 'home_banner_whatsapp',
            message: lines.join("\n")
          })
        }).catch(function(err){
          console.warn('Enquiry store error:', err);
        });
      } catch (err) {
        console.warn(err);
      }

      // Open WhatsApp with pre-filled message
      window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
    });

    var sizeInput = document.getElementById('tyreSize');
    if(sizeInput){
      sizeInput.addEventListener('input', function(){ this.style.borderColor = ''; });
    }
  }

  /* ---------- Ownership notice modal ---------- */
  window.openNotice = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    var body = document.body;
    if (window.Alpine && body._x_dataStack && body._x_dataStack.length) {
      body._x_dataStack[0].noticeModalOpen = true;
    }
    var m = document.getElementById('noticeModal');
    if (m) {
      m.style.setProperty('display', 'flex', 'important');
      m.classList.add('open');
      m.removeAttribute('x-cloak');
    }
    document.documentElement.classList.add('modal-open');
    document.body.classList.add('modal-open');
    var sheetBody = m ? m.querySelector('.sheet-body') : null;
    if (sheetBody) sheetBody.scrollTop = 0;
    var closeBtn = document.getElementById('noticeClose');
    if (closeBtn && window.innerWidth > 820) closeBtn.focus();
  };

  window.closeNotice = function(e) {
    if (e && e.preventDefault) e.preventDefault();
    var body = document.body;
    if (window.Alpine && body._x_dataStack && body._x_dataStack.length) {
      body._x_dataStack[0].noticeModalOpen = false;
    }
    var m = document.getElementById('noticeModal');
    if (m) {
      m.style.setProperty('display', 'none', 'important');
      m.classList.remove('open');
    }
    document.documentElement.classList.remove('modal-open');
    document.body.classList.remove('modal-open');
  };

  // Bind click handlers globally (catches dynamically rendered or static triggers)
  document.addEventListener('click', function(e) {
    var trigger = e.target && e.target.closest && e.target.closest('a[href="#notice"], [data-notice]');
    if (trigger) {
      e.preventDefault();
      window.openNotice(e);
      return;
    }
    var closeBtn = e.target && e.target.closest && e.target.closest('#noticeClose, #noticeClose2, [data-notice-close]');
    if (closeBtn) {
      e.preventDefault();
      window.closeNotice(e);
      return;
    }
    var modal = document.getElementById('noticeModal');
    if (modal && (e.target === modal || (e.target && e.target.classList && e.target.classList.contains('notice-modal-dialog')))) {
      window.closeNotice(e);
    }
  }, true); // Use capture phase so stopPropagation inside dialog won't block it!

  window.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      var modal = document.getElementById('noticeModal');
      if (modal && (modal.style.display === 'flex' || modal.classList.contains('open') || (window.Alpine && document.body._x_dataStack && document.body._x_dataStack[0] && document.body._x_dataStack[0].noticeModalOpen))) {
        closeNotice();
      }
    }
  });

  if (window.location.hash === '#notice') {
    setTimeout(openNotice, 150);
  }

  /* ---------- Mobile Navigation Drawer ---------- */
  function initMobileNav() {
    var menuBtn = document.getElementById('mobileMenuBtn');
    var drawer = document.getElementById('mobileNavDrawer');
    var backdrop = document.getElementById('mobileNavBackdrop');
    var closeBtn = document.getElementById('mobileNavClose');

    function openMobileNav() {
      var d = document.getElementById('mobileNavDrawer');
      var b = document.getElementById('mobileNavBackdrop');
      var m = document.getElementById('mobileMenuBtn');
      if (d) d.classList.add('open');
      if (b) b.classList.add('open');
      if (m) m.setAttribute('aria-expanded', 'true');
      document.body.style.overflow = 'hidden';
    }

    function closeMobileNav() {
      var d = document.getElementById('mobileNavDrawer');
      var b = document.getElementById('mobileNavBackdrop');
      var m = document.getElementById('mobileMenuBtn');
      if (d) d.classList.remove('open');
      if (b) b.classList.remove('open');
      if (m) m.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }

    if (menuBtn) menuBtn.addEventListener('click', openMobileNav);
    if (closeBtn) closeBtn.addEventListener('click', closeMobileNav);
    if (backdrop) backdrop.addEventListener('click', closeMobileNav);

    if (drawer) {
      var links = drawer.querySelectorAll('a');
      for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', function() {
          closeMobileNav();
        });
      }
    }

    window.addEventListener('keydown', function(e) {
      var d = document.getElementById('mobileNavDrawer');
      if (e.key === 'Escape' && d && d.classList.contains('open')) {
        closeMobileNav();
      }
    });
  }

  /* ---------- Global .btn-wa & WhatsApp Click Capture ---------- */
  document.addEventListener('click', function(e) {
    var target = e.target && e.target.closest ? e.target.closest('.btn-wa, .float-wa, a[href*="wa.me"], button[data-wa]') : null;
    if (!target) return;

    // If it's the submit button inside quoteForm, let the form submit event handle it with full input values
    if (target.closest && target.closest('#quoteForm') && (target.type === 'submit' || target.tagName === 'BUTTON')) {
      return;
    }

    var href = target.getAttribute('href') || '';
    var ctaText = (target.textContent || '').trim();
    var pageUrl = window.location.pathname || '/';

    var messageText = 'Direct WhatsApp CTA Click';
    if (href && href.indexOf('text=') !== -1) {
      try {
        var match = href.match(/text=([^&]+)/);
        if (match && match[1]) {
          messageText = decodeURIComponent(match[1]);
        }
      } catch (err) {}
    } else if (ctaText) {
      messageText = 'Clicked: ' + ctaText;
    }

    var formType = 'whatsapp_button_click';
    if (target.classList && target.classList.contains('float-wa')) {
      formType = 'floating_whatsapp_widget';
    } else if (target.closest && target.closest('.nav-cta')) {
      formType = 'header_nav_whatsapp';
    } else if (target.closest && (target.closest('.mobile-sticky-cta') || target.closest('.mobile-nav-cta'))) {
      formType = 'mobile_whatsapp_bar';
    }

    // Extract structured tyre size, vehicle, and brand from element or ancestors
    var tyreSize = target.getAttribute('data-tyre-size') || (target.closest && target.closest('[data-tyre-size]') ? target.closest('[data-tyre-size]').getAttribute('data-tyre-size') : '') || '';
    var vehicle = target.getAttribute('data-vehicle') || (target.closest && target.closest('[data-vehicle]') ? target.closest('[data-vehicle]').getAttribute('data-vehicle') : '') || '';
    var brand = target.getAttribute('data-brand') || (target.closest && target.closest('[data-brand]') ? target.closest('[data-brand]').getAttribute('data-brand') : '') || '';
    var customFormType = target.getAttribute('data-form-type') || (target.closest && target.closest('[data-form-type]') ? target.closest('[data-form-type]').getAttribute('data-form-type') : '') || '';
    var customEnquiryFor = target.getAttribute('data-enquiry-for') || (target.closest && target.closest('[data-enquiry-for]') ? target.closest('[data-enquiry-for]').getAttribute('data-enquiry-for') : '') || '';

    // Intelligent regex parsing fallback from messageText
    if (!tyreSize && messageText) {
      var sm = messageText.match(/\b([1-3]\d{2}\s*\/\s*\d{2}\s*(?:R|ZR|r|zr)?\s*\d{2})\b/);
      if (sm && sm[1]) tyreSize = sm[1].trim();
    }
    if (!vehicle && messageText) {
      var vm = messageText.match(/(?:tyre\s+options\s+for|options\s+for|vehicle:?)\s*([^.\n]+)/i);
      if (vm && vm[1]) vehicle = vm[1].trim();
    }
    if (!brand && messageText) {
      var bm = messageText.match(/(?:tyres\s+from|brand:?)\s*([^.\n]+)/i);
      if (bm && bm[1]) brand = bm[1].trim();
    }

    if (customFormType) {
      formType = customFormType;
    } else if (tyreSize) {
      formType = 'shop_by_size';
    } else if (vehicle) {
      formType = 'shop_by_vehicle';
    } else if (brand) {
      formType = 'shop_by_brand';
    }

    var enquiryFor = customEnquiryFor || (
      tyreSize ? ('Tyre Size Lead (' + tyreSize + ')') :
      vehicle ? ('Vehicle Tyre Lead (' + vehicle + ')') :
      brand ? ('Brand Tyre Lead (' + brand + ')') :
      ('WhatsApp Lead (' + (ctaText || 'CTA Button') + ')')
    );

    var cityAttr = target.getAttribute('data-city') || (target.closest && target.closest('[data-city]') ? target.closest('[data-city]').getAttribute('data-city') : '') || '';
    var locationAttr = target.getAttribute('data-location') || (target.closest && target.closest('[data-location]') ? target.closest('[data-location]').getAttribute('data-location') : '') || '';
    var resolvedCity = 'UAE';
    if (locationAttr && cityAttr) {
      resolvedCity = locationAttr + ', ' + cityAttr;
    } else if (locationAttr || cityAttr) {
      resolvedCity = locationAttr || cityAttr;
    }

    try {
      fetch('/api/v1/enquiry', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          enquiry_for: enquiryFor,
          form_type: formType,
          message: messageText + '\nSource Page: ' + pageUrl,
          tyre_size: tyreSize || '',
          vehicle: vehicle || '',
          spec: brand || '',
          city: resolvedCity
        })
      }).catch(function(err) {
        console.warn('Enquiry tracking error:', err);
      });
    } catch (err) {
      console.warn(err);
    }
  });

  /* ---------- Dynamic Nav Active State (Mobile Drawer) & ScrollSpy ---------- */
  function initNavActiveState() {
    var mobileLinks = document.querySelectorAll('.mobile-nav-links a');
    var allLinks = document.querySelectorAll('.nav-links a, .mobile-nav-links a');
    if (!allLinks.length) return;

    // Ensure desktop links never retain an active class
    var desktopLinks = document.querySelectorAll('.nav-links a');
    desktopLinks.forEach(function(l) { l.classList.remove('active'); });

    function setActive(targetKey) {
      if (!targetKey) return;
      mobileLinks.forEach(function(link) {
        var key = link.getAttribute('data-nav-target') || '';
        if (!key) {
          var href = link.getAttribute('href') || '';
          key = href.indexOf('#') !== -1 ? ('#' + href.split('#')[1]) : href;
        }
        if (key === targetKey) {
          link.classList.add('active');
        } else {
          link.classList.remove('active');
        }
      });
    }

    // 1. Click Listener
    allLinks.forEach(function(link) {
      link.addEventListener('click', function(e) {
        var key = link.getAttribute('data-nav-target') || '';
        if (!key) {
          var href = link.getAttribute('href') || '';
          key = href.indexOf('#') !== -1 ? ('#' + href.split('#')[1]) : href;
        }
        setActive(key);

        // If clicking hash link on current home page, handle smooth scroll
        if (key && key.startsWith('#')) {
          var targetEl = document.getElementById(key.substring(1));
          if (targetEl) {
            var path = window.location.pathname;
            var isHome = path === '/' || path === '/home';
            if (isHome) {
              e.preventDefault();
              history.pushState(null, null, key);
              targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
          }
        }
      });
    });

    // 2. Hash Change & Initial Check
    function checkHashOrTop() {
      if (window.location.hash) {
        setActive(window.location.hash);
      } else {
        var path = window.location.pathname;
        var isHome = path === '/' || path === '/home';
        if (isHome && window.scrollY < 200) {
          setActive('/');
        }
      }
    }

    window.addEventListener('hashchange', checkHashOrTop);
    checkHashOrTop();

    // 3. ScrollSpy on Home Page
    var sectionKeys = ['#faq', '#brands', '#how', '#services', '#prices', '#why'];
    var sectionMap = [];
    sectionKeys.forEach(function(k) {
      var el = document.getElementById(k.substring(1));
      if (el) sectionMap.push({ key: k, el: el });
    });

    if (sectionMap.length > 0) {
      var ticking = false;
      window.addEventListener('scroll', function() {
        if (!ticking) {
          window.requestAnimationFrame(function() {
            var scrollY = window.scrollY;
            if (scrollY < 200) {
              setActive('/');
            } else {
              var probe = scrollY + 180;
              for (var i = 0; i < sectionMap.length; i++) {
                if (probe >= sectionMap[i].el.offsetTop) {
                  setActive(sectionMap[i].key);
                  break;
                }
              }
            }
            ticking = false;
          });
          ticking = true;
        }
      }, { passive: true });
    }
  }

  /* ---------- HTML Escape & Localization Utilities ---------- */
  function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function getLocalizedText(val, locale) {
    if (!val) return '';
    if (typeof val === 'string') {
      var trimmed = val.trim();
      if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
        try {
          var parsed = JSON.parse(trimmed);
          return parsed[locale] || parsed.en || parsed.ar || Object.values(parsed)[0] || '';
        } catch (e) {}
      }
      return val;
    }
    if (typeof val === 'object') {
      return val[locale] || val.en || val.ar || Object.values(val)[0] || '';
    }
    return String(val);
  }

  /* ---------- Dynamic FAQ Section Renderer (via JS) ---------- */
  function renderFaqSections() {
    var locale = document.documentElement.getAttribute('lang') || 'en';

    // Home Page / Section FAQ (Rendered dynamically via JS)
    var homeFaqContainer = document.getElementById('home-faq-container');
    var homeFaqScript = document.getElementById('home-faq-json');

    if (homeFaqContainer && homeFaqScript) {
      try {
        var secData = JSON.parse(homeFaqScript.textContent || '{}');
        var title = getLocalizedText(secData.section_title, locale);
        var subtitle = getLocalizedText(secData.section_subtitle, locale);
        var rawFaqs = (secData.section_data && secData.section_data.faqs) ? secData.section_data.faqs : [];
        if (!Array.isArray(rawFaqs)) rawFaqs = [];

        var itemsHtml = '';
        rawFaqs.forEach(function(f, idx) {
          if (!f) return;
          var q = getLocalizedText(f.question, locale);
          var a = getLocalizedText(f.answer, locale);
          if (!q || !q.trim()) return;

          var isFirst = (idx === 0);
          var answerContent = a.trim().startsWith('<p') ? a : ('<p>' + a + '</p>');

          itemsHtml += `
            <div class="faq-item ${isFirst ? 'active' : ''}" data-faq-item>
              <button type="button" class="faq-summary" aria-expanded="${isFirst ? 'true' : 'false'}">
                <span class="faq-question-text">${escapeHtml(q)}</span>
                <span class="faq-chevron-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </span>
              </button>
              <div class="faq-answer">
                <div class="faq-answer-inner">
                  <div class="body">${answerContent}</div>
                </div>
              </div>
            </div>
          `;
        });

        var headerHtml = '';
        if (subtitle || title) {
          headerHtml = `
            <div class="center">
              ${subtitle ? `<span class="eyebrow">${escapeHtml(subtitle)}</span>` : ''}
              ${title ? `<h2>${escapeHtml(title)}</h2>` : ''}
            </div>
          `;
        }

        homeFaqContainer.innerHTML = `
          ${headerHtml}
          <div style="margin-top:36px" class="faq-list">
            ${itemsHtml}
          </div>
        `;
      } catch (err) {
        console.error('Failed to render FAQ section via JS:', err);
      }
    }
  }

  /* ---------- Smooth Exclusive FAQ Accordion Engine ---------- */
  function initFaqAccordion() {
    // 1. Button-based FAQ items (Smooth CSS Grid Accordion)
    var faqButtons = document.querySelectorAll('.faq-item .faq-summary, .faq-item .faq-trigger, .faq-item .tv-faq-trigger, .faq-item button.faq-question-btn, .faq-item button[aria-expanded], [data-faq-item] button');
    faqButtons.forEach(function(btn) {
      if (btn._faqBound || btn.dataset.bound === 'true') return;
      btn._faqBound = true;
      btn.dataset.bound = 'true';

      btn.addEventListener('click', function(e) {
        e.preventDefault();
        var item = btn.closest('.faq-item, .tv-faq-item, [data-faq-item]');
        if (!item) return;
        var isAlreadyActive = item.classList.contains('active');

        // Smoothly close all other items in this list container
        var container = item.closest('.faq-list, .faq, .dynamic-faq-block, .tv-faq-container, [id^="faq"]') || item.parentElement;
        if (container) {
          var allItems = container.querySelectorAll('.faq-item, .tv-faq-item, [data-faq-item]');
          allItems.forEach(function(otherItem) {
            if (otherItem !== item && otherItem.classList.contains('active')) {
              otherItem.classList.remove('active');
              var otherBtn = otherItem.querySelector('.faq-summary, .faq-trigger, .tv-faq-trigger, button[aria-expanded]');
              if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
              var otherIcon = otherItem.querySelector('.faq-icon');
              if (otherIcon) otherIcon.innerHTML = '+';
              var otherAnswer = otherItem.querySelector('.faq-answer');
              if (otherAnswer && otherAnswer.style.maxHeight) otherAnswer.style.maxHeight = '0px';
            }
          });
        }

        // Toggle clicked item
        if (isAlreadyActive) {
          item.classList.remove('active');
          btn.setAttribute('aria-expanded', 'false');
          var icon = item.querySelector('.faq-icon');
          if (icon) icon.innerHTML = '+';
          var answer = item.querySelector('.faq-answer');
          if (answer && answer.style.maxHeight) answer.style.maxHeight = '0px';
        } else {
          item.classList.add('active');
          btn.setAttribute('aria-expanded', 'true');
          var icon = item.querySelector('.faq-icon');
          if (icon) icon.innerHTML = '&minus;';
          var answer = item.querySelector('.faq-answer');
          if (answer && answer.style.maxHeight) {
            var inner = answer.querySelector('.faq-answer-inner');
            answer.style.maxHeight = ((inner ? inner.scrollHeight : 200) + 40) + 'px';
          }
        }
      });
    });

    // 2. Native <details> fallback support
    var allDetails = document.querySelectorAll('.faq details, .faq-list details, details.faq-item');
    allDetails.forEach(function(detail) {
      if (detail._faqBound || detail.dataset.bound === 'true') return;
      detail._faqBound = true;
      detail.dataset.bound = 'true';

      detail.addEventListener('toggle', function() {
        if (this.open) {
          detail.classList.add('active');
          var container = detail.closest('.faq-list, .faq') || detail.parentElement;
          if (container) {
            container.querySelectorAll('details').forEach(function(other) {
              if (other !== detail && other.open) {
                other.open = false;
                other.removeAttribute('open');
                other.classList.remove('active');
              }
            });
          }
        } else {
          detail.classList.remove('active');
        }
      });
    });
  }

  function initAll() {
    initMobileNav();
    initNavActiveState();
    renderFaqSections();
    initFaqAccordion();
    sliderInit();
  }

  // Exposed so content injected after DOMContentLoaded (e.g. dynamic
  // page/section HTML fetched and inserted by client-page-sections.js) can
  // re-scan for FAQ accordions without needing a second copy of this logic.
  window.initFaqAccordion = initFaqAccordion;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();


sliderInit = function() {

    const slides = document.querySelector(".slides");
    const slideItems = document.querySelectorAll(".slide");
    const dots = document.querySelectorAll(".dot");

    // Slider does not exist on this page
    if (!slides || slideItems.length === 0) {
        return;
    }

    let currentSlide = 0;
    const totalSlides = slideItems.length;

    function showSlide(index) {

        if (index >= totalSlides) {
            currentSlide = 0;
        } 
        else if (index < 0) {
            currentSlide = totalSlides - 1;
        } 
        else {
            currentSlide = index;
        }

        slides.style.transform =
            `translateX(-${currentSlide * 100}%)`;

        dots.forEach((dot, index) => {
            dot.classList.toggle(
                "active",
                index === currentSlide
            );
        });
    }

    window.nextSlide = function () {
        showSlide(currentSlide + 1);
    };

    window.prevSlide = function () {
        showSlide(currentSlide - 1);
    };

    window.goToSlide = function (index) {
        showSlide(index);
    };

    // Auto slide
    setInterval(function () {
        nextSlide();
    }, 3000);

};

// ==========================================================================
// TYRESVISION CMS PAGES & DYNAMIC COMPONENTS (Page.html)
// ==========================================================================
window.initTvPageComponents = function() {
    // 1. Delegate .faq-item to the primary CSS Grid FAQ accordion engine
    if (typeof window.initFaqAccordion === 'function') {
        window.initFaqAccordion();
    }

    // 1b. DataTables Responsive Expand/Collapse Accordion for Mobile Tables
    function initResponsiveDataTables() {
        var tables = document.querySelectorAll('.price-table, .tv-4x4-table, .tv-ev-table, .tv-table');
        tables.forEach(function(table) {
            // Skip if already initialized or if child rows already present
            if (table.dataset.dtrInitialized === 'true' || table.querySelector('.dtr-child-row')) {
                return;
            }

            var thead = table.querySelector('thead');
            var tbody = table.querySelector('tbody');
            if (!thead || !tbody) return;

            var headerRow = thead.querySelector('tr');
            if (!headerRow) return;

            var ths = headerRow.querySelectorAll('th');
            var colCount = ths.length;
            if (colCount < 3) return; // Only tables with collapsible intermediate columns

            table.dataset.dtrInitialized = 'true';
            table.classList.add('dtr-table');

            // Mark intermediate headers as desktop-col (hidden on mobile)
            for (var c = 1; c < colCount - 1; c++) {
                ths[c].classList.add('desktop-col');
            }

            function getDetailIcon(title) {
                var t = (title || '').toLowerCase();
                if (t.indexOf('vehicle') !== -1 || t.indexOf('car') !== -1 || t.indexOf('model') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.5 2.8C2.1 10.7 2 11.1 2 11.5V16c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>';
                }
                if (t.indexOf('mid') !== -1 || t.indexOf('star') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>';
                }
                if (t.indexOf('premium') !== -1 || t.indexOf('crown') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m2 4 3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14"/></svg>';
                }
                if (t.indexOf('value') !== -1 || t.indexOf('price') !== -1 || t.indexOf('tier') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>';
                }
                if (t.indexOf('size') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>';
                }
                if (t.indexOf('brand') !== -1 || t.indexOf('choice') !== -1) {
                    return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>';
                }
                return '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><polyline points="20 6 9 17 4 12"/></svg>';
            }

            var rows = Array.from(tbody.children);
            rows.forEach(function(masterRow) {
                if (masterRow.tagName !== 'TR' || masterRow.classList.contains('dtr-child-row')) return;

                var cells = masterRow.children;
                if (cells.length < colCount) return;

                masterRow.classList.add('dtr-parent-row');

                // 1. Control button in cell 0
                var firstCell = cells[0];
                var ctrlBtn = firstCell.querySelector('.dtr-control-btn');
                if (!ctrlBtn) {
                    ctrlBtn = document.createElement('button');
                    ctrlBtn.type = 'button';
                    ctrlBtn.className = 'dtr-control-btn';
                    ctrlBtn.setAttribute('aria-expanded', 'false');
                    ctrlBtn.setAttribute('aria-label', 'Toggle details');
                    ctrlBtn.innerHTML = '<span class="dtr-icon">+</span>';

                    var cellWrap = document.createElement('div');
                    cellWrap.className = 'dtr-cell-content';
                    cellWrap.appendChild(ctrlBtn);

                    while (firstCell.firstChild) {
                        cellWrap.appendChild(firstCell.firstChild);
                    }
                    firstCell.appendChild(cellWrap);
                }

                // 2. Mark intermediate cells for desktop display only
                for (var c = 1; c < colCount - 1; c++) {
                    cells[c].classList.add('desktop-col');
                }

                // 3. Create child details row
                var childRow = document.createElement('tr');
                childRow.className = 'dtr-child-row';
                childRow.style.display = 'none';

                var childTd = document.createElement('td');
                childTd.className = 'dtr-child-td';
                childTd.setAttribute('colspan', 100);

                var childDetails = document.createElement('div');
                childDetails.className = 'dtr-child-details';

                for (var c = 1; c < colCount - 1; c++) {
                    var hText = ths[c].textContent.trim();
                    var cContent = cells[c].innerHTML.trim();
                    if (!cContent) continue;

                    var detailItem = document.createElement('div');
                    detailItem.className = 'dtr-detail-item';

                    var iconHtml = getDetailIcon(hText);
                    detailItem.innerHTML =
                        '<span class="dtr-detail-title">' + iconHtml + ' ' + hText + ':</span>' +
                        '<span class="dtr-detail-value">' + cContent + '</span>';

                    childDetails.appendChild(detailItem);
                }

                childTd.appendChild(childDetails);
                childRow.appendChild(childTd);
                masterRow.insertAdjacentElement('afterend', childRow);

                // 4. Mobile Toggle Listener
                masterRow.addEventListener('click', function(e) {
                    // Ignore clicks on links or interactive buttons inside the row
                    if (e.target.closest('a') || e.target.closest('button:not(.dtr-control-btn)') || e.target.closest('input')) {
                        return;
                    }
                    if (window.innerWidth > 768) {
                        return;
                    }

                    var isExpanded = masterRow.classList.contains('dtr-expanded');

                    // Exclusive accordion: close any other expanded row in this table
                    table.querySelectorAll('.dtr-parent-row.dtr-expanded').forEach(function(otherRow) {
                        if (otherRow !== masterRow) {
                            otherRow.classList.remove('dtr-expanded');
                            var oBtn = otherRow.querySelector('.dtr-control-btn');
                            if (oBtn) {
                                oBtn.classList.remove('is-expanded');
                                oBtn.setAttribute('aria-expanded', 'false');
                                var oIcon = oBtn.querySelector('.dtr-icon');
                                if (oIcon) oIcon.textContent = '+';
                            }
                            var oChild = otherRow.nextElementSibling;
                            if (oChild && oChild.classList.contains('dtr-child-row')) {
                                oChild.classList.remove('is-open');
                                oChild.style.display = 'none';
                            }
                        }
                    });

                    if (!isExpanded) {
                        masterRow.classList.add('dtr-expanded');
                        ctrlBtn.classList.add('is-expanded');
                        ctrlBtn.setAttribute('aria-expanded', 'true');
                        var iconSpan = ctrlBtn.querySelector('.dtr-icon');
                        if (iconSpan) iconSpan.textContent = '−';
                        childRow.classList.add('is-open');
                        childRow.style.display = 'table-row';
                    } else {
                        masterRow.classList.remove('dtr-expanded');
                        ctrlBtn.classList.remove('is-expanded');
                        ctrlBtn.setAttribute('aria-expanded', 'false');
                        var iconSpan = ctrlBtn.querySelector('.dtr-icon');
                        if (iconSpan) iconSpan.textContent = '+';
                        childRow.classList.remove('is-open');
                        childRow.style.display = 'none';
                    }
                });
            });
        });
    }

    initResponsiveDataTables();

    // 2. Standalone handler for legacy .tv-faq-item ONLY (never binds to .faq-item)
    var tvFaqItems = document.querySelectorAll('.tv-faq-item:not(.faq-item)');
    tvFaqItems.forEach(function(item) {
        var summaryBtn = item.querySelector('.tv-faq-trigger');
        if (!summaryBtn) return;
        if (summaryBtn._tvFaqBound || summaryBtn.dataset.bound === 'true') return;
        summaryBtn._tvFaqBound = true;
        summaryBtn.dataset.bound = 'true';

        summaryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            var isOpen = item.classList.contains('active');
            var container = item.closest('.tv-faq-container') || item.parentElement;

            // Exclusive accordion behavior within the container
            if (container) {
                container.querySelectorAll('.tv-faq-item:not(.faq-item)').forEach(function(sib) {
                    if (sib !== item) {
                        sib.classList.remove('active');
                        var sibBtn = sib.querySelector('.tv-faq-trigger');
                        if (sibBtn) sibBtn.setAttribute('aria-expanded', 'false');
                        var sibPanel = sib.querySelector('.tv-faq-panel');
                        if (sibPanel) sibPanel.style.maxHeight = '0px';
                    }
                });
            }

            if (!isOpen) {
                item.classList.add('active');
                summaryBtn.setAttribute('aria-expanded', 'true');
                var panel = item.querySelector('.tv-faq-panel');
                if (panel) panel.style.maxHeight = (panel.scrollHeight + 30) + 'px';
            } else {
                item.classList.remove('active');
                summaryBtn.setAttribute('aria-expanded', 'false');
                var panel = item.querySelector('.tv-faq-panel');
                if (panel) panel.style.maxHeight = '0px';
            }
        });
    });

    // 2. CMS Hero Quote Form Handler
    var quoteForms = document.querySelectorAll('form#quoteForm');
    quoteForms.forEach(function(qForm) {
        if (qForm.dataset.bound === 'true') return;
        qForm.dataset.bound = 'true';

        qForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var sizeInput = qForm.querySelector('input[name="tyreSize"]');
            var size = sizeInput ? sizeInput.value.trim() : '';
            if (!size) {
                if (sizeInput) {
                    sizeInput.focus();
                    sizeInput.style.borderColor = '#ef4444';
                }
                return;
            }

            var makeInput = qForm.querySelector('input[name="carMake"]');
            var make = makeInput ? makeInput.value.trim() : '';
            var emirateSelect = qForm.querySelector('select[name="emirate"]');
            var emirate = emirateSelect ? emirateSelect.value : '';

            var pageTitle = document.title ? document.title.split('|')[0].trim() : 'TyresVision UAE';
            var msgLines = [
                "Hi TyresVision, I would like a tyre quote.",
                "Tyre size: " + size
            ];
            if (make) msgLines.push("Car: " + make);
            if (emirate) msgLines.push("Emirate: " + emirate);
            msgLines.push("Source: " + pageTitle);

            // Record enquiry in database asynchronously
            try {
                fetch('/api/v1/enquiry', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({
                        tyre_size: size,
                        vehicle: make,
                        city: emirate,
                        enquiry_for: 'CMS Page Quote (' + pageTitle + ')',
                        form_type: 'cms_page_hero_quote',
                        message: msgLines.join("\n")
                    })
                }).catch(function() {});
            } catch (err) {}

            var waUrl = "https://wa.me/971505069575?text=" + encodeURIComponent(msgLines.join("\n"));
            window.open(waUrl, "_blank", "noopener");
        });
    });

    // 3. Open WhatsApp and external action links safely
    var extLinks = document.querySelectorAll('.tv-table-quote-btn, .tv-card-link, .tv-table-link, .chip-interactive, .get-quote-link');
    extLinks.forEach(function(link) {
        if (link.getAttribute('href') && (link.getAttribute('href').startsWith('http') || link.getAttribute('href').startsWith('https://wa.me'))) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener');
        }
    });

    // 4. Antigravity 3D Tilt on Terrain Cards
    var terrainCards = document.querySelectorAll('.tv-terrain-card');
    terrainCards.forEach(function(card) {
        card.addEventListener('mousemove', function(e) {
            var rect = card.getBoundingClientRect();
            var x = e.clientX - rect.left - rect.width / 2;
            var y = e.clientY - rect.top - rect.height / 2;
            var rotX = (-y / (rect.height / 2)) * 6;
            var rotY = (x / (rect.width / 2)) * 6;
            card.style.transform = 'perspective(1000px) rotateX(' + rotX.toFixed(2) + 'deg) rotateY(' + rotY.toFixed(2) + 'deg) translateY(-6px)';
        });
        card.addEventListener('mouseleave', function() {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });

    // 5. GSAP Motion & ScrollTrigger Animations
    if (typeof gsap !== 'undefined') {
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);

            if (document.querySelector('.tv-terrain-grid')) {
                gsap.from('.tv-terrain-card', {
                    scrollTrigger: {
                        trigger: '.tv-terrain-grid',
                        start: 'top 95%',
                        once: true
                    },
                    y: 24,
                    duration: 0.6,
                    stagger: 0.1,
                    ease: 'power2.out',
                    clearProps: 'opacity,transform'
                });
            }

            if (document.querySelector('.tv-4x4-knowledge-grid')) {
                gsap.from('.tv-4x4-knowledge-img-wrap', {
                    scrollTrigger: {
                        trigger: '.tv-4x4-knowledge-grid',
                        start: 'top 90%',
                        once: true
                    },
                    y: 20,
                    duration: 0.7,
                    ease: 'power2.out',
                    clearProps: 'opacity,transform'
                });
                gsap.from('.tv-4x4-knowledge-card', {
                    scrollTrigger: {
                        trigger: '.tv-4x4-knowledge-grid',
                        start: 'top 90%',
                        once: true
                    },
                    y: 20,
                    duration: 0.6,
                    stagger: 0.1,
                    ease: 'power2.out',
                    clearProps: 'opacity,transform'
                });
            }
        }
    }
};

// Auto-run on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initTvPageComponents);
} else {
    window.initTvPageComponents();
}
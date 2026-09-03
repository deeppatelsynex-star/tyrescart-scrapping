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
    var closeBtn = document.getElementById('noticeClose');
    if (closeBtn) closeBtn.focus();
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
    if (modal && e.target === modal) {
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

  function initAll() {
    initMobileNav();
    initNavActiveState();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
  } else {
    initAll();
  }
})();

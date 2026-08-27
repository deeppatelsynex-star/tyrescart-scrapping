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

      window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
    });

    var sizeInput = document.getElementById('tyreSize');
    if(sizeInput){
      sizeInput.addEventListener('input', function(){ this.style.borderColor = ''; });
    }
  }

  /* ---------- Ownership notice modal ---------- */
  var modal    = document.getElementById('noticeModal');
  if(modal){
    var native   = typeof modal.showModal === 'function';
    var opener   = null;   // element that opened the modal, for focus return
    var backdrop = null;   // fallback backdrop node

    function openNotice(e){
      if(e) e.preventDefault();
      opener = (e && e.currentTarget) || null;
      document.documentElement.classList.add('modal-open');
      document.body.classList.add('modal-open');

      if(native){
        modal.showModal();
      } else {
        backdrop = document.createElement('div');
        backdrop.className = 'fb-backdrop';
        backdrop.addEventListener('click', closeNotice);
        document.body.appendChild(backdrop);
        modal.classList.add('fb-open');
        modal.setAttribute('open','');
      }
      var btn = document.getElementById('noticeClose');
      if(btn) btn.focus();
    }

    function closeNotice(){
      document.documentElement.classList.remove('modal-open');
      document.body.classList.remove('modal-open');

      if(native){
        if(modal.open) modal.close();
      } else {
        modal.classList.remove('fb-open');
        modal.removeAttribute('open');
        if(backdrop){ backdrop.remove(); backdrop = null; }
      }
      if(opener && opener.focus) opener.focus();
      opener = null;
    }

    // Any link pointing at #notice (or marked data-notice) opens the modal
    Array.prototype.forEach.call(
      document.querySelectorAll('a[href="#notice"], [data-notice]'),
      function(el){ el.addEventListener('click', openNotice); }
    );

    var closeBtn1 = document.getElementById('noticeClose');
    if(closeBtn1) closeBtn1.addEventListener('click', closeNotice);
    var closeBtn2 = document.getElementById('noticeClose2');
    if(closeBtn2) closeBtn2.addEventListener('click', closeNotice);

    // Click on the backdrop area (outside the white sheet) closes it
    modal.addEventListener('click', function(e){ if(e.target === modal) closeNotice(); });
    // Native <dialog> fires 'close' on Esc — keep body scroll state in sync
    modal.addEventListener('close', function(){
      document.documentElement.classList.remove('modal-open');
      document.body.classList.remove('modal-open');
    });
    // Esc for the fallback path
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && !native && modal.classList.contains('fb-open')) closeNotice();
    });

    // Deep link: /#notice opens the modal on load
    if(window.location.hash === '#notice') openNotice();
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();

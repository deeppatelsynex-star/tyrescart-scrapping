// Scraper Development Guide (/docs/scraper) -- purely presentational: copy
// buttons for the code blocks, and a scroll-spy on the in-page table of
// contents. No data, no upload, no scraper logic here.
(function () {
  document.addEventListener('DOMContentLoaded', () => {
    // --- Table of contents: highlight whichever section is currently in view ---
    const tocLinks = document.querySelectorAll('.guide-toc a[href^="#"]');
    if (tocLinks.length) {
      const linkById = new Map();
      tocLinks.forEach((link) => {
        linkById.set(link.getAttribute('href').slice(1), link);
      });

      const setActive = (id) => {
        tocLinks.forEach((link) => link.classList.remove('is-active'));
        const active = linkById.get(id);
        if (active) active.classList.add('is-active');
      };

      const sections = Array.from(linkById.keys())
        .map((id) => document.getElementById(id))
        .filter(Boolean);

      if (sections.length && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
          const visible = entries.filter((entry) => entry.isIntersecting);
          if (!visible.length) return;
          // Of the sections currently in the "active" band, pick the one
          // closest to the top -- that's the one the reader is actually at.
          visible.sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
          setActive(visible[0].target.id);
        }, {
          // Only counts a section as "current" once it's within the top
          // ~35% of the viewport, so the highlight doesn't flip the instant
          // a section's bottom edge scrolls into view.
          rootMargin: '0px 0px -65% 0px',
          threshold: 0,
        });
        sections.forEach((section) => observer.observe(section));
        setActive(sections[0].id);
      }

      // Instant feedback on click, without waiting for the observer.
      tocLinks.forEach((link) => {
        link.addEventListener('click', () => setActive(link.getAttribute('href').slice(1)));
      });
    }

    document.querySelectorAll('[data-copy-target]').forEach((btn) => {
      const targetId = btn.getAttribute('data-copy-target');
      const codeEl = document.getElementById(targetId);
      if (!codeEl) return;

      btn.addEventListener('click', async () => {
        const text = codeEl.textContent;
        try {
          if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
          } else {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.left = '-9999px';
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
          }
          const original = btn.textContent;
          btn.textContent = 'Copied!';
          setTimeout(() => { btn.textContent = original; }, 1500);
        } catch (err) {
          console.error('Copy failed', err);
        }
      });
    });
  });
})();

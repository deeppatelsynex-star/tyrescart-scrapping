// pages.js - TyresVision CMS Pages & Sections Editor
document.addEventListener('DOMContentLoaded', async () => {
  const pagesListEl = document.getElementById('cms-pages-list');
  if (!pagesListEl) return;

  async function loadPages() {
    try {
      const res = await fetch('/visonadmin/api/pages');
      const data = await res.json();
      renderPages(data.pages || []);
    } catch (err) {
      console.error('Error fetching pages:', err);
    }
  }

  function renderPages(pages) {
    pagesListEl.innerHTML = pages.map(p => `
      <div class="cms-card p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1">
          <div class="flex items-center gap-2.5">
            <h3 class="text-base font-bold text-slate-900">${p.title}</h3>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold ${p.status === 'Published' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}">${p.status}</span>
          </div>
          <p class="text-xs text-slate-500 font-mono">Slug: ${p.slug} • Last edited: ${p.last_edited}</p>
          ${p.sections && p.sections.length ? `<p class="text-xs text-slate-600 font-medium">${p.sections.length} customizable sections (Hero, Stats, Services, Brands, FAQ)</p>` : ''}
        </div>
        <div class="flex items-center gap-2 shrink-0">
          <a href="${p.slug}" target="_blank" class="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition">
            Preview
          </a>
          <button type="button" onclick="alert('Section editor modal for: ${p.title}')" class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition cursor-pointer">
            Edit Sections
          </button>
        </div>
      </div>
    `).join('');
  }

  loadPages();
});

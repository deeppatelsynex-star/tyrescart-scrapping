// media.js - TyresVision CMS Media Library
document.addEventListener('DOMContentLoaded', async () => {
  const mediaGridEl = document.getElementById('cms-media-grid');
  if (!mediaGridEl) return;

  async function loadMedia() {
    try {
      const res = await fetch('/visonadmin/api/media');
      const data = await res.json();
      renderMedia(data.media || []);
    } catch (err) {
      console.error('Error fetching media:', err);
    }
  }

  function renderMedia(items) {
    mediaGridEl.innerHTML = items.map(m => `
      <div class="cms-card p-3 flex flex-col justify-between group">
        <div class="w-full h-32 rounded-xl bg-slate-100 flex items-center justify-center overflow-hidden mb-2">
          <img src="${m.url}" alt="${m.name}" class="max-h-full max-w-full object-contain" />
        </div>
        <div class="space-y-1">
          <p class="text-xs font-bold text-slate-900 truncate" title="${m.name}">${m.name}</p>
          <p class="text-[11px] text-slate-400">${m.size} • ${m.uploaded}</p>
        </div>
        <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between">
          <button type="button" onclick="navigator.clipboard.writeText('${m.url}'); alert('Copied image URL to clipboard!');" class="text-xs font-bold text-emerald-600 hover:text-emerald-700 cursor-pointer">
            Copy URL
          </button>
          <button type="button" onclick="alert('Delete ${m.name}')" class="text-xs font-bold text-rose-500 hover:text-rose-700 cursor-pointer">
            Delete
          </button>
        </div>
      </div>
    `).join('');
  }

  loadMedia();
});

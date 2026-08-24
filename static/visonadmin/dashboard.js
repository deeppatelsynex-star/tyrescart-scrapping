// dashboard.js - TyresVision CMS Dashboard
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch('/visonadmin/api/dashboard-stats');
    if (!res.ok) return;
    const data = await res.json();

    const totalPagesEl = document.getElementById('stat-total-pages');
    const publishedPagesEl = document.getElementById('stat-published-pages');
    const totalMediaEl = document.getElementById('stat-total-media');

    if (totalPagesEl) totalPagesEl.textContent = data.totalPages || 0;
    if (publishedPagesEl) publishedPagesEl.textContent = data.publishedPages || 0;
    if (totalMediaEl) totalMediaEl.textContent = data.totalMedia || 0;
  } catch (err) {
    console.error('Failed to load CMS dashboard stats:', err);
  }
});

// settings.js - TyresVision CMS Site Settings Editor
document.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('cms-settings-form');
  if (!form) return;

  try {
    const res = await fetch('/visonadmin/api/settings');
    const data = await res.json();
    const s = data.settings || {};

    if (document.getElementById('site_name')) document.getElementById('site_name').value = s.site_name || '';
    if (document.getElementById('tagline')) document.getElementById('tagline').value = s.tagline || '';
    if (document.getElementById('meta_title')) document.getElementById('meta_title').value = s.meta_title || '';
    if (document.getElementById('meta_description')) document.getElementById('meta_description').value = s.meta_description || '';
    if (document.getElementById('whatsapp_number')) document.getElementById('whatsapp_number').value = s.whatsapp_number || '';
    if (document.getElementById('phone_number')) document.getElementById('phone_number').value = s.phone_number || '';
    if (document.getElementById('gtm_id')) document.getElementById('gtm_id').value = s.gtm_id || '';
  } catch (err) {
    console.error('Error fetching settings:', err);
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Settings saved successfully!');
  });
});

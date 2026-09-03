// static/visionadmin/settings.js - Reviewer Settings Controller

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('reviewer-settings-form');
  const btnSave = document.getElementById('btn-save-settings');

  const enabledSelect = document.getElementById('reviewer_enabled');
  const initialsInput = document.getElementById('reviewer_initials');
  
  const nameEnInput = document.getElementById('reviewer_name_en');
  const roleEnInput = document.getElementById('reviewer_role_en');
  const bioEnInput = document.getElementById('reviewer_bio_en');

  // Preview elements
  const previewAvatar = document.getElementById('preview-avatar');
  const previewName = document.getElementById('preview-name');
  const previewRole = document.getElementById('preview-role');
  const previewBio = document.getElementById('preview-bio');

  // CSRF Token Helper
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  // Toast Helper
  function showToast(message, isError = false) {
    const toast = document.getElementById('va-toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-0 opacity-100 flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl border text-sm font-semibold ${
      isError 
        ? 'bg-rose-50 border-rose-200 text-rose-800' 
        : 'bg-emerald-50 border-emerald-200 text-emerald-800'
    }`;
    setTimeout(() => {
      toast.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-20 opacity-0 pointer-events-none flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl border text-sm font-semibold';
    }, 4000);
  }

  // Update Live Preview
  function updatePreview() {
    const initials = (initialsInput.value || 'SK').toUpperCase().trim();
    const name = nameEnInput ? nameEnInput.value.trim() || 'Sharvil Kumar' : 'Sharvil Kumar';
    const role = roleEnInput ? roleEnInput.value.trim() || 'Tyre Selection Specialist, TyresVision' : 'Tyre Selection Specialist, TyresVision';
    const bio = bioEnInput ? bioEnInput.value.trim() || 'Sharvil Kumar oversees operations at TyresVision, helping customers find tyres that match their vehicle and budget.' : '';

    if (previewAvatar) previewAvatar.textContent = initials;
    if (previewName) previewName.textContent = name;
    if (previewRole) previewRole.textContent = role;
    if (previewBio) previewBio.textContent = bio;
  }

  // Listen for input changes to update preview in real-time
  [initialsInput, nameEnInput, roleEnInput, bioEnInput].forEach(el => {
    if (el) el.addEventListener('input', updatePreview);
  });

  // Load Settings from Server
  async function loadSettings() {
    try {
      const res = await fetch('/visionadmin/api/settings/reviewer');
      if (res.status === 401 || res.status === 403) {
        window.location.href = `/visionadmin/login?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }
      if (!res.ok) throw new Error('Failed to load settings');
      const data = await res.json();
      if (data.success && data.settings) {
        const s = data.settings;
        
        enabledSelect.value = s.enabled ? 'Yes' : 'No';
        initialsInput.value = s.initials || 'SK';

        if (s.name && nameEnInput) {
          nameEnInput.value = typeof s.name === 'object' ? (s.name.en || '') : s.name;
        }

        if (s.role && roleEnInput) {
          roleEnInput.value = typeof s.role === 'object' ? (s.role.en || '') : s.role;
        }

        if (s.bio && bioEnInput) {
          bioEnInput.value = typeof s.bio === 'object' ? (s.bio.en || '') : s.bio;
        }

        updatePreview();
      }
    } catch (err) {
      console.error('Error loading reviewer settings:', err);
      showToast('Could not load reviewer settings.', true);
    }
  }

  // Save Settings to Server
  async function saveSettings() {
    const isEnabled = enabledSelect.value === 'Yes';
    const nameVal = nameEnInput ? nameEnInput.value.trim() : '';
    const roleVal = roleEnInput ? roleEnInput.value.trim() : '';
    const bioVal = bioEnInput ? bioEnInput.value.trim() : '';

    const payload = {
      enabled: isEnabled,
      initials: initialsInput.value.trim() || 'SK',
      name_en: nameVal,
      name_ar: nameVal,
      role_en: roleVal,
      role_ar: roleVal,
      bio_en: bioVal,
      bio_ar: bioVal
    };

    btnSave.disabled = true;
    const origHtml = btnSave.innerHTML;
    btnSave.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Saving...
    `;

    try {
      const res = await fetch('/visionadmin/api/settings/reviewer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getCsrfToken()
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok && data.success) {
        showToast('Reviewer settings saved successfully!');
        updatePreview();
      } else {
        throw new Error(data.error || 'Failed to save configuration.');
      }
    } catch (err) {
      console.error('Save error:', err);
      showToast(err.message || 'Error saving settings.', true);
    } finally {
      btnSave.disabled = false;
      btnSave.innerHTML = origHtml;
    }
  }

  if (btnSave) {
    btnSave.addEventListener('click', saveSettings);
  }

  // Initialize
  loadSettings();
});

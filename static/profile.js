(function () {
  let currentUser = null;
  let csrfToken = null;

  function getInitial(user) {
    const source = (user && (user.name || user.email)) || '';
    const ch = source.trim().charAt(0);
    return ch ? ch.toUpperCase() : '?';
  }

  function renderAvatarInto(el, user) {
    if (!el) return;
    el.innerHTML = '';
    if (user && user.avatar) {
      const img = document.createElement('img');
      img.src = user.avatar;
      img.alt = user.name || 'avatar';
      img.className = 'w-full h-full object-cover';
      img.onerror = () => {
        el.innerHTML = '';
        el.textContent = getInitial(user);
      };
      el.appendChild(img);
    } else {
      el.textContent = getInitial(user);
    }
  }

  function renderEverywhere() {
    renderAvatarInto(document.getElementById('profile-avatar-header'), currentUser);
    renderAvatarInto(document.getElementById('profile-avatar-dropdown'), currentUser);
    renderAvatarInto(document.getElementById('profile-avatar-sidebar'), currentUser);

    const nameHeader = document.getElementById('profile-name-header');
    if (nameHeader) nameHeader.textContent = currentUser ? currentUser.name : 'Account';
    const nameDropdown = document.getElementById('profile-name-dropdown');
    if (nameDropdown) nameDropdown.textContent = currentUser ? currentUser.name : '—';
    const emailDropdown = document.getElementById('profile-email-dropdown');
    if (emailDropdown) emailDropdown.textContent = currentUser ? currentUser.email : '—';
    const nameSidebar = document.getElementById('profile-name-sidebar');
    if (nameSidebar) nameSidebar.textContent = currentUser ? currentUser.name : '—';
  }

  async function fetchMe() {
    const res = await fetch('/api/me');
    if (!res.ok) return;
    const data = await res.json();
    currentUser = data.user;
    csrfToken = data.csrfToken;
    renderEverywhere();
  }

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
  }

  function closeModal(el) {
    el.classList.add('hidden');
  }

  function populateViewProfile() {
    document.getElementById('vp-name').textContent = (currentUser && currentUser.name) || '—';
    document.getElementById('vp-email').textContent = (currentUser && currentUser.email) || '—';
    document.getElementById('vp-role').textContent = (currentUser && currentUser.role) || '—';
    document.getElementById('vp-status').textContent = currentUser && currentUser.status ? 'Active' : 'Inactive';
    document.getElementById('vp-updated').textContent = (currentUser && currentUser.updatedAt) || '—';
    renderAvatarInto(document.getElementById('vp-avatar'), currentUser);
  }

  function populateChangeProfileForm() {
    document.getElementById('cp-name').value = (currentUser && currentUser.name) || '';
    document.getElementById('cp-email').value = (currentUser && currentUser.email) || '';
    document.getElementById('cp-avatar-url').value = (currentUser && currentUser.avatar) || '';
    document.getElementById('cp-error').classList.add('hidden');
    document.getElementById('cp-success').classList.add('hidden');
    renderAvatarInto(document.getElementById('cp-avatar-preview'), currentUser);
  }

  function resetChangePasswordForm() {
    document.getElementById('change-password-form').reset();
    document.getElementById('pw-error').classList.add('hidden');
    document.getElementById('pw-success').classList.add('hidden');
  }

  async function handleChangeProfileSubmit(event) {
    event.preventDefault();
    const errEl = document.getElementById('cp-error');
    const okEl = document.getElementById('cp-success');
    errEl.classList.add('hidden');
    okEl.classList.add('hidden');

    const submitBtn = document.getElementById('cp-submit');
    const submitLabel = document.getElementById('cp-submit-label');
    submitBtn.disabled = true;
    submitLabel.textContent = 'Saving…';

    try {
      const response = await fetch('/api/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify({
          name: document.getElementById('cp-name').value.trim(),
          email: document.getElementById('cp-email').value.trim(),
          avatar: document.getElementById('cp-avatar-url').value.trim() || null,
        }),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        errEl.textContent = data.error || 'Unable to update profile.';
        errEl.classList.remove('hidden');
        return;
      }

      currentUser = data.user;
      renderEverywhere();
      okEl.textContent = 'Profile updated successfully.';
      okEl.classList.remove('hidden');
    } catch (err) {
      errEl.textContent = 'Network error. Please try again.';
      errEl.classList.remove('hidden');
    } finally {
      submitBtn.disabled = false;
      submitLabel.textContent = 'Save Changes';
    }
  }

  async function handleRemoveAvatar() {
    try {
      const response = await fetch('/api/profile/avatar', {
        method: 'DELETE',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok) {
        currentUser = data.user;
        document.getElementById('cp-avatar-url').value = '';
        renderEverywhere();
        renderAvatarInto(document.getElementById('cp-avatar-preview'), currentUser);
      }
    } catch (err) {
      // Best-effort; the form's own submit path surfaces real errors.
    }
  }

  async function handleChangePasswordSubmit(event) {
    event.preventDefault();
    const errEl = document.getElementById('pw-error');
    const okEl = document.getElementById('pw-success');
    errEl.classList.add('hidden');
    okEl.classList.add('hidden');

    const current = document.getElementById('pw-current').value;
    const next = document.getElementById('pw-new').value;
    const confirm = document.getElementById('pw-confirm').value;

    if (!current || !next || !confirm) {
      errEl.textContent = 'All fields are required.';
      errEl.classList.remove('hidden');
      return;
    }
    if (next !== confirm) {
      errEl.textContent = 'Passwords do not match.';
      errEl.classList.remove('hidden');
      return;
    }

    const submitBtn = document.getElementById('pw-submit');
    const submitLabel = document.getElementById('pw-submit-label');
    submitBtn.disabled = true;
    submitLabel.textContent = 'Changing…';

    try {
      const response = await fetch('/api/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify({ current_password: current, new_password: next, confirm_password: confirm }),
      });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        errEl.textContent = data.error || 'Unable to change password.';
        errEl.classList.remove('hidden');
        return;
      }

      okEl.textContent = 'Password changed successfully.';
      okEl.classList.remove('hidden');
      document.getElementById('change-password-form').reset();
    } catch (err) {
      errEl.textContent = 'Network error. Please try again.';
      errEl.classList.remove('hidden');
    } finally {
      submitBtn.disabled = false;
      submitLabel.textContent = 'Change Password';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    fetchMe();

    const trigger = document.getElementById('profile-trigger');
    const dropdown = document.getElementById('profile-dropdown');

    if (trigger && dropdown) {
      trigger.addEventListener('click', (event) => {
        event.stopPropagation();
        dropdown.classList.toggle('hidden');
      });
      document.addEventListener('click', (event) => {
        if (!dropdown.contains(event.target) && !trigger.contains(event.target)) {
          dropdown.classList.add('hidden');
        }
      });
      document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') dropdown.classList.add('hidden');
      });

      dropdown.querySelectorAll('[data-action]').forEach((btn) => {
        btn.addEventListener('click', () => {
          dropdown.classList.add('hidden');
          const action = btn.getAttribute('data-action');
          if (action === 'view-profile') {
            populateViewProfile();
            openModal('view-profile-modal');
          } else if (action === 'change-profile') {
            populateChangeProfileForm();
            openModal('change-profile-modal');
          } else if (action === 'change-password') {
            resetChangePasswordForm();
            openModal('change-password-modal');
          }
        });
      });
    }

    document.querySelectorAll('[data-close-modal]').forEach((btn) => {
      btn.addEventListener('click', () => {
        closeModal(btn.closest('.fixed'));
      });
    });

    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', async () => {
        const response = await fetch('/logout', { method: 'POST' });
        const data = await response.json().catch(() => ({}));
        window.location.href = data.redirect || '/login';
      });
    }

    const changeProfileForm = document.getElementById('change-profile-form');
    if (changeProfileForm) {
      changeProfileForm.addEventListener('submit', handleChangeProfileSubmit);
      document.getElementById('cp-remove-avatar').addEventListener('click', handleRemoveAvatar);
      document.getElementById('cp-avatar-url').addEventListener('input', (event) => {
        renderAvatarInto(document.getElementById('cp-avatar-preview'), {
          name: currentUser && currentUser.name,
          avatar: event.target.value || null,
        });
      });
    }

    const changePasswordForm = document.getElementById('change-password-form');
    if (changePasswordForm) {
      changePasswordForm.addEventListener('submit', handleChangePasswordSubmit);
    }
  });
})();

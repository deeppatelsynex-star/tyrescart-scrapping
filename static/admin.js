// Wires up every "show password" eye button on the page (Change Password modal,
// admin create/edit user form, reset-password page, etc). A button opts in with
// data-toggle-password="<id of the password input it controls>" and holds its
// own .icon-eye-open/.icon-eye-closed markup, scoped per-button rather than by
// id, so one page can have several password fields each with their own toggle.
// Runs on every page that loads this script, independent of the admin-page
// logic below.
(function () {
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-toggle-password]').forEach((btn) => {
      const input = document.getElementById(btn.getAttribute('data-toggle-password'));
      if (!input) return;

      const eyeOpen = btn.querySelector('.icon-eye-open');
      const eyeClosed = btn.querySelector('.icon-eye-closed');

      btn.addEventListener('click', () => {
        const showing = input.type === 'text';
        input.type = showing ? 'password' : 'text';
        if (eyeOpen) eyeOpen.classList.toggle('hidden', !showing);
        if (eyeClosed) eyeClosed.classList.toggle('hidden', showing);
      });
    });
  });
})();

(function () {
  const rowsEl = document.getElementById('admin-user-rows');
  if (!rowsEl) return; // Not on the admin page.

  const emptyState = document.getElementById('admin-empty-state');
  const errorEl = document.getElementById('admin-error');
  const newUserBtn = document.getElementById('admin-new-user-btn');

  const modal = document.getElementById('admin-user-modal');
  const modalTitle = document.getElementById('admin-modal-title');
  const modalError = document.getElementById('admin-modal-error');
  const form = document.getElementById('admin-user-form');
  const idInput = document.getElementById('admin-user-id');
  const nameInput = document.getElementById('admin-user-name');
  const emailInput = document.getElementById('admin-user-email');
  const passwordInput = document.getElementById('admin-user-password');
  const passwordHint = document.getElementById('admin-user-password-hint');
  const roleSelect = document.getElementById('admin-user-role');
  const statusInput = document.getElementById('admin-user-status');
  const submitBtn = document.getElementById('admin-user-submit');
  const submitLabel = document.getElementById('admin-user-submit-label');

  const deleteModal = document.getElementById('admin-delete-modal');
  const deleteText = document.getElementById('admin-delete-text');
  const deleteError = document.getElementById('admin-delete-error');
  const deleteConfirmBtn = document.getElementById('admin-delete-confirm');

  let csrfToken = null;
  let currentRole = null;
  let currentUserId = null;
  let users = [];
  let pendingDeleteId = null;

  const openModal = (el) => el.classList.remove('hidden');
  const closeModal = (el) => el.classList.add('hidden');

  const showError = (el, message) => {
    el.textContent = message;
    el.classList.remove('hidden');
  };
  const hideError = (el) => {
    el.classList.add('hidden');
    el.textContent = '';
  };

  const escapeHtml = (str) => {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  };

  const roleBadgeClasses = (role) => {
    if (role === 'SuperAdmin') return 'bg-violet-100 text-violet-700';
    if (role === 'Admin') return 'bg-sky-100 text-sky-700';
    return 'bg-slate-100 text-slate-600';
  };

  // --- Toast notifications: brief floating confirmations for action results,
  // separate from the inline form errors (which stay open so validation
  // issues remain visible while the user fixes them). ---
  let toastContainer = null;

  function getToastContainer() {
    if (toastContainer) return toastContainer;
    toastContainer = document.createElement('div');
    toastContainer.setAttribute('aria-live', 'polite');
    toastContainer.style.cssText =
      'position:fixed; top:1rem; right:1rem; z-index:9999; display:flex; flex-direction:column; gap:0.5rem; max-width:22rem; pointer-events:none;';
    document.body.appendChild(toastContainer);
    return toastContainer;
  }

  function showToast(message, type) {
    const isError = type === 'error';
    const container = getToastContainer();

    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
      pointer-events: auto;
      padding: 0.75rem 1rem;
      border-radius: 0.75rem;
      font-size: 0.8125rem;
      font-weight: 600;
      line-height: 1.3;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
      border: 1px solid ${isError ? '#fecdd3' : '#a7f3d0'};
      background-color: ${isError ? '#fff1f2' : '#ecfdf5'};
      color: ${isError ? '#be123c' : '#047857'};
      opacity: 0;
      transform: translateY(-6px);
      transition: opacity 0.2s ease, transform 0.2s ease;
    `;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-6px)';
      setTimeout(() => toast.remove(), 200);
    }, 3500);
  }

  function renderRows() {
    rowsEl.innerHTML = '';
    emptyState.classList.toggle('hidden', users.length > 0);

    users.forEach((user) => {
      const isSelf = user.userId === currentUserId;
      const canDelete = (currentRole === 'SuperAdmin' || currentRole === 'Admin') && user.role !== 'SuperAdmin' && !isSelf;
      const deleteDisabledReason = user.role === 'SuperAdmin'
        ? 'SuperAdmin accounts can never be deleted'
        : isSelf
          ? 'You cannot delete your own account'
          : '';
      const statusBadge = user.isDeleted
        ? '<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-200 text-slate-500">Deleted</span>'
        : user.status
          ? '<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">Active</span>'
          : '<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-700">Disabled</span>';

      // A deleted account swaps Delete for Recover -- and only a SuperAdmin
      // may bring an account back.
      const canRecover = currentRole === 'SuperAdmin';
      const deleteOrRecoverButton = user.isDeleted
        ? `<button type="button" data-recover="${user.userId}" ${canRecover ? '' : 'disabled title="Only a SuperAdmin can recover this account"'}
            class="text-xs font-semibold ${canRecover ? 'text-emerald-600 hover:underline cursor-pointer' : 'text-slate-300 cursor-not-allowed'}">Recover</button>`
        : `<button type="button" data-delete="${user.userId}" ${canDelete ? '' : `disabled title="${deleteDisabledReason}"`}
            class="text-xs font-semibold ${canDelete ? 'text-rose-600 hover:underline cursor-pointer' : 'text-slate-300 cursor-not-allowed'}">Delete</button>`;

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="px-6 py-3 font-medium text-slate-800">${escapeHtml(user.name)}</td>
        <td class="px-6 py-3 text-slate-600">${escapeHtml(user.email)}</td>
        <td class="px-6 py-3"><span class="px-2 py-0.5 rounded-full text-xs font-semibold ${roleBadgeClasses(user.role)}">${escapeHtml(user.role)}</span></td>
        <td class="px-6 py-3">${statusBadge}</td>
        <td class="px-6 py-3 text-right whitespace-nowrap">
          <button type="button" data-edit="${user.userId}" class="text-xs font-semibold text-emerald-600 hover:underline cursor-pointer mr-3">Edit</button>
          ${deleteOrRecoverButton}
        </td>
      `;
      rowsEl.appendChild(tr);
    });
  }

  async function loadMe() {
    const response = await fetch('/api/me');
    if (!response.ok) return;
    const data = await response.json();
    csrfToken = data.csrfToken;
    currentRole = data.user ? data.user.role : null;
    currentUserId = data.user ? data.user.userId : null;
    // Only a SuperAdmin can add a user -- an Admin can still view/edit/delete,
    // so hide the button that would otherwise just 403.
    newUserBtn.classList.toggle('hidden', currentRole !== 'SuperAdmin');
  }

  async function loadUsers() {
    hideError(errorEl);
    try {
      const response = await fetch('/api/admin/users');
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to load users.';
        showError(errorEl, message);
        showToast(message, 'error');
        return;
      }
      users = data.users || [];
      renderRows();
    } catch (err) {
      showError(errorEl, 'Network error while loading users.');
      showToast('Network error while loading users.', 'error');
    }
  }

  function resetForm() {
    form.reset();
    idInput.value = '';
    hideError(modalError);
    roleSelect.value = 'User';
    statusInput.checked = true;
  }

  function openCreateModal() {
    resetForm();
    modalTitle.textContent = 'New User';
    submitLabel.textContent = 'Create User';
    passwordInput.required = true;
    passwordHint.classList.add('hidden');
    openModal(modal);
  }

  function openEditModal(user) {
    resetForm();
    modalTitle.textContent = 'Edit User';
    submitLabel.textContent = 'Save Changes';
    idInput.value = user.userId;
    nameInput.value = user.name;
    emailInput.value = user.email;
    roleSelect.value = user.role;
    statusInput.checked = !!user.status;
    passwordInput.required = false;
    passwordHint.classList.remove('hidden');
    openModal(modal);
  }

  async function handleFormSubmit(event) {
    event.preventDefault();
    hideError(modalError);

    const id = idInput.value;
    const payload = {
      name: nameInput.value.trim(),
      email: emailInput.value.trim(),
      role: roleSelect.value,
      status: statusInput.checked,
    };
    if (passwordInput.value) {
      payload.password = passwordInput.value;
    }

    submitBtn.disabled = true;
    try {
      const response = await fetch(id ? `/api/admin/users/${id}` : '/api/admin/users', {
        method: id ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken },
        body: JSON.stringify(payload),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to save user.';
        showError(modalError, message);
        showToast(message, 'error');
        return;
      }
      closeModal(modal);
      showToast(id ? 'User updated successfully.' : 'User created successfully.', 'success');
      await loadUsers();
    } catch (err) {
      showError(modalError, 'Network error. Please try again.');
      showToast('Network error. Please try again.', 'error');
    } finally {
      submitBtn.disabled = false;
    }
  }

  async function handleDeleteConfirm() {
    if (!pendingDeleteId) return;
    hideError(deleteError);
    deleteConfirmBtn.disabled = true;
    try {
      const response = await fetch(`/api/admin/users/${pendingDeleteId}`, {
        method: 'DELETE',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = data.error || 'Unable to delete user.';
        showError(deleteError, message);
        showToast(message, 'error');
        return;
      }
      closeModal(deleteModal);
      pendingDeleteId = null;
      showToast('User deleted successfully.', 'success');
      await loadUsers();
    } catch (err) {
      showError(deleteError, 'Network error. Please try again.');
      showToast('Network error. Please try again.', 'error');
    } finally {
      deleteConfirmBtn.disabled = false;
    }
  }

  async function handleRecover(userId, btn) {
    btn.disabled = true;
    try {
      const response = await fetch(`/api/admin/users/${userId}/recover`, {
        method: 'POST',
        headers: { 'X-CSRF-Token': csrfToken },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        showToast(data.error || 'Unable to recover user.', 'error');
        btn.disabled = false;
        return;
      }
      showToast('User recovered successfully.', 'success');
      await loadUsers();
    } catch (err) {
      showToast('Network error. Please try again.', 'error');
      btn.disabled = false;
    }
  }

  document.addEventListener('DOMContentLoaded', async () => {
    await loadMe();
    await loadUsers();

    newUserBtn.addEventListener('click', openCreateModal);
    form.addEventListener('submit', handleFormSubmit);
    deleteConfirmBtn.addEventListener('click', handleDeleteConfirm);

    rowsEl.addEventListener('click', (event) => {
      const editId = event.target.getAttribute('data-edit');
      const deleteId = event.target.getAttribute('data-delete');

      if (editId) {
        const user = users.find((u) => String(u.userId) === editId);
        if (user) openEditModal(user);
        return;
      }

      if (deleteId && !event.target.disabled) {
        pendingDeleteId = deleteId;
        const user = users.find((u) => String(u.userId) === deleteId);
        deleteText.textContent = user
          ? `This will disable "${user.name}"'s account. They will no longer be able to log in.`
          : 'This will disable this account.';
        hideError(deleteError);
        openModal(deleteModal);
        return;
      }

      const recoverId = event.target.getAttribute('data-recover');
      if (recoverId && !event.target.disabled) {
        handleRecover(recoverId, event.target);
      }
    });
  });
})();

/**
 * static/visionadmin/users.js
 * Comprehensive Administrator User Management UI & API Connector for admin_users Table.
 */

document.addEventListener('DOMContentLoaded', () => {
  let allUsers = [];
  let currentSearch = '';
  let currentRoleFilter = 'all';
  let currentStatusFilter = 'all';
  let deleteTargetId = null;

  // DOM Elements
  const tableBody = document.getElementById('users-table-body');
  const metricTotal = document.getElementById('metric-total');
  const metricSuper = document.getElementById('metric-super');
  const metricManagers = document.getElementById('metric-managers');
  const metricActive = document.getElementById('metric-active');

  const inputSearch = document.getElementById('input-user-search');
  const selectRole = document.getElementById('select-role-filter');
  const selectStatus = document.getElementById('select-status-filter');
  const btnRefresh = document.getElementById('btn-refresh-users');

  // Modals
  const modalCreate = document.getElementById('modal-create-user');
  const modalEdit = document.getElementById('modal-edit-user');
  const modalDelete = document.getElementById('modal-delete-user');

  const btnOpenCreate = document.getElementById('btn-open-create-modal');
  const formCreate = document.getElementById('form-create-user');
  const createErrAlert = document.getElementById('create-error-alert');
  const createErrText = document.getElementById('create-error-text');

  const formEdit = document.getElementById('form-edit-user');
  const editErrAlert = document.getElementById('edit-error-alert');
  const editErrText = document.getElementById('edit-error-text');

  const btnConfirmDelete = document.getElementById('btn-confirm-delete');
  const deleteUserName = document.getElementById('delete-user-name');

  // ---------------------------------------------------------------------------
  // 1. Toast Notification Helper
  // ---------------------------------------------------------------------------
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3 rounded-2xl shadow-xl border text-xs font-bold flex items-center gap-2.5 transition-all duration-300 transform translate-y-10 opacity-0 ${
      type === 'success' 
        ? 'bg-[#EAF7E2] border-[#C8E8B8] text-[#2E7D32]' 
        : 'bg-rose-50 border-rose-200 text-rose-700'
    }`;
    toast.innerHTML = `
      <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        ${type === 'success' ? '<polyline points="20 6 9 17 4 12"/>' : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'}
      </svg>
      <span>${escapeHtml(message)}</span>
    `;
    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-10', 'opacity-0');
    });
    setTimeout(() => {
      toast.classList.add('translate-y-10', 'opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ---------------------------------------------------------------------------
  // 2. Fetch & Render Admin Users
  // ---------------------------------------------------------------------------
  async function loadUsers() {
    try {
      const res = await fetch('/visionadmin/api/users');
      if (res.status === 401 || res.status === 403) {
        window.location.href = `/visionadmin/login?next=${encodeURIComponent(window.location.pathname)}`;
        return;
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to load administrators');

      allUsers = data.users || [];
      updateMetrics(data.metrics || {});
      renderTable();
    } catch (err) {
      tableBody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-rose-500 font-bold">Error loading users: ${escapeHtml(err.message)}</td></tr>`;
    }
  }

  function updateMetrics(metrics) {
    if (metricTotal) metricTotal.textContent = metrics.total || 0;
    if (metricSuper) metricSuper.textContent = metrics.super_admins || 0;
    if (metricManagers) metricManagers.textContent = (metrics.managers || 0) + (metrics.support || 0);
    if (metricActive) metricActive.textContent = metrics.active || 0;
  }

  function renderTable() {
    // Filter users locally
    let filtered = allUsers.filter(u => {
      const name = (u.name || '').toLowerCase();
      const email = (u.email || '').toLowerCase();
      const matchesSearch = !currentSearch || name.includes(currentSearch) || email.includes(currentSearch);

      const matchesRole = currentRoleFilter === 'all' || u.role === currentRoleFilter;
      const matchesStatus = currentStatusFilter === 'all' || 
        (currentStatusFilter === 'active' && u.is_active) || 
        (currentStatusFilter === 'inactive' && !u.is_active);

      return matchesSearch && matchesRole && matchesStatus;
    });

    if (!filtered.length) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="6" class="py-14 text-center text-slate-400">
            <svg class="w-10 h-10 mx-auto text-slate-300 mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
            </svg>
            <p class="font-bold text-sm text-[#0E1108]">No administrators found</p>
            <p class="text-xs text-slate-400 mt-0.5">${currentSearch ? 'Try clearing your search query' : 'Click "+ Add Admin User" to create one'}</p>
          </td>
        </tr>
      `;
      return;
    }

    tableBody.innerHTML = filtered.map(u => {
      const initial = (u.name || u.email || 'A')[:1].toUpperCase();
      
      // Role pill styles
      let roleBadge = '';
      if (u.role === 'super_admin' || u.role === 'SuperAdmin') {
        roleBadge = `<span class="px-2.5 py-1 rounded-full text-[11px] font-black bg-amber-50 text-amber-800 border border-amber-200/80 flex items-center gap-1.5 w-max"><span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>Super Admin</span>`;
      } else if (u.role === 'manager') {
        roleBadge = `<span class="px-2.5 py-1 rounded-full text-[11px] font-black bg-blue-50 text-blue-800 border border-blue-200/80 flex items-center gap-1.5 w-max"><span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>Manager</span>`;
      } else {
        roleBadge = `<span class="px-2.5 py-1 rounded-full text-[11px] font-black bg-purple-50 text-purple-800 border border-purple-200/80 flex items-center gap-1.5 w-max"><span class="w-1.5 h-1.5 rounded-full bg-purple-500"></span>Support</span>`;
      }

      // Status pill styles
      const statusBadge = u.is_active 
        ? `<button type="button" class="btn-toggle-status px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#EAF7E2] text-[#2E7D32] border border-[#C8E8B8] hover:bg-emerald-100 transition flex items-center gap-1.5 cursor-pointer" data-id="${u.id}" title="Click to toggle status"><span class="w-2 h-2 rounded-full bg-[#00A650] animate-pulse"></span>Active</button>`
        : `<button type="button" class="btn-toggle-status px-2.5 py-1 rounded-full text-[11px] font-bold bg-slate-100 text-slate-500 border border-slate-200 hover:bg-slate-200 transition flex items-center gap-1.5 cursor-pointer" data-id="${u.id}" title="Click to toggle status"><span class="w-2 h-2 rounded-full bg-slate-400"></span>Disabled</button>`;

      return `
        <tr class="hover:bg-slate-50/70 transition">
          <!-- Administrator Profile -->
          <td class="py-4 px-6">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-[#0E1108] text-white flex items-center justify-center font-black text-xs shrink-0 shadow-xs">
                ${initial}
              </div>
              <div class="min-w-0">
                <p class="font-extrabold text-[#0E1108] text-xs sm:text-sm truncate">${escapeHtml(u.name)}</p>
                <p class="text-[11px] text-slate-400 truncate mt-0.5">${escapeHtml(u.email)}</p>
              </div>
            </div>
          </td>

          <!-- Role -->
          <td class="py-4 px-6">
            ${roleBadge}
          </td>

          <!-- Status -->
          <td class="py-4 px-6">
            ${statusBadge}
          </td>

          <!-- Last Login -->
          <td class="py-4 px-6 text-slate-500 text-xs">
            ${escapeHtml(u.last_login_at || 'Never')}
          </td>

          <!-- Created At -->
          <td class="py-4 px-6 text-slate-500 text-xs">
            ${escapeHtml(u.created_at || '—')}
          </td>

          <!-- Action Buttons -->
          <td class="py-4 px-6 text-right">
            <div class="flex items-center justify-end gap-1.5">
              <button type="button" class="btn-edit-user p-2 rounded-xl text-slate-500 hover:text-[#00A650] hover:bg-[#EAF7E2] transition cursor-pointer" data-id="${u.id}" title="Edit Administrator">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>

              <button type="button" class="btn-delete-user p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition cursor-pointer" data-id="${u.id}" data-name="${escapeHtml(u.name)}" title="Delete Administrator">
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    attachTableActionListeners();
  }

  // ---------------------------------------------------------------------------
  // 3. Search & Filter Listeners
  // ---------------------------------------------------------------------------
  if (inputSearch) {
    inputSearch.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      renderTable();
    });
  }

  if (selectRole) {
    selectRole.addEventListener('change', (e) => {
      currentRoleFilter = e.target.value;
      renderTable();
    });
  }

  if (selectStatus) {
    selectStatus.addEventListener('change', (e) => {
      currentStatusFilter = e.target.value;
      renderTable();
    });
  }

  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      loadUsers();
      showToast('Administrator list refreshed');
    });
  }

  // ---------------------------------------------------------------------------
  // 4. Modal Helpers & Event Attachments
  // ---------------------------------------------------------------------------
  document.querySelectorAll('.btn-close-modal').forEach(btn => {
    btn.addEventListener('click', () => {
      modalCreate.classList.add('hidden');
      modalEdit.classList.add('hidden');
      modalDelete.classList.add('hidden');
    });
  });

  if (btnOpenCreate) {
    btnOpenCreate.addEventListener('click', () => {
      formCreate.reset();
      createErrAlert.classList.add('hidden');
      modalCreate.classList.remove('hidden');
      document.getElementById('create-name').focus();
    });
  }

  function attachTableActionListeners() {
    // Edit User Button Click
    document.querySelectorAll('.btn-edit-user').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        const user = allUsers.find(u => String(u.id) === String(id));
        if (!user) return;

        document.getElementById('edit-user-id').value = user.id;
        document.getElementById('edit-name').value = user.name || '';
        document.getElementById('edit-email').value = user.email || '';
        document.getElementById('edit-role').value = user.role || 'manager';
        document.getElementById('edit-password').value = '';
        document.getElementById('edit-is-active').checked = Boolean(user.is_active);

        editErrAlert.classList.add('hidden');
        modalEdit.classList.remove('hidden');
      });
    });

    // Toggle Status Click
    document.querySelectorAll('.btn-toggle-status').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        try {
          const res = await fetch(`/visionadmin/api/users/${id}/toggle-status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || 'Failed to toggle status');
          showToast(data.message || 'Status updated');
          loadUsers();
        } catch (err) {
          showToast(err.message, 'error');
        }
      });
    });

    // Delete User Button Click
    document.querySelectorAll('.btn-delete-user').forEach(btn => {
      btn.addEventListener('click', () => {
        deleteTargetId = btn.getAttribute('data-id');
        const name = btn.getAttribute('data-name');
        deleteUserName.textContent = `"${name}"`;
        modalDelete.classList.remove('hidden');
      });
    });
  }

  // ---------------------------------------------------------------------------
  // 5. Form Submissions
  // ---------------------------------------------------------------------------
  // Create User Form Submit
  if (formCreate) {
    formCreate.addEventListener('submit', async (e) => {
      e.preventDefault();
      createErrAlert.classList.add('hidden');

      const name = document.getElementById('create-name').value.trim();
      const email = document.getElementById('create-email').value.trim();
      const role = document.getElementById('create-role').value;
      const password = document.getElementById('create-password').value;
      const isActive = document.getElementById('create-is-active').checked;

      if (!name || !email || !password) {
        createErrText.textContent = 'Please fill in all required fields.';
        createErrAlert.classList.remove('hidden');
        return;
      }

      if (password.length < 8) {
        createErrText.textContent = 'Password must be at least 8 characters long.';
        createErrAlert.classList.remove('hidden');
        return;
      }

      const submitBtn = document.getElementById('btn-submit-create');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating...';

      try {
        const res = await fetch('/visionadmin/api/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({
            name,
            email,
            role,
            password,
            is_active: isActive ? 1 : 0
          })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to create administrator.');

        modalCreate.classList.add('hidden');
        showToast(data.message || 'Administrator created successfully!');
        loadUsers();
      } catch (err) {
        createErrText.textContent = err.message;
        createErrAlert.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Create Administrator';
      }
    });
  }

  // Edit User Form Submit
  if (formEdit) {
    formEdit.addEventListener('submit', async (e) => {
      e.preventDefault();
      editErrAlert.classList.add('hidden');

      const id = document.getElementById('edit-user-id').value;
      const name = document.getElementById('edit-name').value.trim();
      const email = document.getElementById('edit-email').value.trim();
      const role = document.getElementById('edit-role').value;
      const password = document.getElementById('edit-password').value;
      const isActive = document.getElementById('edit-is-active').checked;

      if (!name || !email) {
        editErrText.textContent = 'Name and email are required.';
        editErrAlert.classList.remove('hidden');
        return;
      }

      if (password && password.length < 8) {
        editErrText.textContent = 'New password must be at least 8 characters.';
        editErrAlert.classList.remove('hidden');
        return;
      }

      const submitBtn = document.getElementById('btn-submit-edit');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving...';

      try {
        const payload = {
          name,
          email,
          role,
          is_active: isActive ? 1 : 0
        };
        if (password) payload.password = password;

        const res = await fetch(`/visionadmin/api/users/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to update administrator.');

        modalEdit.classList.add('hidden');
        showToast(data.message || 'Administrator updated successfully!');
        loadUsers();
      } catch (err) {
        editErrText.textContent = err.message;
        editErrAlert.classList.remove('hidden');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Changes';
      }
    });
  }

  // Delete Confirmation Submit
  if (btnConfirmDelete) {
    btnConfirmDelete.addEventListener('click', async () => {
      if (!deleteTargetId) return;

      btnConfirmDelete.disabled = true;
      btnConfirmDelete.textContent = 'Deleting...';

      try {
        const res = await fetch(`/visionadmin/api/users/${deleteTargetId}`, {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to delete user.');

        modalDelete.classList.add('hidden');
        showToast(data.message || 'Administrator deleted successfully.');
        loadUsers();
      } catch (err) {
        showToast(err.message, 'error');
        modalDelete.classList.add('hidden');
      } finally {
        btnConfirmDelete.disabled = false;
        btnConfirmDelete.textContent = 'Yes, Delete Account';
        deleteTargetId = null;
      }
    });
  }

  // Initial Load
  loadUsers();
});

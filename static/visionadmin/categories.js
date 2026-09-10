/**
 * static/visionadmin/categories.js
 * VisionAdmin Categories Management Module
 */

function visionCategoriesApp() {
  return {
    categories: [],
    parentOptions: [],
    loading: false,
    saving: false,
    searchQuery: '',
    statusFilter: 'all',
    trashCount: 0,
    parentFilter: '',
    currentPage: 1,
    perPage: 15,
    totalItems: 0,
    totalPages: 1,
    modalOpen: false,
    isEdit: false,
    viewMode: 'tree', // 'tree' or 'table'
    treeLoading: false,
    flatTreeNodes: [],
    treeSearch: '',
    csvModalOpen: false,
    selectedCsvFile: null,
    csvUploading: false,
    csvResult: null,
    form: {
      id: null,
      name_en: '',
      slug: '',
      parent_id: '',
      image: '',
      sort_order: 0,
      status: 'active',
      description_en: '',
      meta_title_en: '',
      meta_desc_en: ''
    },

    initData() {
      this.loadCategories(1);
      this.loadParentOptions();
      this.loadTree();
    },

    async loadTree() {
      this.treeLoading = true;
      try {
        const res = await fetch('/visionadmin/api/categories/tree');
        const data = await res.json();
        if (data.success) {
          this.flatTreeNodes = (data.flat || []).map(n => ({
            ...n,
            _expanded: true
          }));
        }
      } catch (err) {
        console.error('Error loading category tree:', err);
      } finally {
        this.treeLoading = false;
      }
    },

    toggleNode(node) {
      node._expanded = !node._expanded;
    },

    expandAllTree(expanded) {
      this.flatTreeNodes.forEach(n => {
        n._expanded = expanded;
      });
    },

    get visibleFlatTreeNodes() {
      const q = (this.treeSearch || '').toLowerCase().trim();
      const expandedMap = {};
      this.flatTreeNodes.forEach(n => {
        expandedMap[n.id] = n._expanded;
      });

      if (q) {
        const matchIds = new Set();
        this.flatTreeNodes.forEach(n => {
          const name = (n.name_en || n.name || '').toLowerCase();
          if (name.includes(q) || String(n.id) === q || (n.slug || '').toLowerCase().includes(q)) {
            matchIds.add(n.id);
            (n.path || []).forEach(ancestorId => matchIds.add(ancestorId));
          }
        });
        return this.flatTreeNodes.filter(n => matchIds.has(n.id));
      }

      return this.flatTreeNodes.filter(node => {
        if (!node.path || node.path.length <= 1) return true;
        for (let i = 0; i < node.path.length - 1; i++) {
          const ancestorId = node.path[i];
          if (expandedMap[ancestorId] === false) {
            return false;
          }
        }
        return true;
      });
    },

    slugify(text) {
      if (!text) return '';
      return text
        .toString()
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
    },

    async loadParentOptions() {
      try {
        const res = await fetch('/visionadmin/api/catalog/categories');
        const data = await res.json();
        if (data.success) {
          this.parentOptions = data.categories || [];
        }
      } catch (err) {
        console.error('Error loading parent categories:', err);
      }
    },

    async loadCategories(page = 1) {
      this.loading = true;
      this.currentPage = page;
      try {
        const params = new URLSearchParams({
          page: page,
          per_page: this.perPage,
          q: this.searchQuery || '',
          status: this.statusFilter || 'all'
        });
        if (this.statusFilter === 'trash') {
          params.set('trash', '1');
        }
        if (this.parentFilter) {
          params.append('parent_id', this.parentFilter);
        }

        const res = await fetch(`/visionadmin/api/categories/paginate?${params.toString()}`);
        const data = await res.json();

        if (data.success) {
          this.categories = data.items || [];
          this.totalItems = data.total || 0;
          this.totalPages = data.total_pages || 1;
          this.trashCount = data.trash_count || 0;
        } else {
          this.showToast(data.error || 'Failed to load categories.', 'error');
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
        this.showToast('Network error while loading categories.', 'error');
      } finally {
        this.loading = false;
      }
    },

    openCreateModal() {
      this.isEdit = false;
      this.form = {
        id: null,
        name_en: '',
        slug: '',
        parent_id: '',
        image: '',
        sort_order: (this.categories.length ? Math.max(...this.categories.map(c => c.sort_order || 0)) + 1 : 1),
        status: 'active',
        description_en: '',
        meta_title_en: '',
        meta_desc_en: ''
      };
      this.modalOpen = true;
    },

    openEditModal(c) {
      this.isEdit = true;
      this.form = {
        id: c.id,
        name_en: c.name_en || '',
        slug: c.slug || '',
        parent_id: c.parent_id || '',
        image: c.image || '',
        sort_order: c.sort_order || 0,
        status: c.status || 'active',
        description_en: c.description_en || '',
        meta_title_en: c.meta_title_en || '',
        meta_desc_en: c.meta_desc_en || ''
      };
      this.modalOpen = true;
    },

    async uploadImage(e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      const fd = new FormData();
      fd.append('image', file);

      try {
        const res = await fetch('/visionadmin/api/upload-category-image', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        if (data.success && data.url) {
          this.form.image = data.url;
          this.showToast('Category image uploaded successfully!', 'success');
        } else {
          this.showToast(data.error || 'Failed to upload category image.', 'error');
        }
      } catch (err) {
        console.error('Upload error:', err);
        this.showToast('Network error uploading category image.', 'error');
      }
    },

    async saveCategory() {
      if (!this.form.name_en.trim()) {
        this.showToast('Category name is required.', 'error');
        return;
      }

      this.saving = true;
      try {
        const url = this.isEdit
          ? `/visionadmin/api/categories/${this.form.id}`
          : '/visionadmin/api/categories';
        const method = this.isEdit ? 'PUT' : 'POST';

        const payload = {
          name_en: this.form.name_en.trim(),
          slug: this.slugify(this.form.slug || this.form.name_en),
          parent_id: this.form.parent_id ? parseInt(this.form.parent_id, 10) : null,
          image: this.form.image || null,
          sort_order: parseInt(this.form.sort_order, 10) || 0,
          status: this.form.status || 'active',
          description_en: this.form.description_en ? this.form.description_en.trim() : null,
          meta_title_en: this.form.meta_title_en ? this.form.meta_title_en.trim() : null,
          meta_desc_en: this.form.meta_desc_en ? this.form.meta_desc_en.trim() : null
        };

        const res = await fetch(url, {
          method: method,
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || (this.isEdit ? 'Category updated successfully!' : 'Category created successfully!'), 'success');
          this.modalOpen = false;
          this.loadCategories(this.isEdit ? this.currentPage : 1);
          this.loadParentOptions();
        } else {
          this.showToast(data.error || 'Failed to save category.', 'error');
        }
      } catch (err) {
        console.error('Save category error:', err);
        this.showToast('Network error while saving category.', 'error');
      } finally {
        this.saving = false;
      }
    },

    async confirmDelete(c) {
      if (!confirm(`Are you sure you want to delete category "${c.name_en}"?`)) {
        return;
      }

      try {
        const res = await fetch(`/visionadmin/api/categories/${c.id}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || 'Category deleted successfully!', 'success');
          this.loadCategories(this.currentPage);
          this.loadParentOptions();
        } else {
          this.showToast(data.error || 'Failed to delete category.', 'error');
        }
      } catch (err) {
        console.error('Delete error:', err);
        this.showToast('Network error deleting category.', 'error');
      }
    },

    async restoreCategory(c) {
      try {
        const res = await fetch(`/visionadmin/api/categories/${c.id}/restore`, {
          method: 'POST'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || 'Category restored successfully!', 'success');
          this.loadCategories(this.currentPage);
          this.loadParentOptions();
        } else {
          this.showToast(data.error || 'Failed to restore category.', 'error');
        }
      } catch (err) {
        console.error('Restore error:', err);
        this.showToast('Network error restoring category.', 'error');
      }
    },

    async purgeCategory(c) {
      if (!confirm(`Are you sure you want to PERMANENTLY delete category "${c.name_en}"? This action cannot be undone.`)) {
        return;
      }

      try {
        const res = await fetch(`/visionadmin/api/categories/${c.id}/purge`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || 'Category permanently deleted!', 'success');
          this.loadCategories(this.currentPage);
          this.loadParentOptions();
        } else {
          this.showToast(data.error || 'Failed to permanently delete category.', 'error');
        }
      } catch (err) {
        console.error('Purge error:', err);
        this.showToast('Network error permanently deleting category.', 'error');
      }
    },

    openCsvModal() {
      this.csvModalOpen = true;
      this.selectedCsvFile = null;
      this.csvResult = null;
      const el = document.getElementById('cat-csv-file-input');
      if (el) el.value = '';
    },

    async submitCsvUpload() {
      if (!this.selectedCsvFile) {
        this.showToast('Please select a CSV file first.', 'error');
        return;
      }

      this.csvUploading = true;
      this.csvResult = null;
      const fd = new FormData();
      fd.append('file', this.selectedCsvFile);

      try {
        const res = await fetch('/visionadmin/api/categories/import-csv', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        this.csvResult = data;
        if (data.success) {
          const msg = data.message || 'Categories imported successfully!';
          this.showToast(msg, 'success');
          await Promise.all([
            this.loadCategories(1),
            this.loadParentOptions(),
            this.loadTree()
          ]);
        } else {
          this.showToast(data.error || 'Failed to import CSV.', 'error');
        }
      } catch (err) {
        console.error('CSV import error:', err);
        this.csvResult = { success: false, message: 'Network error while importing CSV.' };
        this.showToast('Network error while importing CSV.', 'error');
      } finally {
        this.csvUploading = false;
      }
    },

    showToast(message, type = 'success') {
      if (window.showToast) {
        window.showToast(message, type);
        return;
      }
      const toast = document.createElement('div');
      toast.className = `fixed bottom-5 right-5 z-[99999] px-5 py-3 rounded-2xl text-xs font-bold text-white shadow-xl transition-all duration-300 transform translate-y-0 ${
        type === 'error' ? 'bg-rose-600' : 'bg-[#0E1108] border border-[#2563FF]/40 text-[#2563FF]'
      }`;
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    }
  };
}

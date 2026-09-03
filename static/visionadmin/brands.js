/**
 * static/visionadmin/brands.js
 * VisionAdmin Brands Management Module
 */

function visionBrandsApp() {
  return {
    brands: [],
    loading: false,
    saving: false,
    searchQuery: '',
    statusFilter: 'all',
    currentPage: 1,
    perPage: 15,
    totalItems: 0,
    totalPages: 1,
    modalOpen: false,
    isEdit: false,
    csvModalOpen: false,
    selectedCsvFile: null,
    csvUploading: false,
    csvResult: null,
    form: {
      id: null,
      name: '',
      slug: '',
      country: '',
      logo: '',
      sort_order: 0,
      status: 'active',
      is_featured: false,
      description_en: '',
      meta_title_en: '',
      meta_desc_en: ''
    },

    initData() {
      this.loadBrands(1);
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

    async loadBrands(page = 1) {
      this.loading = true;
      this.currentPage = page;
      try {
        const params = new URLSearchParams({
          page: page,
          per_page: this.perPage,
          q: this.searchQuery || '',
          status: this.statusFilter || 'all'
        });

        const res = await fetch(`/visionadmin/api/brands/paginate?${params.toString()}`);
        const data = await res.json();

        if (data.success) {
          this.brands = data.items || [];
          this.totalItems = data.total || 0;
          this.totalPages = data.total_pages || 1;
        } else {
          this.showToast(data.error || 'Failed to load brands.', 'error');
        }
      } catch (err) {
        console.error('Error fetching brands:', err);
        this.showToast('Network error while loading brands.', 'error');
      } finally {
        this.loading = false;
      }
    },

    openCreateModal() {
      this.isEdit = false;
      this.form = {
        id: null,
        name: '',
        slug: '',
        country: '',
        logo: '',
        sort_order: (this.brands.length ? Math.max(...this.brands.map(b => b.sort_order || 0)) + 1 : 1),
        status: 'active',
        is_featured: false,
        description_en: '',
        meta_title_en: '',
        meta_desc_en: ''
      };
      this.modalOpen = true;
    },

    openEditModal(b) {
      this.isEdit = true;
      this.form = {
        id: b.id,
        name: b.name || '',
        slug: b.slug || '',
        country: b.country || '',
        logo: b.logo || '',
        sort_order: b.sort_order || 0,
        status: b.status || 'active',
        is_featured: !!b.is_featured,
        description_en: b.description_en || '',
        meta_title_en: b.meta_title_en || '',
        meta_desc_en: b.meta_desc_en || ''
      };
      this.modalOpen = true;
    },

    async uploadLogo(e) {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      const fd = new FormData();
      fd.append('logo', file);

      try {
        const res = await fetch('/visionadmin/api/upload-brand-logo', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        if (data.success && data.url) {
          this.form.logo = data.url;
          this.showToast('Brand logo uploaded successfully!', 'success');
        } else {
          this.showToast(data.error || 'Failed to upload brand logo.', 'error');
        }
      } catch (err) {
        console.error('Upload error:', err);
        this.showToast('Network error uploading logo.', 'error');
      }
    },

    async saveBrand() {
      if (!this.form.name.trim()) {
        this.showToast('Brand name is required.', 'error');
        return;
      }

      this.saving = true;
      try {
        const url = this.isEdit
          ? `/visionadmin/api/brands/${this.form.id}`
          : '/visionadmin/api/brands';
        const method = this.isEdit ? 'PUT' : 'POST';

        const payload = {
          name: this.form.name.trim(),
          slug: this.slugify(this.form.slug || this.form.name),
          country: this.form.country ? this.form.country.trim() : null,
          logo: this.form.logo || null,
          sort_order: parseInt(this.form.sort_order, 10) || 0,
          status: this.form.status || 'active',
          is_featured: this.form.is_featured ? 1 : 0,
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
          this.showToast(data.message || (this.isEdit ? 'Brand updated successfully!' : 'Brand created successfully!'), 'success');
          this.modalOpen = false;
          this.loadBrands(this.isEdit ? this.currentPage : 1);
        } else {
          this.showToast(data.error || 'Failed to save brand.', 'error');
        }
      } catch (err) {
        console.error('Save brand error:', err);
        this.showToast('Network error while saving brand.', 'error');
      } finally {
        this.saving = false;
      }
    },

    async confirmDelete(b) {
      if (!confirm(`Are you sure you want to delete brand "${b.name}"?`)) {
        return;
      }

      try {
        const res = await fetch(`/visionadmin/api/brands/${b.id}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || 'Brand deleted successfully!', 'success');
          this.loadBrands(this.currentPage);
        } else {
          this.showToast(data.error || 'Failed to delete brand.', 'error');
        }
      } catch (err) {
        console.error('Delete error:', err);
        this.showToast('Network error deleting brand.', 'error');
      }
    },

    openCsvModal() {
      this.csvModalOpen = true;
      this.selectedCsvFile = null;
      this.csvResult = null;
      const el = document.getElementById('brand-csv-file-input');
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
        const res = await fetch('/visionadmin/api/brands/import-csv', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        this.csvResult = data;
        if (data.success) {
          this.showToast(data.message || `Successfully imported ${data.imported} brands!`, 'success');
          this.loadBrands(1);
          setTimeout(() => {
            this.csvModalOpen = false;
          }, 1800);
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
        type === 'error' ? 'bg-rose-600' : 'bg-[#0E1108] border border-[#58B31B]/40 text-[#58B31B]'
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

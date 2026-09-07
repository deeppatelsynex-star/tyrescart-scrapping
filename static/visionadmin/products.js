/**
 * static/visionadmin/products.js - Products Catalog Studio Alpine Component
 * Phase 6.4 Catalog Products Management
 */

function visionProductsApp() {
  return {
    products: [],
    brands: [],
    categories: [],
    counts: { total: 0, in_stock: 0, out_of_stock: 0, inactive: 0, trash: 0 },
    loading: false,
    isSubmitting: false,
    currentTab: 'active',
    currentPage: 1,
    perPage: 25,
    totalPages: 1,
    totalItems: 0,
    selectedIds: [],
    bulkActionChoice: '',
    modalOpen: false,
    viewModalOpen: false,
    isEditMode: false,
    formTab: 'basic',
    activeProduct: null,
    viewProductSchema: null,
    attributeSets: [],
    csvModalOpen: false,
    selectedCsvFile: null,
    csvUploading: false,
    csvResult: null,

    accordions: {
      sources: true,
      content: false,
      configurations: false,
      subscriptions: false,
      media: false,
      seo: false,
      websites: false,
      related: false,
      custom_options: false,
      design: false,
      schedule: false,
      gift: false,
      downloadable: false
    },

    toggleAccordion(key) {
      this.accordions[key] = !this.accordions[key];
    },

    formatScope(scope) {
      if (!scope) return 'global';
      const s = String(scope).toLowerCase();
      if (s === 'store_view' || s === 'store') return 'store view';
      if (s === 'website') return 'website';
      return 'global';
    },

    handleMultiselectChange(code, e) {
      const selected = Array.from(e.target.selectedOptions).map(opt => opt.value);
      this.form.dynamic_attributes[code] = selected.join(',');
      this.syncDynamicField(code, this.form.dynamic_attributes[code]);
    },

    openAddAttributeModal() {
      window.open('/visionadmin/attributes', '_blank');
    },

    syncDynamicField(code, val) {
      if (!this.form.dynamic_attributes) this.form.dynamic_attributes = {};
      this.form.dynamic_attributes[code] = val;

      if (code === 'product_name' || code === 'display_name') {
        this.form.display_name = val;
      } else if (code === 'sku') {
        this.form.sku = val;
      } else if (code === 'price') {
        this.form.price = val;
      } else if (code === 'sale_price' || code === 'promotion') {
        this.form.sale_price = val;
      } else if (code === 'weight') {
        this.form.weight = val;
      } else if (code === 'visibility') {
        this.form.visibility = val;
      } else if (code === 'tabby_payment') {
        this.form.pay_later_eligible = Boolean(val);
      } else if (code === 'country_of_manufacture' || code === 'country_of_origin') {
        this.form.country_of_origin = val;
      } else if (code === 'brand') {
        const found = (this.brands || []).find(b => String(b.name).toLowerCase() === String(val).toLowerCase() || b.id == val);
        if (found) this.form.brand_id = found.id;
      } else if (code === 'tire_size_label' || code === 'tire_size') {
        this.form.tire_size_label = val;
      } else if (code === 'width') {
        this.form.width = val;
        this.calculateSizeLabel();
      } else if (code === 'aspect_ratio' || code === 'height') {
        this.form.aspect_ratio = val;
        this.calculateSizeLabel();
      } else if (code === 'rim_size' || code === 'rim') {
        this.form.rim_size = val;
        this.calculateSizeLabel();
      } else if (code === 'tire_pattern' || code === 'pattern') {
        this.form.tire_pattern = val;
      } else if (code === 'run_flat' || code === 'runflat') {
        this.form.run_flat = Boolean(val);
      } else if (code === 'ev_rated' || code === 'ev_tyre') {
        this.form.ev_rated = Boolean(val);
      } else if (code === 'warranty_period' || code === 'warranty_months') {
        this.form.warranty_months = val;
      }
    },

    filters: {
      search: '',
      brand_id: '',
      category_id: '',
      vehicle_type: '',
      stock_status: '',
      attribute_set_id: ''
    },

    form: {
      id: null,
      attribute_set_id: 2,
      dynamic_attributes: {},
      attribute_groups: [],
      loadingSchema: false,
      sku: '',
      display_name: '',
      brand_id: '',
      category_id: '',
      vehicle_type: 'car',
      short_desc_en: '',
      description_en: '',
      width: '',
      aspect_ratio: '',
      rim_size: '',
      tire_size_label: '',
      tire_speed_rating: '',
      tire_load_index: '',
      tire_type: 'summer',
      tire_pattern: '',
      oem_brand: '',
      run_flat: false,
      ev_rated: false,
      oem_approved: false,
      price: '',
      sale_price: '',
      list_price: '',
      cost_price: '',
      stock_qty: 0,
      stock_status: 'in_stock',
      pay_later_eligible: true,
      image_path: '',
      country_of_origin: '',
      warranty_months: '',
      weight: '',
      status: 'active',
      visibility: 'visible',
      is_featured: false,
      is_new: false,
      meta_title_en: '',
      meta_desc_en: '',
      canonical_url: ''
    },

    async initData() {
      await Promise.all([this.fetchBrands(), this.fetchCategories(), this.fetchAttributeSets()]);
      await this.fetchProducts();

      // Listen to filter search debounce
      this.$watch('filters.search', () => {
        this.currentPage = 1;
        this.fetchProducts();
      });
    },

    async fetchBrands() {
      try {
        const res = await fetch('/visionadmin/api/brands');
        const data = await res.json();
        if (data.success) {
          this.brands = data.brands || [];
        }
      } catch (err) {
        console.error('Error fetching brands:', err);
      }
    },

    async fetchCategories() {
      try {
        const res = await fetch('/visionadmin/api/catalog/categories');
        const data = await res.json();
        if (data.success) {
          this.categories = data.categories || [];
        }
      } catch (err) {
        console.error('Error fetching categories:', err);
      }
    },

    async fetchAttributeSets() {
      try {
        const res = await fetch('/visionadmin/api/attribute-sets');
        const data = await res.json();
        if (data.success || data.attribute_sets) {
          this.attributeSets = data.attribute_sets || [];
        }
      } catch (err) {
        console.error('Error fetching attribute sets:', err);
      }
    },

    async onAttributeSetChange(setId, productId = null) {
      if (!setId) return;
      this.form.loadingSchema = true;
      try {
        const query = productId ? `?product_id=${productId}` : '';
        const res = await fetch(`/visionadmin/api/catalog/form-schema/${setId}${query}`);
        const data = await res.json();
        if (data.schema && data.schema.groups) {
          this.form.attribute_groups = data.schema.groups || [];
          // Initialize dynamic attributes mapping if not already set
          this.form.attribute_groups.forEach(group => {
            (group.attributes || []).forEach(attr => {
              if (this.form.dynamic_attributes[attr.code] === undefined) {
                if (attr.type === 'boolean') {
                  this.form.dynamic_attributes[attr.code] = (attr.current_value !== undefined && attr.current_value !== null) ? Boolean(attr.current_value) : false;
                } else {
                  this.form.dynamic_attributes[attr.code] = (attr.current_value !== undefined && attr.current_value !== null) ? attr.current_value : (attr.default_value || '');
                }
              }
              this.syncDynamicField(attr.code, this.form.dynamic_attributes[attr.code]);
            });
          });
        }
      } catch (err) {
        console.error('Error loading dynamic form schema:', err);
      } finally {
        this.form.loadingSchema = false;
      }
    },

    formatGroupName(g) {
      if (!g) return '';
      if (typeof g.name === 'object' && g.name !== null) {
        return g.name.en || g.name.ar || g.code || 'Group';
      }
      if (typeof g.name === 'string' && g.name.trim().startsWith('{')) {
        try {
          const parsed = JSON.parse(g.name);
          return parsed.en || parsed.ar || g.name;
        } catch(e) {}
      }
      return g.name || g.code || 'Group';
    },

    formatAttrName(attr) {
      if (!attr) return '';
      if (typeof attr.name === 'object' && attr.name !== null) {
        return attr.name.en || attr.name.ar || attr.code || '';
      }
      if (typeof attr.name === 'string' && attr.name.trim().startsWith('{')) {
        try {
          const parsed = JSON.parse(attr.name);
          return parsed.en || parsed.ar || attr.name;
        } catch(e) {
          return attr.name;
        }
      }
      return attr.name || attr.code || '';
    },

    async fetchProducts() {
      this.loading = true;
      try {
        const params = new URLSearchParams({
          page: this.currentPage,
          per_page: this.perPage,
          sort_by: 'created_at',
          sort_dir: 'DESC'
        });

        if (this.filters.search) params.append('search', this.filters.search);
        if (this.filters.brand_id) params.append('brand_id', this.filters.brand_id);
        if (this.filters.category_id) params.append('category_id', this.filters.category_id);
        if (this.filters.vehicle_type) params.append('vehicle_type', this.filters.vehicle_type);
        if (this.filters.stock_status) params.append('stock_status', this.filters.stock_status);
        if (this.filters.attribute_set_id) params.append('attribute_set_id', this.filters.attribute_set_id);

        if (this.currentTab === 'trash') {
          params.append('trash', '1');
        } else if (this.currentTab === 'out_of_stock') {
          params.append('stock_status', 'out_of_stock');
        }

        const res = await fetch('/visionadmin/api/products?' + params.toString());
        const data = await res.json();

        this.products = data.items || [];
        this.totalItems = data.total || 0;
        this.totalPages = data.total_pages || 1;
        this.currentPage = data.page || 1;
        if (data.counts) {
          this.counts = data.counts;
        }
      } catch (err) {
        console.error('Error fetching products:', err);
        this.showToast('Failed to load products.', 'error');
      } finally {
        this.loading = false;
      }
    },

    setTab(tab) {
      this.currentTab = tab;
      this.currentPage = 1;
      this.selectedIds = [];
      this.fetchProducts();
    },

    resetFilters() {
      this.filters = {
        search: '',
        brand_id: '',
        category_id: '',
        vehicle_type: '',
        stock_status: '',
        attribute_set_id: ''
      };
      this.currentPage = 1;
      this.fetchProducts();
    },

    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchProducts();
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchProducts();
      }
    },

    isAllSelected() {
      return this.products.length > 0 && this.selectedIds.length === this.products.length;
    },

    toggleSelectAll(e) {
      if (e.target.checked) {
        this.selectedIds = this.products.map(p => p.id);
      } else {
        this.selectedIds = [];
      }
    },

    calculateSizeLabel() {
      if (this.form.width && this.form.aspect_ratio && this.form.rim_size) {
        this.form.tire_size_label = `${this.form.width}/${this.form.aspect_ratio}R${this.form.rim_size}`;
      }
    },

    openCreateModal() {
      this.isEditMode = false;
      const defaultSet = (this.attributeSets || []).find(s => s.slug === 'default' || (s.name && s.name.toLowerCase() === 'default'));
      const defaultSetId = defaultSet ? defaultSet.id : 2;
      this.form = {
        id: null,
        attribute_set_id: defaultSetId,
        dynamic_attributes: {},
        attribute_groups: [],
        loadingSchema: false,
        sku: '',
        display_name: '',
        brand_id: '',
        category_id: '',
        vehicle_type: 'car',
        short_desc_en: '',
        description_en: '',
        width: '',
        aspect_ratio: '',
        rim_size: '',
        tire_size_label: '',
        tire_speed_rating: '',
        tire_load_index: '',
        tire_type: 'summer',
        tire_pattern: '',
        oem_brand: '',
        run_flat: false,
        ev_rated: false,
        oem_approved: false,
        price: '',
        sale_price: '',
        list_price: '',
        cost_price: '',
        stock_qty: 12,
        stock_status: 'in_stock',
        pay_later_eligible: true,
        image_path: '',
        country_of_origin: '',
        warranty_months: 36,
        weight: '',
        status: 'active',
        visibility: 'visible',
        is_featured: false,
        is_new: false,
        meta_title_en: '',
        meta_desc_en: '',
        canonical_url: ''
      };
      this.modalOpen = true;
      this.onAttributeSetChange(defaultSetId);
    },

    openEditModal(p) {
      this.isEditMode = true;
      this.formTab = 'basic';

      // Parse dimensions if size label exists (e.g. 205/55R16)
      let w = '', a = '', r = '';
      if (p.tire_size_label) {
        const m = p.tire_size_label.match(/(\d+)\/(\d+)R(\d+)/i);
        if (m) {
          w = m[1];
          a = m[2];
          r = m[3];
        }
      }

      const descEn = typeof p.description === 'object' && p.description ? p.description.en || '' : p.description || '';
      const shortDescEn = typeof p.short_desc === 'object' && p.short_desc ? p.short_desc.en || '' : p.short_desc || '';
      const metaTitleEn = typeof p.meta_title === 'object' && p.meta_title ? p.meta_title.en || '' : p.meta_title || '';
      const metaDescEn = typeof p.meta_desc === 'object' && p.meta_desc ? p.meta_desc.en || '' : p.meta_desc || '';

      const setId = p.attribute_set_id || 1;
      const dynAttrs = Object.assign({}, p.attributes_json || {});

      this.form = {
        id: p.id,
        attribute_set_id: setId,
        dynamic_attributes: dynAttrs,
        attribute_groups: [],
        loadingSchema: false,
        sku: p.sku || '',
        display_name: p.display_name || p.name_en || '',
        brand_id: p.brand_id || '',
        category_id: p.category_id || '',
        vehicle_type: p.vehicle_type || 'car',
        short_desc_en: shortDescEn,
        description_en: descEn,
        width: w,
        aspect_ratio: a,
        rim_size: r,
        tire_size_label: p.tire_size_label || '',
        tire_speed_rating: p.tire_speed_rating || '',
        tire_load_index: p.tire_load_index || '',
        tire_type: p.tire_type || 'summer',
        tire_pattern: p.tire_pattern || '',
        oem_brand: p.oem_brand || '',
        run_flat: Boolean(p.run_flat),
        ev_rated: Boolean(p.ev_rated),
        oem_approved: Boolean(p.oem_approved),
        price: p.price != null ? p.price : '',
        sale_price: p.sale_price != null ? p.sale_price : '',
        list_price: p.list_price != null ? p.list_price : '',
        cost_price: p.cost_price != null ? p.cost_price : '',
        stock_qty: p.stock_qty != null ? p.stock_qty : 0,
        stock_status: p.stock_status || 'in_stock',
        pay_later_eligible: Boolean(p.pay_later_eligible),
        image_path: p.image_path || '',
        country_of_origin: p.country_of_origin || '',
        warranty_months: p.warranty_months != null ? p.warranty_months : '',
        weight: p.weight != null ? p.weight : '',
        status: p.status || 'active',
        visibility: p.visibility || 'visible',
        is_featured: Boolean(p.is_featured),
        is_new: Boolean(p.is_new),
        meta_title_en: metaTitleEn,
        meta_desc_en: metaDescEn,
        canonical_url: p.canonical_url || ''
      };
      this.modalOpen = true;
      this.onAttributeSetChange(setId, p.id);
    },

    async openViewModal(p) {
      this.activeProduct = p;
      this.viewProductSchema = null;
      this.viewModalOpen = true;
      const setId = p.attribute_set_id || 1;
      try {
        const res = await fetch(`/visionadmin/api/catalog/form-schema/${setId}?product_id=${p.id}`);
        const data = await res.json();
        if (data.schema) {
          this.viewProductSchema = data.schema;
        }
      } catch (err) {
        console.error('Error fetching view product schema:', err);
      }
    },

    async uploadImage(e) {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('image', file);

      try {
        const res = await fetch('/visionadmin/api/upload-product-image', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (data.success && data.url) {
          this.form.image_path = data.url;
          this.showToast('Image uploaded successfully!', 'success');
        } else {
          this.showToast(data.error || 'Failed to upload image.', 'error');
        }
      } catch (err) {
        console.error('Image upload error:', err);
        this.showToast('Network error uploading image.', 'error');
      }
    },

    async saveProduct(closeAfter = true, newAfter = false, duplicate = false) {
      // Sync any missing fields from dynamic_attributes
      if (!this.form.sku && this.form.dynamic_attributes && this.form.dynamic_attributes.sku) {
        this.form.sku = this.form.dynamic_attributes.sku;
      }
      if (!this.form.display_name && this.form.dynamic_attributes) {
        this.form.display_name = this.form.dynamic_attributes.product_name || this.form.dynamic_attributes.display_name || '';
      }
      if ((!this.form.price || isNaN(parseFloat(this.form.price))) && this.form.dynamic_attributes && this.form.dynamic_attributes.price) {
        this.form.price = this.form.dynamic_attributes.price;
      }

      if (!this.form.sku || !this.form.sku.trim()) {
        this.showToast('Please enter a product SKU.', 'error');
        return;
      }
      if (!this.form.display_name || !this.form.display_name.trim()) {
        this.showToast('Please enter a product name.', 'error');
        return;
      }
      if (!this.form.price || isNaN(parseFloat(this.form.price))) {
        this.showToast('Please enter a valid regular price.', 'error');
        return;
      }

      this.isSubmitting = true;
      try {
        const url = (this.isEditMode && !duplicate)
          ? `/visionadmin/api/products/${this.form.id}`
          : '/visionadmin/api/products';
        const method = (this.isEditMode && !duplicate) ? 'PUT' : 'POST';

        const payload = { ...this.form };
        if (duplicate) {
          delete payload.id;
          payload.sku = payload.sku + '-COPY';
        }
        payload.attribute_set_id = this.form.attribute_set_id;
        payload.dynamic_attributes = this.form.dynamic_attributes;
        payload.attributes_json = this.form.dynamic_attributes;

        if (this.form.dynamic_attributes && this.form.dynamic_attributes.tire_size_label) {
          payload.tire_size_label = this.form.dynamic_attributes.tire_size_label;
        }

        const res = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.success) {
          this.showToast(data.message || 'Product saved successfully!', 'success');
          await this.fetchProducts();
          if (newAfter) {
            this.openCreateModal();
          } else if (closeAfter) {
            this.modalOpen = false;
          }
        } else {
          this.showToast(data.error || 'Failed to save product.', 'error');
        }
      } catch (err) {
        console.error('Save product error:', err);
        this.showToast('Network error saving product.', 'error');
      } finally {
        this.isSubmitting = false;
      }
    },

    async toggleStatus(p) {
      const newStatus = p.status === 'active' ? 'inactive' : 'active';
      try {
        const res = await fetch(`/visionadmin/api/products/${p.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (data.success) {
          p.status = newStatus;
          this.showToast(`Product set to ${newStatus}.`, 'success');
          this.fetchProducts();
        }
      } catch (err) {
        console.error('Toggle status error:', err);
      }
    },

    async deleteProduct(p) {
      if (!confirm(`Move product "${p.display_name || p.sku}" to trash?`)) return;
      try {
        const res = await fetch(`/visionadmin/api/products/${p.id}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast('Product moved to trash.', 'success');
          this.fetchProducts();
        } else {
          this.showToast(data.error || 'Failed to delete product.', 'error');
        }
      } catch (err) {
        console.error('Delete error:', err);
      }
    },

    async restoreProduct(p) {
      try {
        const res = await fetch(`/visionadmin/api/products/${p.id}/restore`, {
          method: 'POST'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast('Product restored successfully!', 'success');
          this.fetchProducts();
        }
      } catch (err) {
        console.error('Restore error:', err);
      }
    },

    async purgeProduct(p) {
      if (!confirm(`Permanently delete "${p.display_name || p.sku}"? This action cannot be undone.`)) return;
      try {
        const res = await fetch(`/visionadmin/api/products/${p.id}/purge`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.success) {
          this.showToast('Product permanently deleted.', 'success');
          this.fetchProducts();
        }
      } catch (err) {
        console.error('Purge error:', err);
      }
    },

    async applyBulkAction() {
      if (!this.bulkActionChoice) {
        this.showToast('Please select a bulk action.', 'error');
        return;
      }
      if (this.selectedIds.length === 0) {
        this.showToast('No products selected.', 'error');
        return;
      }

      if (this.bulkActionChoice === 'delete' && !confirm(`Move ${this.selectedIds.length} selected products to trash?`)) {
        return;
      }

      try {
        const res = await fetch('/visionadmin/api/products/bulk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: this.bulkActionChoice,
            ids: this.selectedIds
          })
        });
        const data = await res.json();
        if (data.success) {
          this.showToast(data.message || 'Bulk action applied.', 'success');
          this.selectedIds = [];
          this.bulkActionChoice = '';
          this.fetchProducts();
        } else {
          this.showToast(data.error || 'Failed to execute bulk action.', 'error');
        }
      } catch (err) {
        console.error('Bulk action error:', err);
      }
    },

    openCsvModal() {
      this.csvModalOpen = true;
      this.selectedCsvFile = null;
      this.csvResult = null;
      const el = document.getElementById('prod-csv-file-input');
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
        const res = await fetch('/visionadmin/api/products/import-csv', {
          method: 'POST',
          body: fd
        });
        const data = await res.json();
        this.csvResult = data;
        if (data.success) {
          this.showToast(data.message || `Successfully imported ${data.imported} products!`, 'success');
          this.fetchProducts();
          this.fetchBrands();
          this.fetchCategories();
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
      const toastEl = document.getElementById('va-toast');
      if (!toastEl) {
        alert(message);
        return;
      }
      toastEl.textContent = message;
      toastEl.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-0 opacity-100 flex items-center gap-3 px-5 py-3 rounded-2xl shadow-2xl border text-sm font-bold ' +
        (type === 'success' ? 'bg-[#0E1108] text-[#58B31B] border-[#58B31B]/40' : 'bg-rose-900 text-white border-rose-700');

      setTimeout(() => {
        toastEl.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-20 opacity-0 pointer-events-none flex items-center gap-3 px-5 py-3 rounded-2xl shadow-xl border text-sm font-semibold';
      }, 3500);
    }
  };
}

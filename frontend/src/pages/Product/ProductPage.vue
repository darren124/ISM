<template>
    <div class="product-container">
      <SuccessToast
        v-if="showSuccessToast"
        :message="toastMessage"
        @close="showSuccessToast = false"
      />
      <ErrorToast
        v-if="showErrorToast"
        :message="toastMessage"
        @close="showErrorToast = false"
      />

      <h1>Product</h1>
      <div class="product-actions">
        <div class="search-bar">
          <i class="search-icon"></i>
          <input 
            type="text" 
            placeholder="Search product by name, code, or category" 
            v-model="searchQuery"
          />
        </div>
        <div class="filter-dropdown">
          <select v-model="selectedCategory" class="filter-select">
            <option value="">All Categories</option>
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
      </div>
      
      <div v-if="productsError" class="error-message">{{ productsError }}</div>
      <div class="product-table">
        <table>
          <thead>
            <tr>
              <th>No.</th>
              <th>Name</th>
              <th>Category</th>
              <th>Code</th>
              <th>Cost</th>
              <th>Retail Price</th>
              <th>Threshold</th>
              <th>Quantity</th>
              <th class="expand-cell"></th>
              <th class="action-cell">Action</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(product, index) in paginatedProducts" :key="product.id">
              <tr :class="{'expanded': expandedProductId === product.id}">
                <td>{{ (currentPage - 1) * pageSize + index + 1 }}</td>
                <td>{{ product.name }}</td>
                <td>{{ product.category }}</td>
                <td>{{ product.code }}</td>
                <td>{{ product.cost }}</td>
                <td>{{ product.retail_price }}</td>
                <td>{{ product.stock_threshold }}</td>
                <td>{{ product.quantity }}</td>
                <td class="expand-cell">
                  <button 
                    class="expand-btn" 
                    @click="toggleExpand(product.id)"
                    :title="expandedProductId === product.id ? 'Collapse' : 'Expand'"
                  >
                    <i :class="['chevron-icon', expandedProductId === product.id ? 'chevron-up' : 'chevron-down']"></i>
                  </button>
                </td>
                <td class="action-cell">               
                  <div class="action-buttons">
                    <button 
                      class="sell-btn"
                      @click="openSellProductModal(product)"
                      title="Sell product"
                    >
                      <i class="sell-icon"></i>
                    </button>
                    <button 
                      class="edit-btn" 
                      @click="openEditModal(product)"
                      title="Edit product"
                    >
                      <i class="edit-icon"></i>
                    </button>
                    <button 
                      class="delete-btn" 
                      @click="confirmDeleteProduct(product.id)"
                      title="Delete product"
                    >
                      <i class="delete-icon"></i>
                    </button>
                  </div>
                </td>
              </tr>
              
              <!-- Expanded Batch Details -->
              <tr v-if="expandedProductId === product.id" class="batch-header">
                <td colspan="10">
                  <div class="batch-container">
                    <div class="batch-header-row">
                      <div class="batch-column batch-id">Batch ID</div>
                      <div class="batch-column batch-quantity">Quantity</div>
                      <div class="batch-column batch-expiry">Expiry Date</div>
                      <div class="batch-column batch-received">Received Date</div>
                      <div class="batch-column batch-actions">Action</div>
                    </div>
                    
                    <div class="batch-content">
                      <div v-if="product.batches && product.batches.length > 0">
                        <div 
                          v-for="(batch, index) in product.batches" 
                          :key="index"
                          class="batch-row"
                        >
                          <div class="batch-column batch-id">{{ batch.batch_id }}</div>
                          <div class="batch-column batch-quantity">{{ batch.quantity }}</div>
                          <div class="batch-column batch-expiry">{{ formatDate(batch.expiry_date) }}</div>
                          <div class="batch-column batch-received">{{ formatDate(batch.received_date) }}</div>
                          <div class="batch-column batch-actions">
                            <button class="batch-edit-btn" @click="openBatchEditModal(product.id, batch)">
                              <i class="edit-icon"></i>
                            </button>
                            <button class="batch-delete-btn" @click="confirmDeleteBatch(product.id, batch.batch_id)">
                              <i class="delete-icon"></i>
                            </button>
                          </div>
                        </div>
                      </div>
                      <div v-else class="no-batches">No batch information available</div>
                    </div>
                    
                    <div class="add-batch-container">
                      <button class="add-batch-btn" @click="openAddBatchModal(product.id)">
                        <i class="plus-icon"></i>
                        Add Batch
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
          <tr v-if="filteredProducts.length === 0">
            <td colspan="10" style="text-align: center;">No products found.</td>
          </tr>
        </table>
        <div class="pagination">
          <button @click="currentPage--" :disabled="currentPage === 1" title="Previous">
            &lt;
          </button>
          <span>
            Page
            <input
              type="number"
              v-model.number="pageInput"
              @change="goToPage"
              :min="1"
              :max="totalPages"
              style="width: 40px; text-align: center;"
            />
            of {{ totalPages }}
          </span>
          <button @click="currentPage++" :disabled="currentPage === totalPages" title="Next">
            &gt;
          </button>
        </div>
        <SalesModal
          v-if="isSalesModalOpen"
          :product="salesProduct"
          @close="closeSalesModal"
          @sale-success="showToast('Sale completed successfully!', 'success')"
        />
      </div>
      
      <button class="add-product-btn" @click="openAddModal">
        <i class="plus-icon"></i>
        Add Product
      </button>
      
      <!-- Product Modal -->
      <BaseModal
        :isOpen="isModalOpen"
        :title="modalTitle"
        @close="closeModal"
      >
        <div class="product-form">
          <div class="form-group">
            <label for="productName">Product Name:</label>
            <input 
              id="productName" 
              type="text" 
              v-model="formData.name" 
              class="form-control"
              @input="clearFieldError('name')"
            />
            <p v-if="nameError" class="field-error">{{ nameError }}</p>
          </div>
          <div class="form-group">
            <label for="productCategory">Product Category:</label>
            <v-select
              id="productCategory"
              v-model="formData.category"
              :options="categoryOptions"
              placeholder="Select or search category"
              :reduce="cat => cat"
              :taggable="true"
              @new="addCategory"
              class="form-control category-vselect"
              @input="clearFieldError('category')"
            />
            <p v-if="categoryError" class="field-error">{{ categoryError }}</p>
          </div>
          <div class="form-group">
            <label for="productCode">Product Code:</label>
            <input 
              id="productCode" 
              type="text" 
              v-model="formData.code" 
              class="form-control"
              @input="clearFieldError('code')"
            />
            <p v-if="codeError" class="field-error">{{ codeError }}</p>
          </div>
          <div class="form-group">
            <label for="productCost">Product Cost:</label>
            <input 
              id="productCost" 
              type="number" 
              step="0.01" 
              v-model="formData.cost" 
              class="form-control"
              @input="clearFieldError('cost')"
            />
            <p v-if="costError" class="field-error">{{ costError }}</p>
          </div>
          <div class="form-group">
            <label for="productRetailPrice">Product Retail Price:</label>
            <input 
              id="productRetailPrice" 
              type="number" 
              step="0.01" 
              v-model="formData.retail_price" 
              class="form-control"
              @input="clearFieldError('retail_price')"
            />
            <p v-if="retailPriceError" class="field-error">{{ retailPriceError }}</p>
          </div>
          <div class="form-group">
            <label for="productThreshold">Stock Threshold:</label>
            <input 
              id="productThreshold" 
              type="number" 
              v-model="formData.stock_threshold" 
              class="form-control"
              @input="clearFieldError('stock_threshold')"
            />
            <p v-if="thresholdError" class="field-error">{{ thresholdError }}</p>
          </div>
          <div class="form-group">
            <label for="productQuantity">Product Quantity:</label>
            <input 
              id="productQuantity" 
              type="number" 
              v-model="formData.quantity" 
              class="form-control"
              disabled
            />
            <small class="form-text">Total quantity is calculated from batches</small>
          </div>
        </div>
        <template v-slot:footer>
          <button class="submit-btn" @click="submitForm">
            {{ isEditing ? 'Update' : 'Add' }}
          </button>
        </template>
      </BaseModal>

      <!-- Delete Modal -->
      <DeleteModal
        :isOpen="showDeleteModal"
        @close="cancelDeleteProduct"
        @confirm="deleteProductConfirmed"
        message="Are you sure you want to delete this product?"
      />
      
      <!-- Batch Modal -->
      <BaseModal
        :isOpen="isBatchModalOpen"
        :title="batchModalTitle"
        @close="closeBatchModal"
      >
        <div class="product-form">      
          <div class="form-group">
            <label for="batchQuantity">Quantity:</label>
            <input 
              id="batchQuantity" 
              type="number" 
              v-model="batchFormData.quantity" 
              class="form-control"
              @input="clearBatchFieldError('quantity')"
            />
            <p v-if="batchQuantityError" class="field-error">{{ batchQuantityError }}</p>
          </div>
          <div class="form-group">
            <label for="expiryDate">Expiry Date:</label>
            <input 
              id="expiryDate" 
              type="date" 
              v-model="batchFormData.expiry_date" 
              class="form-control"
              @input="clearBatchFieldError('expiry_date')"
            />
            <p v-if="batchExpiryError" class="field-error">{{ batchExpiryError }}</p>
          </div>
          <div class="form-group">
            <label for="receivedDate">Received Date:</label>
            <input 
              id="receivedDate" 
              type="date" 
              v-model="batchFormData.received_date" 
              class="form-control"
              @input="clearBatchFieldError('received_date')"
            />
            <p v-if="batchReceivedError" class="field-error">{{ batchReceivedError }}</p>
          </div>
        </div>
        
        <template v-slot:footer>
          <button class="submit-btn" @click="submitBatchForm">
            {{ isEditingBatch ? 'Update Batch' : 'Add Batch' }}
          </button>
        </template>
      </BaseModal>

      <!-- Delete Batch Modal -->
      <DeleteModal
        :isOpen="showDeleteBatchModal"
        @close="cancelDeleteBatch"
        @confirm="deleteBatchConfirmed"
        message="Are you sure you want to delete this batch?"
      />
    </div>
  </template>
  
  <script>
  import BaseModal from '@/components/BaseModal.vue';
  import DeleteModal from '@/components/DeleteModal.vue';
  import SalesModal from '@/components/SalesModal.vue';
  import SuccessToast from "@/components/SuccessToast.vue";
  import ErrorToast from "@/components/ErrorToast.vue";
  import api from "@/services/api";
  import vSelect from "vue-select";
  import "vue-select/dist/vue-select.css";
  
  export default {
    name: 'ProductPage',
    components: {
      BaseModal,
      DeleteModal,
      SalesModal,
      SuccessToast,
      ErrorToast,
      vSelect
    },
    data() {
      return {
        currentPage: 1,
        pageSize: 5,
        pageInput: 1,
        searchQuery: '',
        selectedCategory: '',
        isModalOpen: false,
        isBatchModalOpen: false,
        isSellModalOpen: false,
        isEditing: false,
        isEditingBatch: false,
        isSalesModalOpen: false,
        salesProduct: null,
        expandedProductId: null,
        currentProductId: null,
        currentBatchId: null,
        showDeleteModal: false,
        productIdToDelete: null,
        showDeleteBatchModal: false,
        batchToDelete: { product_id: null, batch_id: null },
        productsError: "",
        nameError: "",
        categoryError: "",
        codeError: "",
        costError: "",
        retailPriceError: "",
        thresholdError: "",
        batchQuantityError: "",
        batchExpiryError: "",
        batchReceivedError: "",
        products: [],
        formData: {
          name: '',
          category: '',
          code: '',
          cost: '',
          retail_price: '',
          stock_threshold: '',
          quantity: ''
        },
        batchFormData: {
          batch_id: '',
          quantity: '',
          expiry_date: '',
          received_date: ''
        },
        sellFormData: {
          quantity: 1,
          maxQuantity: 0,
          price: '',
          sell_date: '',
          product_id: null,
          batch_id: null
        },
        categoryOptions: [
          "Vegetables", "Fruits", "Herbs & Spices", "Poultry", "Beef & Lamb", "Fish & Seafood", "Frozen Meat",
          "Milk", "Cheese", "Eggs", "Yogurt", "Bread", "Cakes & Pastries", "Buns & Rolls", "Canned Food",
          "Instant Noodles", "Rice & Grains", "Cooking Oil", "Flour & Baking Supplies", "Sugar & Salt",
          "Pasta & Spaghetti", "Soy Sauce", "Chili Sauce", "Curry Paste", "Seasoning Powders", "Bottled Water",
          "Soft Drinks", "Coffee & Tea", "Juice", "Instant Beverages", "Biscuits & Cookies", "Chocolates & Candy",
          "Chips & Crackers", "Traditional Snacks", "Detergents", "Cleaning Supplies", "Tissues & Towels",
          "Trash Bags", "Soap & Body Wash", "Shampoo & Hair Care", "Toothpaste", "Sanitary Products", "Diapers",
          "Baby Food", "Baby Wipes", "Pet Food", "Pet Grooming", "Others"
        ],
        showSuccessToast: false,
        showErrorToast: false,
        toastMessage: ""
      };
    },
    mounted() {
        this.fetchProducts();
    },
    watch: {
      currentPage(val) {
        this.pageInput = val;
      },
      searchQuery() {
        this.currentPage = 1;
      },
      selectedCategory() {
        this.currentPage = 1;
      }
    },
    computed: {
      paginatedProducts() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        return this.filteredProducts.slice(start, end);
      },
      totalPages() {
        return Math.ceil(this.filteredProducts.length / this.pageSize) || 1;
      },
      filteredProducts() {
        let filtered = this.products;
        if (this.selectedCategory) {
          filtered = filtered.filter(product => product.category === this.selectedCategory);
        }
        if (this.searchQuery) {
          const query = this.searchQuery.toLowerCase();
          filtered = filtered.filter(product => {
            return (
              (product.name && product.name.toLowerCase().includes(query)) ||
              (product.code && product.code.toLowerCase().includes(query)) ||
              (product.category && product.category.toLowerCase().includes(query))
            );
          });
        }
        return filtered;
      },
      modalTitle() {
        return this.isEditing ? 'Edit Product' : 'Add Product';
      },
      batchModalTitle() {
        return this.isEditingBatch ? 'Edit Batch' : 'Add Batch';
      }
    },
    methods: {
      goToPage() {
        if (this.pageInput < 1) this.pageInput = 1;
        if (this.pageInput > this.totalPages) this.pageInput = this.totalPages;
        this.currentPage = this.pageInput;
      },
      showToast(msg, type = "success") {
        this.toastMessage = msg;
        this.showSuccessToast = type === "success";
        this.showErrorToast = type === "error";
        setTimeout(() => {
          this.showSuccessToast = false;
          this.showErrorToast = false;
          this.toastMessage = "";
        }, 2500);
      },
      addCategory(newCategory) {
        if (!this.categoryOptions.includes(newCategory)) {
          this.categoryOptions.push(newCategory);
        }
        this.formData.category = newCategory;
      },
      formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString();
      },
      toggleExpand(product_id) {
        if (this.expandedProductId === product_id) {
          this.expandedProductId = null;
        } else {
          this.expandedProductId = product_id;
        }
      },
      resetForm() {
        this.formData = {
          name: '',
          category: '',
          code: '',
          cost: '',
          retail_price: '',
          stock_threshold: '',
          quantity: ''
        };
        this.currentProductId = null;
        this.isEditing = false;
        this.clearAllFieldErrors();
      },
      clearFieldError(field) {
        if (field === "name") this.nameError = "";
        if (field === "category") this.categoryError = "";
        if (field === "code") this.codeError = "";
        if (field === "cost") this.costError = "";
        if (field === "retail_price") this.retailPriceError = "";
        if (field === "stock_threshold") this.thresholdError = "";
      },
      clearAllFieldErrors() {
        this.nameError = "";
        this.categoryError = "";
        this.codeError = "";
        this.costError = "";
        this.retailPriceError = "";
        this.thresholdError = "";
      },
      clearBatchFieldError(field) {
        if (field === "quantity") this.batchQuantityError = "";
        if (field === "expiry_date") this.batchExpiryError = "";
        if (field === "received_date") this.batchReceivedError = "";
      },
      clearAllBatchFieldErrors() {
        this.batchQuantityError = "";
        this.batchExpiryError = "";
        this.batchReceivedError = "";
      },
      resetBatchForm() {
        this.batchFormData = {
          batch_id: '',
          quantity: '',
          expiry_date: '',
          received_date: ''
        };
        this.currentBatchId = null;
        this.isEditingBatch = false;
      },
      resetSellForm() {
        const today = new Date();

        this.sellFormData = {
          quantity: 1,
          maxQuantity: 0,
          price: '',
          sell_date: today.toLocaleDateString('en-CA'),
          product_id: null,
          batch_id: null
        };
      },
      openAddModal() {
        this.resetForm();
        this.isModalOpen = true;
      },
      openEditModal(product) {
        this.isEditing = true;
        this.currentProductId = product.id;
        this.formData = { ...product };
        this.isModalOpen = true;
        this.clearAllFieldErrors();
      },
      closeModal() {
        this.isModalOpen = false;
        setTimeout(this.resetForm, 300);
      },
      openAddBatchModal(product_id) {
        this.resetBatchForm();
        this.currentProductId = product_id;
        
        const product = this.products.find(p => p.id === product_id);
        const batchCount = product.batches ? product.batches.length : 0;
        this.batchFormData.batch_id = `B${String(product_id).padStart(2, '0')}${String(batchCount + 1).padStart(2, '0')}`;
        
        const today = new Date();

        this.batchFormData.received_date = today.toLocaleDateString('en-CA');
        
        const expiry_date = new Date();
        expiry_date.setMonth(expiry_date.getMonth() + 6);
        this.batchFormData.expiry_date = expiry_date.toLocaleDateString('en-CA');
        
        this.isBatchModalOpen = true;
      },
      openBatchEditModal(product_id, batch) {
        this.isEditingBatch = true;
        this.currentProductId = product_id;
        this.currentBatchId = batch.batch_id;
        this.batchFormData = { ...batch };
        this.isBatchModalOpen = true;
      },
      closeBatchModal() {
        this.isBatchModalOpen = false;
        setTimeout(this.resetBatchForm, 300);
      },
      openSellProductModal(product) {
        this.resetSellForm();
        this.salesProduct = product;
        this.isSalesModalOpen = true;
      },
      closeSalesModal() {
        this.isSalesModalOpen = false;
        this.salesProduct = null;
        this.fetchProducts(); 
      },
      closeSellModal() {
        this.isSellModalOpen = false;
        setTimeout(this.resetSellForm, 300);
      },
      async fetchProducts() {
        this.productsError = "";
        try {
          const response = await api.get('/api/products');
          this.products = response.data;
          this.products.forEach(product => {
            this.updateProductQuantity(product.id);
          });
        } catch (error) {
          this.products = [];
          this.productsError = "Failed to fetch products.";
        }
      },
      validateForm() {
        let valid = true;
        this.clearAllFieldErrors();

        if (!this.formData.name) {
          this.nameError = "Product name is required.";
          valid = false;
        } else if (
          this.products.some(
            p =>
              p.name.trim().toLowerCase() === this.formData.name.trim().toLowerCase() &&
              (!this.isEditing || p.id !== this.currentProductId)
          )
        ) {
          this.nameError = "Product name must be unique.";
          valid = false;
        }

        if (!this.formData.category) {
          this.categoryError = "Category is required.";
          valid = false;
        }

        if (!this.formData.code) {
          this.codeError = "Product code is required.";
          valid = false;
        } else if (
          this.products.some(
            p =>
              p.code.trim().toLowerCase() === this.formData.code.trim().toLowerCase() &&
              (!this.isEditing || p.id !== this.currentProductId)
          )
        ) {
          this.codeError = "Product code must be unique.";
          valid = false;
        }

        if (!this.formData.cost && this.formData.cost !== 0) {
          this.costError = "Cost is required.";
          valid = false;
        } else if (isNaN(this.formData.cost) || Number(this.formData.cost) < 0) {
          this.costError = "Cost must be a non-negative number.";
          valid = false;
        }

        if (!this.formData.retail_price && this.formData.retail_price !== 0) {
          this.retailPriceError = "Retail price is required.";
          valid = false;
        } else if (isNaN(this.formData.retail_price) || Number(this.formData.retail_price) < 0) {
          this.retailPriceError = "Retail price must be a non-negative number.";
          valid = false;
        }

        if (!this.formData.stock_threshold && this.formData.stock_threshold !== 0) {
          this.thresholdError = "Stock threshold is required.";
          valid = false;
        } else if (isNaN(this.formData.stock_threshold) || Number(this.formData.stock_threshold) < 0) {
          this.thresholdError = "Stock threshold must be a non-negative number.";
          valid = false;
        }

        return valid;
      },
      async submitForm() {
        if (!this.validateForm()) return;
        try {
          if (this.isEditing) {
            await api.put(`/api/products/${this.currentProductId}`, this.formData);
            this.showToast("Product updated successfully!", "success");
          } else {
            await api.post('/api/products', this.formData);
            this.showToast("Product added successfully!", "success");
          }
          this.closeModal();
          this.fetchProducts();
        } catch (error) {
          this.showToast("Failed to save product.", "error");
        }
      },
      validateBatchForm() {
        let valid = true;
        this.clearAllBatchFieldErrors();
        if (!this.batchFormData.quantity || isNaN(this.batchFormData.quantity) || Number(this.batchFormData.quantity) < 1) {
          this.batchQuantityError = "Quantity must be at least 1.";
          valid = false;
        }
        if (!this.batchFormData.expiry_date) {
          this.batchExpiryError = "Expiry date is required.";
          valid = false;
        }
        if (!this.batchFormData.received_date) {
          this.batchReceivedError = "Received date is required.";
          valid = false;
        }
        return valid;
      }, 
      async submitBatchForm() {
        if (!this.validateBatchForm()) return;
        try {
          const payload = {
            product_id: this.currentProductId,
            quantity: Number(this.batchFormData.quantity),
            expiry_date: this.batchFormData.expiry_date,
            received_date: this.batchFormData.received_date
          };

          if (this.isEditingBatch) {
            await api.put(`/api/products/${this.currentProductId}/batches/${this.currentBatchId}`, payload);
            this.showToast("Batch updated successfully!", "success"); // <-- Add this
          } else {
            await api.post(`/api/products/${this.currentProductId}/batches`, payload);
            this.showToast("Batch added successfully!", "success"); // <-- Add this
          }
          this.closeBatchModal();
          this.fetchProducts();
        } catch (error) {
          this.showToast("Failed to save batch.", "error"); // <-- Add this
        }
      },
      confirmDeleteProduct(productId) {
        this.productIdToDelete = productId;
        this.showDeleteModal = true;
      },
      async deleteProductConfirmed() {
        try {
          await api.delete(`/api/products/${this.productIdToDelete}`);
          this.fetchProducts();
          this.showToast("Product deleted.", "success");
        } catch (error) {
          this.showToast("Failed to delete product.", "error");
        } finally {
          this.showDeleteModal = false;
          this.productIdToDelete = null;
        }
      },
      cancelDeleteProduct() {
        this.showDeleteModal = false;
        this.productIdToDelete = null;
      },
      confirmDeleteBatch(product_id, batch_id) {
        this.batchToDelete = { product_id, batch_id };
        this.showDeleteBatchModal = true;
      },
      async deleteBatchConfirmed() {
        try {
          await api.delete(`/api/products/${this.batchToDelete.product_id}/batches/${this.batchToDelete.batch_id}`);
          this.fetchProducts();
          this.showToast("Batch deleted.", "success");
        } catch (error) {
          this.showToast("Failed to delete batch.", "error");
        } finally {
          this.showDeleteBatchModal = false;
          this.batchToDelete = { product_id: null, batch_id: null };
        }
      },
      cancelDeleteBatch() {
        this.showDeleteBatchModal = false;
        this.batchToDelete = { product_id: null, batch_id: null };
      },
      updateProductQuantity(product_id) {
        const productIndex = this.products.findIndex(p => p.id === product_id);
        if (productIndex === -1) return;
        const product = this.products[productIndex];
        if (!product.batches) {
          this.products[productIndex].quantity = 0;
          return;
        }
        const totalQuantity = product.batches.reduce((sum, batch) => {
          return sum + (Number(batch.quantity) || 0);
        }, 0);
        this.products[productIndex].quantity = totalQuantity;
      },
    },
  };
  </script>
  
  <style scoped>
  .product-container {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    color: #4a5568;
    margin-top: 0;
    margin-bottom: 24px;
    font-weight: 500;
    font-size: 24px;
  }
  
  .product-actions {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
  }
  
  .search-bar {
    position: relative;
    flex: 1;
    max-width: 500px;
  }
  
  .search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23718096'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .search-bar input {
    width: 100%;
    padding: 10px 10px 10px 40px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .filter-dropdown {
    margin-left: 15px;
  }
  
  .filter-btn {
    display: flex;
    align-items: center;
    padding: 8px 16px;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
  }
  
  .chevron-down {
    width: 16px;
    height: 16px;
    margin-left: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23718096'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .expand-cell .chevron-down {
    margin-left: 0px;
  }
  
  .chevron-up {
    width: 16px;
    height: 16px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23718096'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 15l7-7 7 7' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .product-table {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 20px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid #edf2f7;
  }
  
  th {
    background-color: #f8fafc;
    color: #4a5568;
    font-weight: 500;
    font-size: 14px;
  }
  
  td {
    color: #2d3748;
    font-size: 14px;
  }
  
  .action-cell {
    width: 100px;
    text-align: center;
  }
  
  .expand-cell {
    width: 50px;
    text-align: center;
  }
  
  .action-buttons {
    display: flex;
    justify-content: center;
    gap: 8px;
  }
  
  .edit-btn, .expand-btn, .delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background-color: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .edit-btn:hover, .expand-btn:hover {
    background-color: #edf2f7;
  }
  
  .delete-btn:hover {
    background-color: #fed7d7;
  }
  
  .edit-icon {
    width: 16px;
    height: 16px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%234a5568'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .delete-icon {
    width: 16px;
    height: 16px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23e53e3e'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .sell-icon {
    width: 16px;
    height: 16px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%234a5568'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .chevron-icon {
    width: 16px;
    height: 16px;
  }
  
  .add-product-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px 16px;
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    float: right;
    transition: background-color 0.2s;
  }
  
  .add-product-btn:hover {
    background-color: #0052a3;
  }
  
  .plus-icon {
    width: 16px;
    height: 16px;
    margin-right: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='white'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 6v6m0 0v6m0-6h6m-6 0H6' /%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .product-form {
    width: 100%;
  }
  
  .form-group {
    margin-bottom: 16px;
  }
  
  .form-group label {
    display: block;
    font-size: 14px;
    color: #4a5568;
    margin-bottom: 6px;
  }
  
  .form-control {
    width: 100%;
    padding: 10px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .form-text {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    color: #718096;
  }
  
  .submit-btn {
    padding: 10px 24px;
    background-color: #0066cc;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .submit-btn:hover {
    background-color: #0052a3;
  }
  
  /* Expanded row styles */
  tr.expanded {
    background-color: #ebf4ff;
  }

  tr.batch-header td {
  padding: 0;
  border-bottom: none;
}

.batch-container {
  padding: 0 16px 16px 16px;
  background-color: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.batch-header-row {
  display: flex;
  background-color: #edf2f7;
  border-radius: 4px 4px 0 0;
  padding: 10px 16px;
  font-weight: 500;
  font-size: 13px;
  color: #4a5568;
}

.batch-row {
  display: flex;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.batch-row:last-child {
  border-bottom: none;
}

.batch-column {
  flex: 1;
}

.batch-id {
  flex: 0.5;
}

.batch-quantity {
  flex: 0.5;
}

.batch-expiry {
  flex: 1;
}

.batch-received {
  flex: 1;
}

.batch-actions {
  flex: 1;
  display: flex;
  justify-content: flex-start;
  gap: 8px;
}

.batch-edit-btn, .batch-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background-color: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  cursor: pointer;
}

.batch-edit-btn:hover {
  background-color: #edf2f7;
}

.batch-delete-btn:hover {
  background-color: #fed7d7;
}

.add-batch-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.add-batch-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

.add-batch-btn:hover {
  background-color: #3182ce;
}

.no-batches {
  padding: 16px;
  text-align: center;
  color: #718096;
  font-style: italic;
}

.sell-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: #38a169;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.sell-btn:hover {
  background-color: #2f855a;
}
.filter-select {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  min-width: 180px;
}
.error-message {
  color: #e53e3e;
  font-size: 15px;
  padding: 12px 16px;
}
.field-error {
  color: #e53e3e;
  font-size: 13px;
  margin: 0 0 8px 0;
  text-align: left;
  width: 100%;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
}
.pagination button {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 4px;
  cursor: pointer;
}
.pagination button:disabled {
  background: #e2e8f0;
  cursor: not-allowed;
}
</style>

<!--Global style for v-select (ProductPage and ProductCatalogPage)-->
<style>
.category-vselect {
  width: 100%;
  font-size: 14px;
}
.v-select {
  width: 100%;
}
.vs__dropdown-toggle, .vs__selected {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  color: #2d3748;
}
.vs__dropdown-menu {
  border-radius: 4px;
}
.vs__placeholder {
  color: #718096;
  font-size: 14px;
  display: flex;
  align-items: center;
  height: 38px;
}
.vs__dropdown-option--highlight {
  background: #e2e8f0;
  color: #2d3748;
}
.vs__dropdown-option--selected {
  background: #0066cc;
  color: #fff;
}
</style>
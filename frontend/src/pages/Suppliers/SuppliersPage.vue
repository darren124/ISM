<template>
    <div class="suppliers-container">
      <h1>Suppliers</h1>
      
      <div class="suppliers-actions">
        <div class="search-bar">
          <i class="search-icon"></i>
          <input 
            type="text" 
            placeholder="Search supplier ID" 
            v-model="searchQuery"
          />
        </div>
        
        <div class="filter-dropdown">
          <button class="filter-btn">
            Filter
            <i class="chevron-down"></i>
          </button>
        </div>
      </div>
      
      <div class="suppliers-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Company</th>
              <th>Address</th>
              <th>Phone no.</th>
              <th>Email</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="supplier in filteredSuppliers" :key="supplier.id">
              <td>{{ supplier.id }}</td>
              <td>{{ supplier.name }}</td>
              <td>{{ supplier.company }}</td>
              <td>{{ supplier.address }}</td>
              <td>{{ supplier.phone }}</td>
              <td>{{ supplier.email }}</td>
              <td>{{ supplier.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <button class="add-supplier-btn" @click="addSupplier">
        <i class="plus-icon"></i>
        Add Supplier
      </button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SuppliersPage',
    data() {
      return {
        searchQuery: '',
        suppliers: [
          {
            id: 1,
            name: 'Chong',
            company: 'Chong\'s Trading',
            address: 'Kemaman, Terengganu',
            phone: '01234567890',
            email: 'chong@gmail.com',
            status: 'Active'
          },
          {
            id: 2,
            name: 'Ali',
            company: 'Ali Enterprise Sdn. Bhd.',
            address: 'Pekan, Kuantan',
            phone: '01234567890',
            email: 'ali@gmail.com',
            status: 'Active'
          },
          {
            id: 3,
            name: 'Siti',
            company: 'ST Grocery',
            address: 'Alor Setar, Kedah',
            phone: '01234567890',
            email: 'siti@gmail.com',
            status: 'Active'
          },
          {
            id: 4,
            name: 'Kumar',
            company: 'KM Wholesale',
            address: 'Johor Bahru, Johor',
            phone: '01234567890',
            email: 'kumar@gmail.com',
            status: 'Active'
          }
        ]
      };
    },
    computed: {
      filteredSuppliers() {
        if (!this.searchQuery) {
          return this.suppliers;
        }
        
        const query = this.searchQuery.toLowerCase();
        return this.suppliers.filter(supplier => {
          return supplier.id.toString().includes(query) ||
                 supplier.name.toLowerCase().includes(query) ||
                 supplier.company.toLowerCase().includes(query) ||
                 supplier.address.toLowerCase().includes(query) ||
                 supplier.phone.includes(query) ||
                 supplier.email.toLowerCase().includes(query) ||
                 supplier.status.toLowerCase().includes(query);
        });
      }
    },
    methods: {
      addSupplier() {
        console.log('Add supplier clicked');
        // Implement your add supplier logic here
        // This could open a modal or navigate to a supplier form
      }
    }
  };
  </script>
  
  <style scoped>
  .suppliers-container {
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
  
  .suppliers-actions {
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
  
  .suppliers-table {
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
  
  .add-supplier-btn {
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
    margin-left: auto;
    transition: background-color 0.2s;
  }
  
  .add-supplier-btn:hover {
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
  </style>
// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let currentUser = null;
let authToken = null;
let allItems = [];
let allCategories = [];
let allTransactions = [];

// ==================== Auth Functions ====================

function toggleAuthForms() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    loginForm.style.display = loginForm.style.display === 'none' ? 'block' : 'none';
    registerForm.style.display = registerForm.style.display === 'none' ? 'block' : 'none';
}

function showAuthAlert(message, type = 'error') {
    const alertDiv = document.getElementById('authAlert');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.display = 'block';
}

async function handleLogin() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        showAuthAlert('Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showAuthAlert(data.error);
            return;
        }

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));

        showApp();
    } catch (error) {
        showAuthAlert('Login failed: ' + error.message);
    }
}

async function handleRegister() {
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;

    if (!username || !email || !password) {
        showAuthAlert('Please fill in all fields');
        return;
    }

    if (password.length < 6) {
        showAuthAlert('Password must be at least 6 characters');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            showAuthAlert(data.error);
            return;
        }

        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));

        showAuthAlert('Registration successful!', 'success');
        setTimeout(() => showApp(), 1000);
    } catch (error) {
        showAuthAlert('Registration failed: ' + error.message);
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    showAuthPage();
}

// ==================== Page Navigation ====================

function showAuthPage() {
    document.getElementById('authPage').classList.add('active');
    document.getElementById('appPage').classList.remove('active');
}

function showApp() {
    document.getElementById('authPage').classList.remove('active');
    document.getElementById('appPage').classList.add('active');
    document.getElementById('userDisplay').textContent = `👤 ${currentUser.username}`;
    loadDashboard();
    loadCategories();
    loadInventory();
}

function switchPage(page) {
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update page title
    const titles = {
        dashboard: '📊 Dashboard',
        inventory: '📦 Inventory Items',
        categories: '🏷️ Categories',
        transactions: '📝 Transactions'
    };
    document.getElementById('pageTitle').textContent = titles[page];

    // Hide all content
    document.querySelectorAll('.page-content').forEach(content => {
        content.style.display = 'none';
    });

    // Show selected content
    document.getElementById(page + 'Content').style.display = 'block';

    // Load data if needed
    if (page === 'dashboard') {
        loadDashboard();
    } else if (page === 'inventory') {
        loadInventory();
    } else if (page === 'categories') {
        loadCategories();
    } else if (page === 'transactions') {
        loadTransactions();
    }
}

// ==================== API Functions ====================

async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: { ...headers, ...options.headers }
    });

    if (response.status === 401) {
        handleLogout();
        return null;
    }

    return response;
}

// ==================== Dashboard Functions ====================

async function loadDashboard() {
    try {
        const response = await apiCall('/dashboard/stats');
        const stats = await response.json();

        const statsGrid = document.getElementById('statsGrid');
        statsGrid.innerHTML = `
            <div class="stat-card">
                <h3>Total Items</h3>
                <div class="stat-value">${stats.total_items}</div>
            </div>
            <div class="stat-card">
                <h3>Inventory Value</h3>
                <div class="stat-value">$${stats.total_value.toFixed(2)}</div>
            </div>
            <div class="stat-card">
                <h3>Low Stock</h3>
                <div class="stat-value" style="color: var(--warning);">${stats.low_stock_count}</div>
            </div>
        `;

        // Load low stock items
        const lowStockTable = document.getElementById('lowStockTable');
        lowStockTable.innerHTML = '';

        if (stats.low_stock_items.length === 0) {
            lowStockTable.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text);">All items are well stocked</td></tr>';
        } else {
            stats.low_stock_items.forEach(item => {
                lowStockTable.innerHTML += `
                    <tr>
                        <td>${item.name}</td>
                        <td>${item.sku}</td>
                        <td><strong>${item.quantity}</strong></td>
                        <td>${item.reorder_level}</td>
                        <td>$${item.unit_price.toFixed(2)}</td>
                    </tr>
                `;
            });
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ==================== Inventory Functions ====================

async function loadInventory() {
    try {
        const response = await apiCall('/inventory');
        allItems = await response.json();
        displayInventory(allItems);
    } catch (error) {
        console.error('Error loading inventory:', error);
    }
}

function displayInventory(items) {
    const table = document.getElementById('inventoryTable');
    table.innerHTML = '';

    if (items.length === 0) {
        table.innerHTML = '<tr><td colspan="8" style="text-align: center; color: var(--text);">No items found</td></tr>';
        return;
    }

    items.forEach(item => {
        const statusBadge = item.needs_reorder 
            ? '<span class="badge badge-warning">Low Stock</span>'
            : '<span class="badge badge-success">In Stock</span>';

        table.innerHTML += `
            <tr>
                <td>${item.name}</td>
                <td>${item.sku}</td>
                <td>${item.category_name || 'N/A'}</td>
                <td>${item.quantity}</td>
                <td>$${item.unit_price.toFixed(2)}</td>
                <td>$${item.total_value.toFixed(2)}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-secondary" onclick="openStockAction(${item.id}, '${item.name}', 'add')">+</button>
                        <button class="btn btn-small btn-secondary" onclick="openStockAction(${item.id}, '${item.name}', 'remove')">-</button>
                        <button class="btn btn-small btn-danger" onclick="deleteItem(${item.id})">🗑️</button>
                    </div>
                </td>
            </tr>
        `;
    });
}

function filterInventory() {
    const search = document.getElementById('searchInput').value.toLowerCase();
    const categoryId = document.getElementById('categoryFilter').value;
    const lowStockOnly = document.getElementById('lowStockFilter').checked;

    let filtered = allItems.filter(item => {
        const matchesSearch = item.name.toLowerCase().includes(search) || item.sku.toLowerCase().includes(search);
        const matchesCategory = !categoryId || item.category_id == categoryId;
        const matchesLowStock = !lowStockOnly || item.needs_reorder;
        return matchesSearch && matchesCategory && matchesLowStock;
    });

    displayInventory(filtered);
}

async function handleAddItem() {
    const name = document.getElementById('itemName').value;
    const sku = document.getElementById('itemSKU').value;
    const categoryId = document.getElementById('itemCategory').value;
    const price = parseFloat(document.getElementById('itemPrice').value);
    const quantity = parseInt(document.getElementById('itemQuantity').value) || 0;
    const reorderLevel = parseInt(document.getElementById('itemReorderLevel').value) || 10;
    const description = document.getElementById('itemDescription').value;

    if (!name || !sku || !categoryId || isNaN(price)) {
        alert('Please fill in all required fields');
        return;
    }

    try {
        const response = await apiCall('/inventory', {
            method: 'POST',
            body: JSON.stringify({
                name, sku, category_id: parseInt(categoryId), unit_price: price,
                quantity, reorder_level: reorderLevel, description
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error);
            return;
        }

        closeModal('addItemModal');
        document.getElementById('itemName').value = '';
        document.getElementById('itemSKU').value = '';
        document.getElementById('itemPrice').value = '';
        document.getElementById('itemQuantity').value = '0';
        document.getElementById('itemReorderLevel').value = '10';
        document.getElementById('itemDescription').value = '';
        loadInventory();
    } catch (error) {
        alert('Error adding item: ' + error.message);
    }
}

async function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
        const response = await apiCall(`/inventory/${itemId}`, { method: 'DELETE' });

        if (!response.ok) {
            alert('Error deleting item');
            return;
        }

        loadInventory();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function openStockAction(itemId, itemName, action) {
    document.getElementById('stockActionTitle').textContent = action === 'add' ? 'Add Stock' : 'Remove Stock';
    document.getElementById('stockActionItem').value = itemName;
    document.getElementById('stockActionQuantity').value = '';
    document.getElementById('stockActionReason').value = '';
    document.getElementById('stockActionBtn').textContent = action === 'add' ? 'Add Stock' : 'Remove Stock';
    document.getElementById('stockActionBtn').dataset.itemId = itemId;
    document.getElementById('stockActionBtn').dataset.action = action;
    openModal('stockActionModal');
}

async function handleStockAction() {
    const btn = document.getElementById('stockActionBtn');
    const itemId = btn.dataset.itemId;
    const action = btn.dataset.action;
    const quantity = parseInt(document.getElementById('stockActionQuantity').value);
    const reason = document.getElementById('stockActionReason').value;

    if (!quantity || quantity <= 0) {
        alert('Please enter a valid quantity');
        return;
    }

    try {
        const endpoint = action === 'add' ? `/inventory/${itemId}/add` : `/inventory/${itemId}/remove`;
        const response = await apiCall(endpoint, {
            method: 'POST',
            body: JSON.stringify({ quantity, reason })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error);
            return;
        }

        closeModal('stockActionModal');
        loadInventory();
        loadDashboard();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ==================== Category Functions ====================

async function loadCategories() {
    try {
        const response = await apiCall('/categories');
        allCategories = await response.json();
        displayCategories();
        populateCategoryDropdowns();
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function displayCategories() {
    const table = document.getElementById('categoriesTable');
    table.innerHTML = '';

    if (allCategories.length === 0) {
        table.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text);">No categories found</td></tr>';
        return;
    }

    allCategories.forEach(category => {
        const date = new Date(category.created_at).toLocaleDateString();
        table.innerHTML += `
            <tr>
                <td>${category.name}</td>
                <td>${category.description || '-'}</td>
                <td>${date}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-small btn-danger" onclick="deleteCategory(${category.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    });
}

function populateCategoryDropdowns() {
    const dropdowns = ['itemCategory', 'categoryFilter'];
    dropdowns.forEach(id => {
        const select = document.getElementById(id);
        if (!select) return;
        
        const currentValue = select.value;
        select.innerHTML = id === 'categoryFilter' ? '<option value="">All Categories</option>' : '';
        
        allCategories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });

        if (currentValue) select.value = currentValue;
    });
}

async function handleAddCategory() {
    const name = document.getElementById('categoryName').value;
    const description = document.getElementById('categoryDescription').value;

    if (!name) {
        alert('Please enter a category name');
        return;
    }

    try {
        const response = await apiCall('/categories', {
            method: 'POST',
            body: JSON.stringify({ name, description })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.error);
            return;
        }

        closeModal('addCategoryModal');
        document.getElementById('categoryName').value = '';
        document.getElementById('categoryDescription').value = '';
        loadCategories();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteCategory(categoryId) {
    if (!confirm('Are you sure you want to delete this category?')) return;

    try {
        const response = await apiCall(`/categories/${categoryId}`, { method: 'DELETE' });

        if (!response.ok) {
            alert('Error deleting category');
            return;
        }

        loadCategories();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ==================== Transaction Functions ====================

async function loadTransactions() {
    try {
        const response = await apiCall('/transactions');
        allTransactions = await response.json();
        displayTransactions(allTransactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function displayTransactions(transactions) {
    const table = document.getElementById('transactionsTable');
    table.innerHTML = '';

    if (transactions.length === 0) {
        table.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text);">No transactions found</td></tr>';
        return;
    }

    transactions.forEach(transaction => {
        const date = new Date(transaction.created_at).toLocaleDateString();
        const typeBadge = transaction.transaction_type === 'add' 
            ? '<span class="badge badge-success">Add</span>'
            : '<span class="badge badge-warning">Remove</span>';

        table.innerHTML += `
            <tr>
                <td>${transaction.item_name}</td>
                <td>${typeBadge}</td>
                <td>${transaction.quantity_changed}</td>
                <td>${transaction.reason || '-'}</td>
                <td>${transaction.username}</td>
                <td>${date}</td>
            </tr>
        `;
    });
}

function filterTransactions() {
    const typeFilter = document.getElementById('transactionTypeFilter').value;

    let filtered = allTransactions;
    if (typeFilter) {
        filtered = allTransactions.filter(t => t.transaction_type === typeFilter);
    }

    displayTransactions(filtered);
}

// ==================== Modal Functions ====================

function openModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

function openAddItemModal() {
    openModal('addItemModal');
}

function openAddCategoryModal() {
    openModal('addCategoryModal');
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('show');
    }
});

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showApp();
    } else {
        showAuthPage();
    }
});

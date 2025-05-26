/**
 * School Management System - Main JavaScript File
 * Provides enhanced interactivity and user experience
 */

(function() {
    'use strict';

    // Global variables
    let currentUser = null;
    let notifications = [];

    // Initialize the application
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    /**
     * Initialize the application
     */
    function initializeApp() {
        // Initialize components
        initializeFormValidation();
        initializeDataTables();
        initializeTooltips();
        initializeAutoRefresh();
        initializeKeyboardShortcuts();
        initializeSearchFunctionality();
        initializeDatePickers();
        initializeModalManagement();
        
        // Add loading states
        addLoadingStates();
        
        // Initialize notifications
        initializeNotifications();
        
        console.log('School Management System initialized successfully');
    }

    /**
     * Initialize form validation
     */
    function initializeFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                this.classList.add('was-validated');
            });
        });

        // Real-time validation
        const inputs = document.querySelectorAll('input[required], select[required], textarea[required]');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    }

    /**
     * Validate a form
     * @param {HTMLFormElement} form 
     * @returns {boolean}
     */
    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Validate a single field
     * @param {HTMLElement} field 
     * @returns {boolean}
     */
    function validateField(field) {
        let isValid = true;
        const value = field.value.trim();
        
        // Remove previous validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        // Check if required field is empty
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            field.classList.add('is-invalid');
            showFieldError(field, 'هذا الحقل مطلوب');
        }
        
        // Email validation
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                field.classList.add('is-invalid');
                showFieldError(field, 'يرجى إدخال بريد إلكتروني صحيح');
            }
        }
        
        // Phone validation (basic)
        if (field.name === 'phone' || field.name === 'parent_phone') {
            const phoneRegex = /^[\d\s\-\+\(\)]+$/;
            if (value && !phoneRegex.test(value)) {
                isValid = false;
                field.classList.add('is-invalid');
                showFieldError(field, 'يرجى إدخال رقم هاتف صحيح');
            }
        }
        
        if (isValid && value) {
            field.classList.add('is-valid');
            hideFieldError(field);
        }
        
        return isValid;
    }

    /**
     * Show field error message
     * @param {HTMLElement} field 
     * @param {string} message 
     */
    function showFieldError(field, message) {
        let errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentElement.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    /**
     * Hide field error message
     * @param {HTMLElement} field 
     */
    function hideFieldError(field) {
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Initialize enhanced data tables
     */
    function initializeDataTables() {
        const tables = document.querySelectorAll('table.table');
        
        tables.forEach(table => {
            // Add sorting functionality
            addTableSorting(table);
            
            // Add row highlighting
            addRowHighlighting(table);
            
            // Add pagination if needed
            if (table.querySelectorAll('tbody tr').length > 25) {
                addTablePagination(table);
            }
        });
    }

    /**
     * Add sorting to table columns
     * @param {HTMLTableElement} table 
     */
    function addTableSorting(table) {
        const headers = table.querySelectorAll('th');
        
        headers.forEach((header, index) => {
            if (header.textContent.trim() && !header.classList.contains('no-sort')) {
                header.style.cursor = 'pointer';
                header.innerHTML += ' <i class="fas fa-sort text-muted ms-1"></i>';
                
                header.addEventListener('click', function() {
                    sortTable(table, index);
                });
            }
        });
    }

    /**
     * Sort table by column
     * @param {HTMLTableElement} table 
     * @param {number} columnIndex 
     */
    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const header = table.querySelectorAll('th')[columnIndex];
        
        // Determine sort direction
        const isAscending = !header.classList.contains('sort-desc');
        
        // Clear previous sort indicators
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
            const icon = th.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-sort text-muted ms-1';
            }
        });
        
        // Sort rows
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            const result = aValue.localeCompare(bValue, 'ar', { numeric: true });
            return isAscending ? result : -result;
        });
        
        // Update table
        rows.forEach(row => tbody.appendChild(row));
        
        // Update sort indicator
        header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
        const icon = header.querySelector('i');
        if (icon) {
            icon.className = `fas fa-sort-${isAscending ? 'up' : 'down'} text-primary ms-1`;
        }
    }

    /**
     * Add row highlighting
     * @param {HTMLTableElement} table 
     */
    function addRowHighlighting(table) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'var(--bs-secondary-bg)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    }

    /**
     * Initialize tooltips
     */
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            // Add tooltip if bootstrap is available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            }
        });
    }

    /**
     * Initialize auto-refresh for dashboard
     */
    function initializeAutoRefresh() {
        if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
            // Refresh dashboard every 5 minutes
            setInterval(() => {
                refreshDashboardData();
            }, 300000);
        }
    }

    /**
     * Refresh dashboard data without full page reload
     */
    function refreshDashboardData() {
        const statsCards = document.querySelectorAll('.stats-card');
        
        // Add loading animation
        statsCards.forEach(card => {
            card.classList.add('loading');
        });
        
        // Simulate data refresh (in real implementation, this would be an AJAX call)
        setTimeout(() => {
            statsCards.forEach(card => {
                card.classList.remove('loading');
            });
            
            // Show notification
            showNotification('تم تحديث البيانات', 'success');
        }, 2000);
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Alt + shortcuts
            if ((e.ctrlKey || e.metaKey) && e.altKey) {
                switch(e.key) {
                    case 'd':
                        e.preventDefault();
                        window.location.href = '/dashboard';
                        break;
                    case 'a':
                        e.preventDefault();
                        window.location.href = '/attendance';
                        break;
                    case 's':
                        e.preventDefault();
                        window.location.href = '/students';
                        break;
                    case 'b':
                        e.preventDefault();
                        window.location.href = '/behavior';
                        break;
                    case 'r':
                        e.preventDefault();
                        window.location.href = '/statistics';
                        break;
                }
            }
            
            // Escape key to close modals
            if (e.key === 'Escape') {
                const openModals = document.querySelectorAll('.modal.show');
                openModals.forEach(modal => {
                    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                    }
                });
            }
        });
    }

    /**
     * Initialize search functionality
     */
    function initializeSearchFunctionality() {
        const searchInputs = document.querySelectorAll('input[type="search"], input[name*="search"]');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    performSearch(this);
                }, 300);
            });
        });
    }

    /**
     * Perform search in tables
     * @param {HTMLInputElement} searchInput 
     */
    function performSearch(searchInput) {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const targetTable = document.querySelector(searchInput.getAttribute('data-target') || 'table');
        
        if (!targetTable) return;
        
        const rows = targetTable.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            const isVisible = !searchTerm || rowText.includes(searchTerm);
            
            row.style.display = isVisible ? '' : 'none';
            if (isVisible) visibleCount++;
        });
        
        // Update result count if element exists
        const resultCount = document.querySelector('.search-result-count');
        if (resultCount) {
            resultCount.textContent = `عرض ${visibleCount} من ${rows.length} نتيجة`;
        }
    }

    /**
     * Initialize date pickers
     */
    function initializeDatePickers() {
        const dateInputs = document.querySelectorAll('input[type="date"]');
        
        dateInputs.forEach(input => {
            // Set max date to today for past dates
            if (input.name.includes('birth') || input.name.includes('enrollment')) {
                input.max = new Date().toISOString().split('T')[0];
            }
            
            // Add calendar icon
            const wrapper = document.createElement('div');
            wrapper.className = 'input-group';
            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(input);
            
            const icon = document.createElement('span');
            icon.className = 'input-group-text';
            icon.innerHTML = '<i class="fas fa-calendar-alt"></i>';
            wrapper.appendChild(icon);
        });
    }

    /**
     * Initialize modal management
     */
    function initializeModalManagement() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', function() {
                // Focus first input in modal
                const firstInput = this.querySelector('input:not([type="hidden"]), select, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            });
            
            modal.addEventListener('hidden.bs.modal', function() {
                // Clear form validation states
                const form = this.querySelector('form');
                if (form) {
                    form.classList.remove('was-validated');
                    form.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
                        field.classList.remove('is-valid', 'is-invalid');
                    });
                    form.querySelectorAll('.invalid-feedback').forEach(feedback => {
                        feedback.remove();
                    });
                }
            });
        });
    }

    /**
     * Add loading states to buttons and forms
     */
    function addLoadingStates() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                const submitButton = this.querySelector('button[type="submit"]');
                if (submitButton) {
                    addLoadingToButton(submitButton);
                }
            });
        });
    }

    /**
     * Add loading spinner to button
     * @param {HTMLButtonElement} button 
     */
    function addLoadingToButton(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>جاري المعالجة...';
        button.disabled = true;
        
        // Reset button after form submission or timeout
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
        }, 3000);
    }

    /**
     * Initialize notifications system
     */
    function initializeNotifications() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            const container = document.createElement('div');
            container.className = 'notification-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
    }

    /**
     * Show notification
     * @param {string} message 
     * @param {string} type 
     * @param {number} duration 
     */
    function showNotification(message, type = 'info', duration = 5000) {
        const container = document.querySelector('.notification-container');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show shadow`;
        notification.style.minWidth = '300px';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    /**
     * Utility function to format dates in Arabic
     * @param {Date} date 
     * @returns {string}
     */
    function formatDateArabic(date) {
        return date.toLocaleDateString('ar-SA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * Utility function to format numbers in Arabic
     * @param {number} number 
     * @returns {string}
     */
    function formatNumberArabic(number) {
        return number.toLocaleString('ar-SA');
    }

    /**
     * Export functions for global use
     */
    window.SchoolManagement = {
        showNotification,
        validateForm,
        formatDateArabic,
        formatNumberArabic,
        addLoadingToButton
    };

    // Add keyboard shortcut hints
    if (document.querySelector('.navbar')) {
        const helpButton = document.createElement('button');
        helpButton.className = 'btn btn-outline-secondary btn-sm position-fixed bottom-0 end-0 m-3';
        helpButton.innerHTML = '<i class="fas fa-keyboard"></i>';
        helpButton.title = 'اختصارات لوحة المفاتيح';
        helpButton.onclick = showKeyboardShortcuts;
        document.body.appendChild(helpButton);
    }

    /**
     * Show keyboard shortcuts modal
     */
    function showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl+Alt+D', action: 'الذهاب إلى لوحة التحكم' },
            { key: 'Ctrl+Alt+A', action: 'الذهاب إلى الحضور والغياب' },
            { key: 'Ctrl+Alt+S', action: 'الذهاب إلى الطلاب' },
            { key: 'Ctrl+Alt+B', action: 'الذهاب إلى التقارير السلوكية' },
            { key: 'Ctrl+Alt+R', action: 'الذهاب إلى الإحصائيات' },
            { key: 'Escape', action: 'إغلاق النوافذ المنبثقة' }
        ];

        let shortcutsHtml = '<div class="table-responsive"><table class="table table-sm">';
        shortcutsHtml += '<thead><tr><th>الاختصار</th><th>الإجراء</th></tr></thead><tbody>';
        
        shortcuts.forEach(shortcut => {
            shortcutsHtml += `<tr><td><kbd>${shortcut.key}</kbd></td><td>${shortcut.action}</td></tr>`;
        });
        
        shortcutsHtml += '</tbody></table></div>';

        showNotification(`
            <strong>اختصارات لوحة المفاتيح:</strong><br>
            ${shortcutsHtml}
        `, 'info', 10000);
    }

})();

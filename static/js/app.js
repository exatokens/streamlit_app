// Custom JavaScript for GitHub Migration App

// Utility function to load custom CSS
function loadCustomCSS() {
    const cssFile = '/static/css/styles.css';
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = cssFile;
    document.head.appendChild(link);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    loadCustomCSS();
});

// Table interaction utilities
const TableUtils = {
    // Highlight selected rows
    highlightSelectedRows: function() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const row = this.closest('tr');
                if (this.checked) {
                    row.classList.add('selected-row');
                } else {
                    row.classList.remove('selected-row');
                }
            });
        });
    },

    // Add keyboard shortcuts
    initKeyboardShortcuts: function() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const saveButton = document.querySelector('button:contains("Save Changes")');
                if (saveButton) {
                    saveButton.click();
                }
            }

            // Ctrl/Cmd + R to refresh
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                const refreshButton = document.querySelector('button:contains("Refresh")');
                if (refreshButton) {
                    refreshButton.click();
                }
            }

            // Escape to cancel
            if (e.key === 'Escape') {
                const cancelButton = document.querySelector('button:contains("Cancel")');
                if (cancelButton) {
                    cancelButton.click();
                }
            }
        });
    },

    // Auto-resize table columns
    autoResizeColumns: function() {
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            const headers = table.querySelectorAll('th');
            headers.forEach(header => {
                header.style.minWidth = '100px';
            });
        });
    },

    // Smooth scroll to changed rows section
    scrollToChangedRows: function() {
        const changedRowsSection = document.querySelector('h3:contains("Changed Rows")');
        if (changedRowsSection) {
            changedRowsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
};

// Filter utilities
const FilterUtils = {
    // Debounce filter input
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Clear all filters
    clearAllFilters: function() {
        const filterInputs = document.querySelectorAll('input[placeholder]');
        filterInputs.forEach(input => {
            if (!input.disabled) {
                input.value = '';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        });
    }
};

// Loading state utilities
const LoadingUtils = {
    // Show loading spinner overlay
    showLoadingOverlay: function(message) {
        const overlay = document.createElement('div');
        overlay.id = 'custom-loading-overlay';
        overlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    },

    // Hide loading overlay
    hideLoadingOverlay: function() {
        const overlay = document.getElementById('custom-loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// Export utilities for use in Streamlit components
window.TableUtils = TableUtils;
window.FilterUtils = FilterUtils;
window.LoadingUtils = LoadingUtils;

// Initialize utilities when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        TableUtils.highlightSelectedRows();
        TableUtils.initKeyboardShortcuts();
        TableUtils.autoResizeColumns();
    });
} else {
    TableUtils.highlightSelectedRows();
    TableUtils.initKeyboardShortcuts();
    TableUtils.autoResizeColumns();
}
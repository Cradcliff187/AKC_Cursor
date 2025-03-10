/**
 * AKC LLC Construction CRM
 * Main JavaScript file
 */

// Format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

// Format percentage values
function formatPercent(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// Format date values
function formatDate(dateString) {
    if (!dateString) return 'Not set';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(date);
}

// Refresh dashboard data
function refreshDashboardData() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            // Update the dashboard with new data
            console.log('Dashboard data refreshed:', data);
            // Logic to update UI elements would go here
        })
        .catch(error => {
            console.error('Error refreshing dashboard data:', error);
        });
}

// Initialize tooltips and popovers when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Set up dashboard auto-refresh if on dashboard page
    if (document.getElementById('projectStatusChart')) {
        // Set up auto-refresh every 5 minutes
        setInterval(refreshDashboardData, 5 * 60 * 1000);
    }

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            
            // On mobile, toggle the sidebar visibility
            const sidebar = document.querySelector('.sidebar');
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('active');
            }
        });
    }

    // Hide sidebar on mobile when clicking outside
    document.addEventListener('click', function(event) {
        const sidebar = document.querySelector('.sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        
        if (window.innerWidth <= 768 && 
            sidebar && 
            sidebar.classList.contains('active') && 
            !sidebar.contains(event.target) && 
            !sidebarToggle.contains(event.target)) {
            sidebar.classList.remove('active');
        }
    });

    // Add event listeners to table rows for highlighting
    const projectRows = document.querySelectorAll('table tbody tr');
    if (projectRows) {
        projectRows.forEach(row => {
            row.addEventListener('mouseover', function() {
                this.classList.add('table-active');
            });
            row.addEventListener('mouseout', function() {
                this.classList.remove('table-active');
            });
        });
    }

    // Add click event to "Add Project" button for demonstration
    const addProjectBtn = document.querySelector('a.btn-primary');
    if (addProjectBtn) {
        addProjectBtn.addEventListener('click', function(e) {
            e.preventDefault();
            alert('This would open a form to add a new project in a real application.');
        });
    }
}); 
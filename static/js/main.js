// Construction CRM - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Construction CRM JavaScript loaded');

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
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
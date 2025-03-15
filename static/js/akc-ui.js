/**
 * AKC LLC UI Enhancements
 * Adds subtle animations and interactions to improve user experience
 */

document.addEventListener('DOMContentLoaded', function() {
  // Apply fade-in animation to main content
  const mainContent = document.querySelector('.container.py-4, .container.mt-4');
  if (mainContent) {
    mainContent.classList.add('fade-in');
  }

  // Enhance cards with hover effects
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-5px)';
      this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
      this.style.boxShadow = '0 8px 15px rgba(0, 0, 0, 0.1)';
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
      this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
    });
  });

  // Make tables more interactive
  const tableRows = document.querySelectorAll('tbody tr');
  tableRows.forEach(row => {
    row.addEventListener('mouseenter', function() {
      this.style.backgroundColor = 'rgba(4, 133, 234, 0.05)';
      this.style.transition = 'background-color 0.2s ease';
    });
    
    row.addEventListener('mouseleave', function() {
      this.style.backgroundColor = '';
    });
  });

  // Add ripple effect to buttons
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(button => {
    button.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = button.getBoundingClientRect();
      
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      ripple.classList.add('btn-ripple');
      
      button.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });

  // Improve form field focus interactions
  const formInputs = document.querySelectorAll('.form-control');
  formInputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('input-focused');
    });
    
    input.addEventListener('blur', function() {
      this.parentElement.classList.remove('input-focused');
    });
  });

  // Add confirmation to delete buttons
  const deleteButtons = document.querySelectorAll('[data-action="delete"]');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        e.preventDefault();
      }
    });
  });

  // Initialize tooltips
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
      new bootstrap.Tooltip(tooltip);
    });
  }

  // Add data-bs-toggle="tooltip" to action buttons that don't have text
  const iconOnlyButtons = document.querySelectorAll('.btn-sm:not(:has(span)), .btn:has(i:only-child)');
  iconOnlyButtons.forEach(button => {
    if (!button.getAttribute('data-bs-toggle')) {
      button.setAttribute('data-bs-toggle', 'tooltip');
      
      // If there's no title, try to set one based on icon or class
      if (!button.getAttribute('title')) {
        if (button.classList.contains('btn-danger') || button.querySelector('.fa-trash')) {
          button.setAttribute('title', 'Delete');
        } else if (button.classList.contains('btn-warning') || button.querySelector('.fa-edit')) {
          button.setAttribute('title', 'Edit');
        } else if (button.classList.contains('btn-info') || button.querySelector('.fa-eye')) {
          button.setAttribute('title', 'View');
        }
      }
    }
  });
}); 
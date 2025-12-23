// Football Predictor Pro - Advanced JavaScript Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAnimations();
    initializeInteractiveElements();
    initializeFormEnhancements();
    initializePerformanceTracking();
    initializeResponsiveFeatures();
});

// Animation System
function initializeAnimations() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.card, .feature-card, .stat-card').forEach(el => {
        observer.observe(el);
    });

    // Parallax effect for hero sections
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero-section');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
}

// Interactive Elements
function initializeInteractiveElements() {
    // Enhanced hover effects
    document.querySelectorAll('.card, .btn, .feature-card').forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Loading states for buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('btn-loading')) {
                this.classList.add('btn-loading');
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                
                // Reset after 2 seconds (for demo purposes)
                setTimeout(() => {
                    this.classList.remove('btn-loading');
                    this.innerHTML = this.getAttribute('data-original-text') || this.innerHTML;
                }, 2000);
            }
        });
    });

    // Tooltip system
    initializeTooltips();
}

// Form Enhancements
function initializeFormEnhancements() {
    // Real-time form validation
    document.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearValidation);
    });

    // Auto-save form data
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('input', debounce(saveFormData, 500));
        loadFormData(form);
    });

    // Enhanced select dropdowns
    document.querySelectorAll('select').forEach(select => {
        select.addEventListener('change', function() {
            this.classList.add('selected');
            setTimeout(() => {
                this.classList.remove('selected');
            }, 200);
        });
    });
}

// Performance Tracking
function initializePerformanceTracking() {
    // Track page load performance
    window.addEventListener('load', () => {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
        
        // Send analytics data
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_load', {
                'load_time': loadTime,
                'page_title': document.title
            });
        }
    });

    // Track user interactions
    document.addEventListener('click', (e) => {
        const target = e.target.closest('a, button, .card');
        if (target) {
            trackInteraction(target);
        }
    });
}

// Responsive Features
function initializeResponsiveFeatures() {
    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', () => {
            navbarCollapse.classList.toggle('show');
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }

    // Responsive table handling
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (table.scrollWidth > table.clientWidth) {
            table.classList.add('has-horizontal-scroll');
        }
    });

    // Dynamic font sizing
    adjustFontSize();
    window.addEventListener('resize', debounce(adjustFontSize, 250));
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
    } else {
        clearFieldError(field);
    }
}

function clearValidation(event) {
    const field = event.target;
    clearFieldError(field);
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function saveFormData(event) {
    const form = event.target.closest('form');
    if (form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        localStorage.setItem(`form_${form.id || 'default'}`, JSON.stringify(data));
    }
}

function loadFormData(form) {
    const savedData = localStorage.getItem(`form_${form.id || 'default'}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const field = form.querySelector(`[name="${key}"]`);
            if (field && !field.value) {
                field.value = data[key];
            }
        });
    }
}

function initializeTooltips() {
    // Custom tooltip implementation
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    
    element.tooltip = tooltip;
}

function hideTooltip(event) {
    const element = event.target;
    if (element.tooltip) {
        element.tooltip.remove();
        element.tooltip = null;
    }
}

function trackInteraction(element) {
    const interactionData = {
        element: element.tagName.toLowerCase(),
        text: element.textContent.trim().substring(0, 50),
        timestamp: new Date().toISOString(),
        url: window.location.pathname
    };
    
    console.log('User interaction:', interactionData);
    
    // Send to analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', 'user_interaction', interactionData);
    }
}

function adjustFontSize() {
    const width = window.innerWidth;
    const html = document.documentElement;
    
    if (width < 768) {
        html.style.fontSize = '14px';
    } else if (width < 1024) {
        html.style.fontSize = '16px';
    } else {
        html.style.fontSize = '18px';
    }
}

// Advanced Features
function initializeAdvancedFeatures() {
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            focusSearch();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            closeModals();
        }
    });

    // Progressive Web App features (disabled - no service worker file)
    // if ('serviceWorker' in navigator) {
    //     navigator.serviceWorker.register('/sw.js')
    //         .then(registration => {
    //             console.log('SW registered: ', registration);
    //         })
    //         .catch(registrationError => {
    //             console.log('SW registration failed: ', registrationError);
    //         });
    // }
}

function focusSearch() {
    const searchInput = document.querySelector('input[type="search"], .search-input');
    if (searchInput) {
        searchInput.focus();
    }
}

function closeModals() {
    const modals = document.querySelectorAll('.modal.show');
    modals.forEach(modal => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
}

// Initialize advanced features
initializeAdvancedFeatures();

// Export functions for global access
window.FootballPredictor = {
    trackInteraction,
    saveFormData,
    loadFormData,
    validateField,
    showTooltip,
    hideTooltip
}; 
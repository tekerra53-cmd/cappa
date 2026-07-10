// SRMS - Modern JavaScript Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAnimations();
    initializeFormEnhancements();
    initializeTableInteractions();
    initializeAlerts();
});

// Animation System
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add bounce-in animation to dashboard cards
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    dashboardCards.forEach((card, index) => {
        card.classList.add('bounce-in');
        card.style.animationDelay = `${index * 0.1}s`;
    });
}

// Form Enhancements
function initializeFormEnhancements() {
    // Add loading state to form submissions
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // Real-time form validation
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateInput(this);
        });

        input.addEventListener('input', function() {
            clearValidation(this);
        });
    });
}

// Input Validation
function validateInput(input) {
    const value = input.value.trim();
    const isRequired = input.hasAttribute('required');
    const minLength = input.getAttribute('minlength');

    // Remove existing validation classes
    input.classList.remove('is-valid', 'is-invalid');

    if (isRequired && !value) {
        showValidationError(input, 'This field is required');
        return false;
    }

    if (minLength && value.length < parseInt(minLength)) {
        showValidationError(input, `Minimum ${minLength} characters required`);
        return false;
    }

    if (value) {
        input.classList.add('is-valid');
    }

    return true;
}

function showValidationError(input, message) {
    input.classList.add('is-invalid');

    // Create or update error message
    let errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        input.parentNode.appendChild(errorElement);
    }
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearValidation(input) {
    input.classList.remove('is-valid', 'is-invalid');
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

// Table Interactions
function initializeTableInteractions() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.01)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Alert System
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-dismiss alerts after 5 seconds unless marked persistent
        if (!alert.hasAttribute('data-persist')) {
            setTimeout(() => {
                fadeOut(alert);
            }, 5000);
        }

        // Add close button functionality
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                fadeOut(alert);
            });
        }
    });
}

// Utility Functions
function fadeOut(element) {
    element.style.transition = 'all 0.3s ease-out';
    element.style.opacity = '0';
    element.style.transform = 'translateY(-10px)';

    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, 300);
}

// Smooth scrolling for anchor links
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

// Add loading states for navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function() {
        if (this.href && !this.href.includes('#')) {
            this.innerHTML += ' <span class="loading"></span>';
        }
    });
});

// GPA Calculator Animation
function animateGPA(element) {
    const targetValue = parseFloat(element.textContent);
    let currentValue = 0;
    const increment = targetValue / 50;
    const timer = setInterval(() => {
        currentValue += increment;
        if (currentValue >= targetValue) {
            currentValue = targetValue;
            clearInterval(timer);
        }
        element.textContent = currentValue.toFixed(2);
    }, 20);
}

// Initialize GPA animations on result pages
const gpaElements = document.querySelectorAll('.gpa-value');
gpaElements.forEach(element => {
    animateGPA(element);
});

// Print functionality enhancement
function enhancePrint() {
    const printBtn = document.querySelector('.btn-print, [onclick*="print"]');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
}

// Initialize print enhancement
enhancePrint();

// Responsive navigation toggle
const navbarToggler = document.querySelector('.navbar-toggler');
if (navbarToggler) {
    navbarToggler.addEventListener('click', function() {
        const navbarCollapse = document.querySelector('.navbar-collapse');
        if (navbarCollapse) {
            navbarCollapse.classList.toggle('show');
        }
    });
}

// Theme toggle (future enhancement)
function initializeThemeToggle() {
    // Add dark mode toggle functionality here if needed
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Initialize theme toggle
initializeThemeToggle();

// Performance optimization: Lazy load images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
lazyLoadImages();

// Export functions for global use
window.SRMS = {
    animateGPA,
    fadeOut,
    validateInput
};

// كوريزا - ملف JavaScript الرئيسي

// تهيئة التطبيق مع معالجة الأخطاء
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeApp();
        // إخفاء أي مؤشرات تحميل موجودة
        hideAllLoadingIndicators();
    } catch (error) {
        console.error('خطأ في تهيئة التطبيق:', error);
        hideAllLoadingIndicators();
    }
});

// إخفاء جميع مؤشرات التحميل (بدون إجبار اكتمال التحميل)
function hideAllLoadingIndicators() {
    // إخفاء مؤشرات التحميل العامة
    const loadingIndicators = document.querySelectorAll('.loading-indicator, .loading-overlay, .spinner-border');
    loadingIndicators.forEach(indicator => {
        indicator.style.display = 'none';
        indicator.remove();
    });
    
    // إخفاء مؤشرات التحميل في الصفحة
    const pageLoaders = document.querySelectorAll('[class*="loading"], [class*="spinner"]');
    pageLoaders.forEach(loader => {
        loader.style.display = 'none';
        loader.remove();
    });
    
    // إزالة أي عناصر تحميل معلقة
    const body = document.body;
    if (body.classList.contains('loading')) {
        body.classList.remove('loading');
    }
}

// تهيئة التطبيق
function initializeApp() {
    // إخفاء مؤشرات التحميل أولاً
    hideAllLoadingIndicators();
    
    // تهيئة الرسوم المتحركة
    initializeAnimations();
    
    // تهيئة النماذج
    initializeForms();
    
    // تهيئة التنقل
    initializeNavigation();
    
    // تهيئة البحث
    initializeSearch();
    
    // تهيئة الإشعارات
    initializeNotifications();
    
    // تهيئة التمرير
    initializeScroll();
    
    // تهيئة الأدوات المساعدة
    initializeUtilities();
    
    // إخفاء مؤشرات التحميل نهائياً
    setTimeout(hideAllLoadingIndicators, 1000);
}

// تهيئة الرسوم المتحركة
function initializeAnimations() {
    // إضافة الرسوم المتحركة للعناصر عند الظهور
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // مراقبة العناصر
    document.querySelectorAll('.feature-card, .post-card, .category-card').forEach(el => {
        observer.observe(el);
    });
}

// تهيئة النماذج
function initializeForms() {
    // تحسين النماذج
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // إضافة التحقق من صحة النماذج
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // تحسين حقول الإدخال
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            // إضافة تأثير التركيز
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                if (!this.value) {
                    this.parentElement.classList.remove('focused');
                }
            });
            
            // التحقق من صحة البيانات في الوقت الفعلي
            input.addEventListener('input', function() {
                validateField(this);
            });
        });
    });
}

// التحقق من صحة الحقل
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const required = field.hasAttribute('required');
    
    // إزالة رسائل الخطأ السابقة
    removeFieldError(field);
    
    // التحقق من الحقول المطلوبة
    if (required && !value) {
        showFieldError(field, 'هذا الحقل مطلوب');
        return false;
    }
    
    // التحقق من البريد الإلكتروني
    if (type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'البريد الإلكتروني غير صحيح');
            return false;
        }
    }
    
    // التحقق من كلمة المرور
    if (type === 'password' && value) {
        if (value.length < 8) {
            showFieldError(field, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل');
            return false;
        }
    }
    
    // التحقق من رقم الهاتف
    if (field.name === 'phone' && value) {
        const phoneRegex = /^(\+966|0)?[5-9][0-9]{8}$/;
        if (!phoneRegex.test(value)) {
            showFieldError(field, 'رقم الهاتف غير صحيح');
            return false;
        }
    }
    
    return true;
}

// إظهار رسالة الخطأ
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentElement.appendChild(errorDiv);
}

// إزالة رسالة الخطأ
function removeFieldError(field) {
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// تهيئة التنقل
function initializeNavigation() {
    // تحسين شريط التنقل
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        // إضافة تأثير التمرير
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // تحسين القوائم المنسدلة
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                menu.classList.toggle('show');
            });
            
            // إغلاق القائمة عند النقر خارجها
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    menu.classList.remove('show');
                }
            });
        }
    });
}

// تهيئة البحث
function initializeSearch() {
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        
        if (searchInput) {
            // إضافة البحث التلقائي
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    performSearch(this.value);
                }, 300);
            });
            
            // إضافة اختصارات لوحة المفاتيح
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchForm.submit();
                }
            });
        }
    }
}

// تنفيذ البحث
function performSearch(query) {
    if (query.length < 3) return;
    
    // إظهار مؤشر التحميل
    showLoadingIndicator();
    
    // تنفيذ طلب البحث
    fetch(`/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            hideLoadingIndicator();
            displaySearchResults(data);
        })
        .catch(error => {
            hideLoadingIndicator();
            console.error('خطأ في البحث:', error);
        });
}

// عرض نتائج البحث
function displaySearchResults(results) {
    // تنفيذ عرض النتائج
    console.log('نتائج البحث:', results);
}

// تهيئة الإشعارات
function initializeNotifications() {
    // إخفاء الإشعارات تلقائياً
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.hide();
        }, 5000);
    });
    
    // إضافة إشعار مخصص
    window.showNotification = function(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast show`;
        toast.setAttribute('role', 'alert');
        
        const iconClass = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        }[type] || 'fas fa-info-circle text-info';
        
        toast.innerHTML = `
            <div class="toast-header">
                <i class="${iconClass} me-2"></i>
                <strong class="me-auto">إشعار</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // إخفاء الإشعار بعد 5 ثوان
        setTimeout(() => {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.hide();
        }, 5000);
    };
}

// إنشاء حاوية الإشعارات
function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

// تهيئة التمرير
function initializeScroll() {
    // إضافة زر العودة للأعلى
    const backToTopButton = createBackToTopButton();
    document.body.appendChild(backToTopButton);
    
    // إظهار/إخفاء زر العودة للأعلى
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });
    
    // النقر على زر العودة للأعلى
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// إنشاء زر العودة للأعلى
function createBackToTopButton() {
    const button = document.createElement('button');
    button.className = 'back-to-top btn btn-primary';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.setAttribute('aria-label', 'العودة للأعلى');
    
    // إضافة الأنماط
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        background: var(--primary-color);
        color: white;
        font-size: 18px;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    `;
    
    // إضافة تأثيرات التمرير
    button.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
    });
    
    return button;
}

// تهيئة الأدوات المساعدة
function initializeUtilities() {
    // إضافة مؤشر التحميل
    window.showLoadingIndicator = function() {
        const indicator = document.createElement('div');
        indicator.className = 'loading-indicator';
        indicator.innerHTML = `
            <div class="loading-overlay">
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">جاري التحميل...</span>
                    </div>
                    <p class="mt-3">جاري التحميل...</p>
                </div>
            </div>
        `;
        
        // إضافة الأنماط
        indicator.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
        
        document.body.appendChild(indicator);
        return indicator;
    };
    
    // إخفاء مؤشر التحميل
    window.hideLoadingIndicator = function() {
        const indicator = document.querySelector('.loading-indicator');
        if (indicator) {
            indicator.remove();
        }
    };
    
    // إضافة وظيفة النسخ
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('تم نسخ النص بنجاح', 'success');
        }).catch(() => {
            showNotification('فشل في نسخ النص', 'error');
        });
    };
    
    // إضافة وظيفة التنسيق
    window.formatDate = function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ar-SA', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };
    
    // إضافة وظيفة التنسيق
    window.formatNumber = function(number) {
        return new Intl.NumberFormat('ar-SA').format(number);
    };
}

// وظائف إضافية
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// تهيئة الأحداث
document.addEventListener('DOMContentLoaded', function() {
    // إضافة تأثيرات التمرير
    const style = document.createElement('style');
    style.textContent = `
        .back-to-top.show {
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        .navbar.scrolled {
            background: rgba(0,123,255,0.95) !important;
            backdrop-filter: blur(10px);
        }
        
        .loading-overlay {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .loading-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
    `;
    document.head.appendChild(style);
});

// إخفاء مؤشرات التحميل بعد فترة زمنية قصيرة فقط
setTimeout(function() {
    hideAllLoadingIndicators();
}, 1000);

// تصدير الوظائف للاستخدام العام
window.CorizaApp = {
    showNotification,
    showLoadingIndicator,
    hideLoadingIndicator,
    copyToClipboard,
    formatDate,
    formatNumber,
    debounce,
    throttle
};


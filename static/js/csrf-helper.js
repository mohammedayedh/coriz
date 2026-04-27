/**
 * CSRF Helper - دالة مساعدة للحصول على CSRF token
 * يجب تضمين هذا الملف في جميع الصفحات التي تستخدم AJAX
 */

/**
 * الحصول على CSRF token من الصفحة أو الكوكيز
 * @returns {string} CSRF token
 */
function getCsrf() {
    // محاولة 1: الحصول من input مخفي في النموذج
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput && tokenInput.value) {
        return tokenInput.value;
    }
    
    // محاولة 2: الحصول من meta tag
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (tokenMeta && tokenMeta.content) {
        return tokenMeta.content;
    }
    
    // محاولة 3: الحصول من الكوكيز
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    
    if (cookieValue) {
        return cookieValue.split('=')[1];
    }
    
    // إذا لم نجد token، نعرض تحذير
    console.warn('CSRF token not found! Make sure {% csrf_token %} is in your template.');
    return '';
}

/**
 * إضافة CSRF token إلى headers
 * @param {Object} headers - كائن headers
 * @returns {Object} headers مع CSRF token
 */
function addCsrfHeader(headers = {}) {
    const csrfToken = getCsrf();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }
    return headers;
}

/**
 * fetch مع CSRF token تلقائي
 * @param {string} url - عنوان URL
 * @param {Object} options - خيارات fetch
 * @returns {Promise} - Promise من fetch
 */
function csrfFetch(url, options = {}) {
    // إضافة CSRF token للطلبات غير GET
    if (!options.method || options.method.toUpperCase() !== 'GET') {
        options.headers = addCsrfHeader(options.headers || {});
    }
    
    // إضافة Content-Type إذا لم يكن موجوداً
    if (!options.headers['Content-Type'] && options.body && typeof options.body === 'string') {
        options.headers['Content-Type'] = 'application/json';
    }
    
    return fetch(url, options);
}

// تصدير للاستخدام العام
if (typeof window !== 'undefined') {
    window.getCsrf = getCsrf;
    window.addCsrfHeader = addCsrfHeader;
    window.csrfFetch = csrfFetch;
}

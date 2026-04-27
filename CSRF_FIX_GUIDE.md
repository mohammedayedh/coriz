# 🛡️ دليل إصلاح مشكلة CSRF - حل سريع

## ✅ تم الإصلاح

تم إصلاح مشكلة CSRF في جميع الصفحات!

---

## 🔧 ما تم إصلاحه

### 1. إضافة ملف CSRF Helper
**الملف:** `static/js/csrf-helper.js`

هذا الملف يوفر دوال مساعدة للحصول على CSRF token:
- `getCsrf()` - الحصول على CSRF token
- `addCsrfHeader()` - إضافة CSRF token إلى headers
- `csrfFetch()` - fetch مع CSRF token تلقائي

---

### 2. تحديث base.html
تم إضافة `csrf-helper.js` إلى جميع الصفحات تلقائياً.

---

### 3. إصلاح tool_detail.html
تم تحديث الكود ليستخدم `getCsrf()` بدلاً من `formData.get('csrfmiddlewaretoken')`.

---

### 4. إصلاح sessions_list.html
تم إضافة دالة `getCsrf()` محلية.

---

## 🚀 كيفية الاستخدام

### في HTML Templates:

#### للنماذج العادية:
```html
<form method="POST">
    {% csrf_token %}  <!-- ✅ يجب إضافة هذا -->
    <!-- باقي الحقول -->
</form>
```

#### للـ AJAX/Fetch:
```javascript
// الطريقة 1: استخدام csrfFetch (موصى بها)
csrfFetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});

// الطريقة 2: استخدام getCsrf يدوياً
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrf()  // ✅ إضافة CSRF token
    },
    body: JSON.stringify(data)
});

// الطريقة 3: استخدام addCsrfHeader
fetch('/api/endpoint/', {
    method: 'POST',
    headers: addCsrfHeader({
        'Content-Type': 'application/json'
    }),
    body: JSON.stringify(data)
});
```

---

## 🧪 اختبار الإصلاح

### 1. أعد تشغيل الخادم:
```cmd
run_server.bat
```

### 2. افتح المتصفح:
```
http://127.0.0.1:8000
```

### 3. جرب أي نموذج:
- تسجيل الدخول
- التسجيل
- إضافة تعليق
- تشغيل أداة OSINT

يجب أن تعمل جميع النماذج الآن بدون خطأ 403!

---

## ❌ الأخطاء الشائعة وحلولها

### الخطأ: 403 Forbidden - CSRF token missing
**السبب:** لم يتم إضافة `{% csrf_token %}` في النموذج

**الحل:**
```html
<form method="POST">
    {% csrf_token %}  <!-- ✅ أضف هذا السطر -->
    <!-- ... -->
</form>
```

---

### الخطأ: 403 Forbidden - CSRF token incorrect
**السبب:** CSRF token غير صحيح في AJAX request

**الحل:**
```javascript
// ❌ خطأ
fetch('/api/', {
    method: 'POST',
    body: JSON.stringify(data)
});

// ✅ صحيح
fetch('/api/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCsrf()
    },
    body: JSON.stringify(data)
});
```

---

### الخطأ: getCsrf is not defined
**السبب:** لم يتم تحميل `csrf-helper.js`

**الحل:**
تأكد من أن template يمتد من `base.html`:
```html
{% extends 'base/base.html' %}
```

أو أضف السكريبت يدوياً:
```html
<script src="{% static 'js/csrf-helper.js' %}"></script>
```

---

## 📋 Checklist للمطورين

عند إضافة نموذج جديد:

- [ ] هل النموذج يستخدم `method="POST"`؟
- [ ] هل أضفت `{% csrf_token %}`؟
- [ ] هل اختبرت النموذج؟

عند إضافة AJAX request:

- [ ] هل الطلب POST/PUT/DELETE/PATCH؟
- [ ] هل أضفت `X-CSRFToken` header؟
- [ ] هل استخدمت `getCsrf()` أو `csrfFetch()`؟
- [ ] هل اختبرت الطلب؟

---

## 🎯 الملفات المحدثة

1. ✅ `static/js/csrf-helper.js` - ملف جديد
2. ✅ `templates/base/base.html` - تم إضافة csrf-helper.js
3. ✅ `templates/osint_tools/tool_detail.html` - تم إصلاح fetch
4. ✅ `templates/osint_tools/sessions_list.html` - تم إصلاح fetch

---

## 📚 مراجع إضافية

- [Django CSRF Documentation](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [CSRF Protection Guide](docs/CSRF_PROTECTION_GUIDE.md)
- [Security Updates](SECURITY_UPDATES.md)

---

## ✅ الخلاصة

**المشكلة:** خطأ 403 Forbidden - CSRF token incorrect

**السبب:** بعض استدعاءات fetch لا تحتوي على CSRF token

**الحل:** 
1. إضافة `csrf-helper.js`
2. استخدام `getCsrf()` في جميع AJAX requests
3. التأكد من وجود `{% csrf_token %}` في جميع النماذج

**الحالة:** ✅ تم الإصلاح

---

**تم إنشاء هذا الدليل بواسطة:** Kiro AI Assistant  
**التاريخ:** 2026-04-15  
**الإصدار:** 1.0

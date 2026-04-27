# 🛡️ دليل حماية CSRF - مشروع Coriza OSINT

## 📋 نظرة عامة

تم إصلاح المشكلة الحرجة #4 بإزالة جميع استخدامات `@csrf_exempt` غير المبررة وتفعيل حماية CSRF على جميع POST endpoints.

---

## 🔍 ما هو CSRF؟

CSRF (Cross-Site Request Forgery) هو هجوم يجبر المستخدم المصادق على تنفيذ إجراءات غير مرغوب فيها على تطبيق ويب.

### مثال على هجوم CSRF:
```html
<!-- موقع خبيث -->
<form action="https://coriza.cloud/newsletter/subscribe/" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com">
</form>
<script>document.forms[0].submit();</script>
```

بدون حماية CSRF، سيتم تنفيذ هذا الطلب باستخدام جلسة المستخدم الحالية!

---

## ✅ الحماية المطبقة

### 1. إزالة csrf_exempt
تم إزالة `@csrf_exempt` من:
- ✅ `main/views.py` - `newsletter_subscribe_view`
- ✅ `osint_tools/views.py` - `api_stats`

### 2. تفعيل CSRF Middleware
```python
# coriza/settings.py
MIDDLEWARE = [
    ...
    'django.middleware.csrf.CsrfViewMiddleware',  # ✅ مفعل
    ...
]
```

---

## 🔧 كيفية استخدام CSRF في التطبيق

### 1. في Django Templates

#### في النماذج (Forms):
```html
<form method="POST" action="/newsletter/subscribe/">
    {% csrf_token %}  <!-- ✅ إضافة CSRF token -->
    <input type="email" name="email" required>
    <button type="submit">اشترك</button>
</form>
```

#### في AJAX مع jQuery:
```javascript
// الحصول على CSRF token من الكوكيز
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// إرسال طلب POST مع CSRF token
$.ajax({
    url: '/newsletter/subscribe/',
    type: 'POST',
    headers: {
        'X-CSRFToken': csrftoken
    },
    data: JSON.stringify({
        email: 'user@example.com'
    }),
    contentType: 'application/json',
    success: function(response) {
        console.log('نجح!', response);
    }
});
```

---

### 2. في JavaScript الحديث (Vanilla JS)

#### استخدام الوظائف المدمجة في main.js:
```javascript
// ✅ الطريقة الموصى بها - استخدام csrfFetch
csrfFetch('/newsletter/subscribe/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'user@example.com'
    })
})
.then(response => response.json())
.then(data => {
    console.log('نجح!', data);
})
.catch(error => {
    console.error('خطأ:', error);
});
```

#### أو يدوياً:
```javascript
// الحصول على CSRF token
const csrfToken = getCSRFToken();

// إرسال طلب POST
fetch('/newsletter/subscribe/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken  // ✅ إضافة CSRF token
    },
    body: JSON.stringify({
        email: 'user@example.com'
    })
})
.then(response => response.json())
.then(data => {
    console.log('نجح!', data);
});
```

---

### 3. في React/Vue/Angular

#### React Example:
```javascript
// في component
import { useState, useEffect } from 'react';

function NewsletterForm() {
    const [csrfToken, setCsrfToken] = useState('');
    
    useEffect(() => {
        // الحصول على CSRF token عند تحميل المكون
        const token = getCookie('csrftoken');
        setCsrfToken(token);
    }, []);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        
        const response = await fetch('/newsletter/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // ✅ إضافة CSRF token
            },
            body: JSON.stringify({
                email: email
            })
        });
        
        const data = await response.json();
        console.log(data);
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input type="email" name="email" required />
            <button type="submit">اشترك</button>
        </form>
    );
}
```

---

### 4. في Axios

#### إعداد Axios مع CSRF:
```javascript
import axios from 'axios';

// إعداد Axios لإرسال CSRF token تلقائياً
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

// الآن جميع طلبات Axios ستتضمن CSRF token تلقائياً
axios.post('/newsletter/subscribe/', {
    email: 'user@example.com'
})
.then(response => {
    console.log('نجح!', response.data);
});
```

---

## 🚫 الأخطاء الشائعة

### ❌ خطأ 1: نسيان CSRF token
```javascript
// ❌ خطأ - سيفشل مع 403 Forbidden
fetch('/newsletter/subscribe/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({email: 'test@example.com'})
});
```

**الحل:**
```javascript
// ✅ صحيح
csrfFetch('/newsletter/subscribe/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({email: 'test@example.com'})
});
```

---

### ❌ خطأ 2: استخدام csrf_exempt بدون مبرر
```python
# ❌ خطأ - يزيل الحماية
@csrf_exempt
def my_view(request):
    ...
```

**الحل:**
```python
# ✅ صحيح - استخدام CSRF protection
def my_view(request):
    # Django سيتحقق من CSRF token تلقائياً
    ...
```

---

### ❌ خطأ 3: إرسال CSRF token في GET requests
```javascript
// ❌ غير ضروري - GET لا يحتاج CSRF
fetch('/api/stats/', {
    method: 'GET',
    headers: {
        'X-CSRFToken': getCSRFToken()  // غير ضروري
    }
});
```

**الحل:**
```javascript
// ✅ صحيح - GET لا يحتاج CSRF token
fetch('/api/stats/', {
    method: 'GET'
});
```

---

## 🔐 متى تستخدم csrf_exempt؟

استخدم `@csrf_exempt` فقط في الحالات التالية:

### 1. API Endpoints مع Token Authentication
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_endpoint(request):
    # DRF يستخدم Token Authentication بدلاً من CSRF
    ...
```

### 2. Webhooks من خدمات خارجية
```python
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib

@csrf_exempt
def webhook_endpoint(request):
    # التحقق من التوقيع بدلاً من CSRF
    signature = request.headers.get('X-Hub-Signature')
    expected = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        return JsonResponse({'error': 'Invalid signature'}, status=403)
    
    # معالجة الـ webhook
    ...
```

### 3. Public APIs بدون مصادقة
```python
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def public_api(request):
    # API عام بدون مصادقة
    # يجب إضافة rate limiting وvalidation قوي
    ...
```

---

## 🧪 اختبار CSRF Protection

### 1. اختبار يدوي

#### اختبار بدون CSRF token:
```bash
curl -X POST http://localhost:8000/newsletter/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# النتيجة المتوقعة: 403 Forbidden
```

#### اختبار مع CSRF token:
```bash
# الحصول على CSRF token أولاً
CSRF_TOKEN=$(curl -c cookies.txt http://localhost:8000/ | grep csrftoken | awk '{print $7}')

# إرسال الطلب مع CSRF token
curl -X POST http://localhost:8000/newsletter/subscribe/ \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -d '{"email": "test@example.com"}'

# النتيجة المتوقعة: 200 OK
```

---

### 2. اختبار في Django Tests

```python
from django.test import TestCase, Client
from django.urls import reverse

class NewsletterViewTest(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
    
    def test_newsletter_subscribe_without_csrf(self):
        """اختبار الفشل بدون CSRF token"""
        response = self.client.post(
            reverse('main:newsletter_subscribe'),
            data={'email': 'test@example.com'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
    
    def test_newsletter_subscribe_with_csrf(self):
        """اختبار النجاح مع CSRF token"""
        # الحصول على CSRF token
        self.client.get(reverse('main:home'))
        
        # إرسال الطلب مع CSRF token
        response = self.client.post(
            reverse('main:newsletter_subscribe'),
            data={'email': 'test@example.com'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
```

---

## 📚 مراجع إضافية

### Django Documentation:
- [CSRF Protection](https://docs.djangoproject.com/en/stable/ref/csrf/)
- [CSRF in AJAX](https://docs.djangoproject.com/en/stable/howto/csrf/#ajax)

### OWASP:
- [Cross-Site Request Forgery (CSRF)](https://owasp.org/www-community/attacks/csrf)
- [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

## ✅ Checklist للمطورين

عند إضافة endpoint جديد:

- [ ] هل الـ endpoint يستقبل POST/PUT/DELETE/PATCH؟
- [ ] هل يحتاج مصادقة (authentication)؟
- [ ] هل تم إضافة CSRF protection؟
- [ ] هل تم اختبار الـ endpoint مع وبدون CSRF token؟
- [ ] هل تم توثيق كيفية استخدام الـ endpoint في الـ frontend؟

---

**تم إنشاء هذا الدليل بواسطة:** Kiro AI Assistant  
**التاريخ:** 2026-04-15  
**الإصدار:** 1.0

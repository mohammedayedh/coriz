## 6. نظام الأمان والحماية (Security System)

### 6.1 طبقات الأمان في المشروع

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
└─────────────────────────────────────────────────────────────┘

Layer 1: Network Security
├── HTTPS Enforcement (SECURE_SSL_REDIRECT)
├── HSTS Headers
└── Secure Proxy Headers

Layer 2: Application Security
├── CSRF Protection
├── XSS Protection
├── Clickjacking Protection
└── Content Type Sniffing Protection

Layer 3: Authentication & Authorization
├── Email-based Authentication
├── Password Validators
├── Clearance Level System (L1-L4)
└── Session Management

Layer 4: Rate Limiting
├── Login Attempts
├── API Requests
└── Tool Execution

Layer 5: Data Security
├── Input Validation
├── SQL Injection Prevention (ORM)
├── Command Injection Prevention
└── Sensitive Data Encryption

Layer 6: Monitoring & Logging
├── Activity Logs
├── Login Attempts Tracking
├── Error Monitoring (Sentry)
└── Audit Trail
```

### 6.2 نظام الصلاحيات (Clearance Level System)

#### 6.2.1 مستويات التصريح الأمني

```python
CLEARANCE_LEVELS = [
    ('L1', 'Level 1 - Public OSINT'),
    ('L2', 'Level 2 - Commercial APIs'),
    ('L3', 'Level 3 - Private & Leaked'),
    ('L4', 'Level 4 - Agency / Admin'),
]
```

**تفصيل المستويات:**

| المستوى | الوصف | الأدوات المتاحة | مثال |
|---------|-------|-----------------|------|
| **L1** | مصادر عامة مفتوحة | أدوات OSINT المجانية | Sherlock, theHarvester |
| **L2** | واجهات تجارية | أدوات تتطلب API Keys مدفوعة | VirusTotal, Shodan |
| **L3** | بيانات خاصة وتسريبات | أدوات تصل لقواعد بيانات مسربة | Have I Been Pwned, Dehashed |
| **L4** | جهات حكومية فقط | أدوات حساسة للغاية | أدوات استخباراتية متقدمة |

#### 6.2.2 آلية التحقق من الصلاحيات

```python
# في views.py - run_tool()
def run_tool(request, tool_slug):
    tool = get_object_or_404(OSINTTool, slug=tool_slug)
    
    # الحصول على مستوى تصريح المستخدم
    try:
        user_clearance = request.user.profile.clearance_level
    except:
        user_clearance = 'L1'  # افتراضي
    
    # التحقق من الصلاحية
    if user_clearance < tool.required_clearance:
        return JsonResponse({
            'success': False,
            'error': f'تحتاج إلى مستوى تصريح {tool.required_clearance} أو أعلى',
            'user_clearance': user_clearance,
            'required_clearance': tool.required_clearance
        }, status=403)
```

**مثال عملي:**
```
المستخدم: clearance_level = 'L2'
الأداة: required_clearance = 'L3'

النتيجة: ❌ رفض الوصول

المستخدم: clearance_level = 'L4'
الأداة: required_clearance = 'L2'

النتيجة: ✅ السماح بالوصول
```

### 6.3 حماية CSRF (Cross-Site Request Forgery)

#### 6.3.1 آلية الحماية

```python
# في settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF Protection
]

CSRF_COOKIE_SECURE = True  # في الإنتاج
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = [
    'https://coriza.cloud',
    'https://www.coriza.cloud'
]
```

#### 6.3.2 استخدام CSRF في الواجهة

```html
<!-- في النماذج -->
<form method="POST">
    {% csrf_token %}
    <input type="text" name="target">
    <button type="submit">تشغيل</button>
</form>
```

```javascript
// في AJAX Requests
// static/js/csrf-helper.js
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

fetch('/osint/tools/sherlock/run/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({target: 'john_doe'})
});
```

### 6.4 Rate Limiting (تحديد معدل الطلبات)

#### 6.4.1 Rate Limiting على مستوى التطبيق

```python
# في authentication/views.py
RATE_LIMITS = {
    'login': {'limit': 5, 'window': 15 * 60},  # 5 محاولات / 15 دقيقة
    'password_reset': {'limit': 5, 'window': 15 * 60},
    'resend_verification': {'limit': 5, 'window': 15 * 60},
    'availability': {'limit': 10, 'window': 120},  # 10 طلبات / دقيقتين
}

def is_rate_limited(kind: str, ident: str) -> bool:
    """التحقق من تجاوز الحد"""
    conf = RATE_LIMITS[kind]
    key = f"auth:{kind}:{ident}"
    count = cache.get(key, 0)
    return count >= conf['limit']

def incr_rate(kind: str, ident: str):
    """زيادة العداد"""
    conf = RATE_LIMITS[kind]
    key = f"auth:{kind}:{ident}"
    val = cache.get(key, 0)
    if val == 0:
        cache.set(key, 1, timeout=conf['window'])
    else:
        try:
            cache.incr(key)
        except Exception:
            cache.set(key, val + 1, timeout=conf['window'])
```

#### 6.4.2 Rate Limiting Middleware

```python
# في coriza/middleware.py
class RateLimitMiddleware(MiddlewareMixin):
    """وسيط تحديد معدل الطلبات"""
    
    _LIMIT = 100    # عدد الطلبات المسموحة
    _WINDOW = 3600  # نافذة زمنية (ساعة واحدة)
    
    def process_request(self, request):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            ip_address = self._get_client_ip(request)
            cache_key = f'rate_limit:{ip_address}'
            
            request_count = cache.get(cache_key, 0)
            if request_count >= self._LIMIT:
                logger.warning('Rate limit exceeded for IP: %s', ip_address)
                return HttpResponseForbidden('تم تجاوز حد الطلبات المسموح به')
            
            try:
                cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, self._WINDOW)
        
        return None
```

### 6.5 Security Headers

```python
# في coriza/middleware.py
class SecurityMiddleware(MiddlewareMixin):
    """وسيط الأمان — يُضيف Security Headers"""
    
    _SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Permitted-Cross-Domain-Policies': 'none',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    }
    
    def process_response(self, request, response):
        for header, value in self._SECURITY_HEADERS.items():
            response.setdefault(header, value)
        
        # X-XSS-Protection
        if getattr(settings, 'SECURE_BROWSER_XSS_FILTER', True):
            response.setdefault('X-XSS-Protection', '1; mode=block')
        
        # X-Frame-Options
        x_frame = getattr(settings, 'X_FRAME_OPTIONS', 'DENY')
        response.setdefault('X-Frame-Options', x_frame)
        
        return response
```

**الرؤوس الأمنية المُضافة:**
```http
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 6.6 Input Validation (التحقق من المدخلات)

#### 6.6.1 التحقق على مستوى النموذج

```python
# في osint_tools/serializers.py
class OSINTSessionFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = OSINTSession
        fields = ['tool', 'target', 'config', 'options']
    
    def validate_target(self, value):
        """التحقق من صحة الهدف"""
        if not value or not value.strip():
            raise serializers.ValidationError("الهدف مطلوب")
        
        # تنظيف المدخلات
        value = value.strip()
        
        # التحقق من الطول
        if len(value) > 500:
            raise serializers.ValidationError("الهدف طويل جداً")
        
        # منع الأحرف الخطيرة
        dangerous_chars = ['<', '>', '"', "'", ';', '|', '&', '$', '`']
        for char in dangerous_chars:
            if char in value:
                raise serializers.ValidationError(f"الحرف {char} غير مسموح")
        
        return value
```

#### 6.6.2 التحقق من JSON Fields

```python
# في osint_tools/models.py
class JSONValidationMixin:
    """Mixin لتدقيق الحقول من نوع JSONField"""
    
    json_fields = {}
    
    def clean(self):
        super().clean()
        errors = {}
        for field_name, allowed_types in self.json_fields.items():
            value = getattr(self, field_name, None)
            if value in (None, ''):
                continue
            
            if not isinstance(value, allowed_types):
                errors[field_name] = ValidationError("قيمة JSON غير صالحة.")
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        self.full_clean()  # التحقق قبل الحفظ
        return super().save(*args, **kwargs)
```

### 6.7 Command Injection Prevention

```python
# في osint_tools/utils.py
class OSINTToolRunner:
    def _build_command(self):
        """بناء أمر تشغيل الأداة بشكل آمن"""
        tool_path = os.path.join(settings.BASE_DIR, 'open_tool', self.tool.tool_path)
        executable = os.path.join(tool_path, self.tool.executable_name)
        
        # ✅ استخدام قائمة بدلاً من string
        # هذا يمنع command injection
        command = [
            'python',
            executable,
            self.target,  # يُعامل كمعامل واحد
            '--json'
        ]
        
        return command
    
    def _execute_command(self, command):
        """تنفيذ الأمر بشكل آمن"""
        result = subprocess.run(
            command,  # قائمة، ليس string
            cwd=tool_path,
            capture_output=True,
            text=True,
            timeout=self.tool.timeout,  # منع التعليق
            shell=False,  # ✅ مهم جداً - منع shell injection
            encoding='utf-8',
            errors='ignore'
        )
        
        return result
```

**مثال على الفرق:**
```python
# ❌ خطير - عرضة لـ Command Injection
command = f"python sherlock.py {target}"
subprocess.run(command, shell=True)  # خطير!

# إذا كان target = "john; rm -rf /"
# سيتم تنفيذ: python sherlock.py john; rm -rf /

# ✅ آمن - محمي من Command Injection
command = ['python', 'sherlock.py', target]
subprocess.run(command, shell=False)  # آمن!

# target = "john; rm -rf /" سيُعامل كمعامل واحد
```

### 6.8 Session Security

```python
# في settings.py
SESSION_COOKIE_SECURE = True  # HTTPS فقط
SESSION_COOKIE_HTTPONLY = True  # لا يمكن الوصول عبر JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'  # حماية CSRF
SESSION_COOKIE_AGE = 1209600  # أسبوعين
SESSION_SAVE_EVERY_REQUEST = False  # لتحسين الأداء
```

```python
# في dashboard/models.py
class UserSession(models.Model):
    """تتبع جلسات المستخدمين"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# في dashboard/views.py
@login_required
def terminate_session(request, session_id):
    """إنهاء جلسة محددة"""
    user_session = get_object_or_404(
        UserSession,
        id=session_id,
        user=request.user
    )
    
    # حذف الجلسة من Django
    Session.objects.filter(session_key=user_session.session_key).delete()
    
    # تحديث السجل
    user_session.is_active = False
    user_session.save()
    
    messages.success(request, 'تم إنهاء الجلسة بنجاح')
    return redirect('dashboard:security')
```

### 6.9 Logging & Monitoring

#### 6.9.1 Activity Logging

```python
# تسجيل كل نشاط مهم
OSINTActivityLog.objects.create(
    user=request.user,
    session=session,
    action='tool_run',
    description=f'تم تشغيل أداة {tool.name} للهدف {target}',
    details={
        'tool_id': tool.id,
        'tool_name': tool.name,
        'target': target,
        'case_id': case.id if case else None
    },
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT')
)
```

#### 6.9.2 Login Attempts Tracking

```python
# تتبع محاولات تسجيل الدخول
LoginAttempt.objects.create(
    user=user if user else None,
    email=email,
    ip_address=get_client_ip(request),
    user_agent=request.META.get('HTTP_USER_AGENT', ''),
    success=user is not None
)
```

#### 6.9.3 Error Monitoring (Sentry)

```python
# في settings.py
SENTRY_DSN = os.getenv('SENTRY_DSN', '')
if SENTRY_DSN and sentry_sdk:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,  # لا ترسل معلومات شخصية
        environment=os.getenv('SENTRY_ENVIRONMENT', 'development'),
    )
```

### 6.10 Best Practices المطبقة

✅ **Authentication:**
- Email-based authentication
- Strong password validators
- Email verification required
- Password reset with tokens

✅ **Authorization:**
- Clearance level system (L1-L4)
- Permission checks before tool execution
- User-specific data access

✅ **Input Validation:**
- Django ORM (prevents SQL injection)
- Form validation
- Serializer validation
- JSON field validation

✅ **Output Encoding:**
- Django templates (auto-escaping)
- JSON responses properly encoded

✅ **Session Management:**
- Secure cookies
- Session tracking
- Multiple session management

✅ **Rate Limiting:**
- Login attempts
- API requests
- Tool execution

✅ **Logging:**
- Activity logs
- Login attempts
- Error monitoring
- Audit trail

✅ **HTTPS:**
- SSL redirect in production
- HSTS headers
- Secure cookies

---


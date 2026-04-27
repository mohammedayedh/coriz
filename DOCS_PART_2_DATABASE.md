## 4. قاعدة البيانات والنماذج (Database & Models)

### 4.1 مخطط قاعدة البيانات (ERD - Entity Relationship Diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA OVERVIEW                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│      User        │ (authentication_user)
├──────────────────┤
│ id (PK)          │
│ email (UNIQUE)   │
│ username         │
│ password         │
│ is_verified      │
│ created_at       │
└──────────────────┘
        │
        │ 1:1
        ↓
┌──────────────────┐
│   UserProfile    │ (authentication_userprofile)
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ clearance_level  │ ← مهم جداً (L1, L2, L3, L4)
│ organization     │
│ bio              │
└──────────────────┘

        │ 1:N
        ↓
┌──────────────────┐
│InvestigationCase │ (osint_tools_investigationcase)
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ title            │
│ description      │
│ status           │ (open, in_progress, closed)
│ tags (JSON)      │
│ created_at       │
└──────────────────┘
        │
        │ 1:N
        ↓
┌──────────────────┐
│   OSINTTool      │ (osint_tools_osinttool)
├──────────────────┤
│ id (PK)          │
│ name             │
│ slug (UNIQUE)    │
│ tool_type        │
│ source_type      │
│ required_clearance│ ← يتحقق من UserProfile.clearance_level
│ status           │
│ tool_path        │
│ command_template │
│ config_schema    │
└──────────────────┘
        │
        │ 1:N
        ↓
┌──────────────────┐
│  OSINTSession    │ (osint_tools_osintsession)
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ tool_id (FK)     │
│ case_id (FK)     │ ← ربط بالقضية
│ target           │
│ status           │ (pending, running, completed, failed)
│ progress         │ (0-100)
│ celery_task_id   │
│ results_count    │
│ results_summary  │ (JSON)
│ started_at       │
│ completed_at     │
│ duration         │
│ error_message    │
└──────────────────┘
        │
        │ 1:N
        ↓
┌──────────────────┐
│   OSINTResult    │ (osint_tools_osintresult)
├──────────────────┤
│ id (PK)          │
│ session_id (FK)  │
│ result_type      │
│ title            │
│ description      │
│ url              │
│ raw_data (JSON)  │ ← البيانات الخام الكاملة
│ confidence       │ (high, medium, low)
│ confidence_score │ (0.0-1.0)
│ source           │
│ tags (JSON)      │
│ metadata (JSON)  │
│ discovered_at    │
└──────────────────┘

┌──────────────────┐
│   OSINTReport    │ (osint_tools_osintreport)
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ session_id (FK)  │
│ title            │
│ report_type      │
│ format           │ (pdf, html, json, csv)
│ file             │ ← مسار الملف
│ file_size        │
│ status           │
│ celery_task_id   │
│ generated_at     │
│ downloaded_count │
└──────────────────┘

┌──────────────────┐
│OSINTActivityLog  │ (osint_tools_osintactivitylog)
├──────────────────┤
│ id (PK)          │
│ user_id (FK)     │
│ session_id (FK)  │
│ action           │
│ description      │
│ details (JSON)   │
│ ip_address       │
│ user_agent       │
│ created_at       │
└──────────────────┘
```

### 4.2 النماذج الرئيسية (Core Models)

#### 4.2.1 نموذج المستخدم (User Model)

```python
class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    email = models.EmailField(unique=True)  # البريد كمعرف رئيسي
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # التحقق من البريد
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'  # تسجيل الدخول بالبريد
```

**دورة حياة بيانات المستخدم:**
1. **التسجيل:** إنشاء User + UserProfile
2. **التحقق:** EmailVerification → is_verified = True
3. **تسجيل الدخول:** LoginAttempt (تتبع المحاولات)
4. **التحديث:** تعديل البيانات الشخصية
5. **الحذف:** CASCADE على جميع البيانات المرتبطة

#### 4.2.2 نموذج الملف الشخصي (UserProfile Model)

```python
class UserProfile(models.Model):
    """ملف المستخدم الشخصي"""
    CLEARANCE_LEVELS = [
        ('L1', 'Level 1 - Public OSINT'),
        ('L2', 'Level 2 - Commercial APIs'),
        ('L3', 'Level 3 - Private & Leaked'),
        ('L4', 'Level 4 - Agency / Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clearance_level = models.CharField(max_length=2, default='L1')
    organization = models.CharField(max_length=150, blank=True)
    preferences = models.JSONField(default=dict)
```

**أهمية clearance_level:**
- يتحكم في الأدوات المتاحة للمستخدم
- يُفحص قبل تنفيذ أي أداة OSINT
- يحدد نوع البيانات التي يمكن الوصول إليها

#### 4.2.3 نموذج القضية التحقيقية (InvestigationCase Model)

```python
class InvestigationCase(models.Model):
    """نموذج القضايا الاستخباراتية"""
    STATUS_CHOICES = [
        ('open', 'مفتوحة'),
        ('in_progress', 'قيد التحقيق'),
        ('closed', 'مغلقة'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    tags = models.JSONField(default=list)  # ['terrorism', 'cybercrime']
    created_at = models.DateTimeField(auto_now_add=True)
```

**دورة حياة القضية:**
```
إنشاء (open) → قيد التحقيق (in_progress) → إغلاق (closed)
    ↓                    ↓                          ↓
  جلسات OSINT      جلسات + نتائج              تقارير نهائية
```

#### 4.2.4 نموذج أداة OSINT (OSINTTool Model)

```python
class OSINTTool(models.Model):
    """نموذج أدوات OSINT"""
    name = models.CharField(max_length=100)  # "Sherlock"
    slug = models.SlugField(unique=True)     # "sherlock"
    tool_type = models.CharField(max_length=20)  # 'username'
    source_type = models.CharField(max_length=20)  # 'open'
    required_clearance = models.CharField(max_length=2)  # 'L1'
    
    # إعدادات التنفيذ
    tool_path = models.CharField(max_length=200)  # "sherlock/"
    executable_name = models.CharField(max_length=100)  # "sherlock.py"
    command_template = models.TextField()  # "python {executable} {target}"
    
    # إحصائيات
    usage_count = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
```

**مثال على command_template:**
```python
"python {executable} {target} --timeout {timeout} --json"
# يتحول إلى:
"python sherlock.py john_doe --timeout 30 --json"
```

#### 4.2.5 نموذج جلسة OSINT (OSINTSession Model)

```python
class OSINTSession(models.Model):
    """نموذج جلسات OSINT"""
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('running', 'قيد التشغيل'),
        ('completed', 'مكتملة'),
        ('failed', 'فشلت'),
        ('cancelled', 'ملغية'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tool = models.ForeignKey(OSINTTool, on_delete=models.CASCADE)
    investigation_case = models.ForeignKey(InvestigationCase, null=True)
    target = models.CharField(max_length=500)  # الهدف
    status = models.CharField(max_length=20, default='pending')
    
    # معلومات التقدم
    progress = models.PositiveIntegerField(default=0)  # 0-100
    current_step = models.CharField(max_length=200)
    
    # النتائج
    results_count = models.PositiveIntegerField(default=0)
    results_summary = models.JSONField(default=dict)
    
    # التوقيت
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    
    # Celery
    celery_task_id = models.CharField(max_length=100, blank=True)
```

**دوال مساعدة مهمة:**
```python
def mark_running(self, task_id):
    """تحديث الحالة إلى running"""
    self.celery_task_id = task_id
    self.status = 'running'
    self.started_at = timezone.now()
    self.save()

def mark_completed(self):
    """تحديث الحالة إلى completed"""
    self.status = 'completed'
    self.progress = 100
    self.completed_at = timezone.now()
    self.duration = self.completed_at - self.started_at
    self.save()

def mark_failed(self, message):
    """تحديث الحالة إلى failed"""
    self.status = 'failed'
    self.error_message = message
    self.completed_at = timezone.now()
    self.save()
```

#### 4.2.6 نموذج نتيجة OSINT (OSINTResult Model)

```python
class OSINTResult(models.Model):
    """نموذج نتائج OSINT"""
    RESULT_TYPES = [
        ('email', 'بريد إلكتروني'),
        ('username', 'اسم مستخدم'),
        ('profile', 'ملف شخصي'),
        ('domain', 'نطاق'),
        ('ip', 'عنوان IP'),
        ('phone', 'رقم هاتف'),
        ('social_media', 'وسائل التواصل'),
        ('website', 'موقع ويب'),
        ('image', 'صورة'),
        ('document', 'مستند'),
        ('other', 'أخرى'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('high', 'عالي'),      # 0.7-1.0
        ('medium', 'متوسط'),   # 0.4-0.7
        ('low', 'منخفض'),      # 0.0-0.4
        ('unknown', 'غير معروف'),
    ]
    
    session = models.ForeignKey(OSINTSession, on_delete=models.CASCADE)
    result_type = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    
    # البيانات الخام
    raw_data = models.JSONField(default=dict)  # البيانات الكاملة
    
    # مستوى الثقة
    confidence = models.CharField(max_length=20)
    confidence_score = models.FloatField(default=0.0)  # 0.0-1.0
    
    # معلومات إضافية
    source = models.CharField(max_length=100)  # "Sherlock"
    tags = models.JSONField(default=list)  # ['twitter', 'verified']
    metadata = models.JSONField(default=dict)
    
    discovered_at = models.DateTimeField(auto_now_add=True)
```

**مثال على raw_data:**
```json
{
    "platform": "Twitter",
    "url": "https://twitter.com/john_doe",
    "found": true,
    "status_code": 200,
    "response_time": 1.23,
    "additional_info": {
        "followers": 1234,
        "verified": false
    }
}
```

### 4.3 العلاقات بين الجداول (Relationships)

```
User (1) ←→ (1) UserProfile
User (1) ←→ (N) InvestigationCase
User (1) ←→ (N) OSINTSession
User (1) ←→ (N) OSINTReport

InvestigationCase (1) ←→ (N) OSINTSession

OSINTTool (1) ←→ (N) OSINTSession
OSINTTool (1) ←→ (N) OSINTConfiguration

OSINTSession (1) ←→ (N) OSINTResult
OSINTSession (1) ←→ (N) OSINTReport
OSINTSession (1) ←→ (N) OSINTActivityLog
```

### 4.4 الفهارس (Indexes) والأداء

**الفهارس المهمة:**
```python
class Meta:
    indexes = [
        models.Index(fields=['user', 'status']),  # للاستعلامات السريعة
        models.Index(fields=['created_at']),      # للترتيب
        models.Index(fields=['tool', 'status']),  # لإحصائيات الأدوات
    ]
```

**استعلامات محسّنة:**
```python
# ✅ جيد - استخدام select_related
sessions = OSINTSession.objects.select_related('tool', 'user').all()

# ✅ جيد - استخدام prefetch_related
sessions = OSINTSession.objects.prefetch_related('results').all()

# ❌ سيء - N+1 queries
for session in OSINTSession.objects.all():
    print(session.tool.name)  # استعلام إضافي لكل جلسة
```

---


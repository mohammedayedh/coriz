# 📚 توثيق مشروع التخرج: منصة Coriza OSINT

## 🎓 معلومات المشروع

**اسم المشروع:** منصة Coriza لجمع المعلومات الاستخباراتية مفتوحة المصدر (OSINT Platform)

**نوع المشروع:** نظام ويب متكامل لإدارة وتنفيذ عمليات الاستخبارات مفتوحة المصدر

**التقنيات المستخدمة:**
- Backend: Django 5.2.6 (Python)
- Frontend: HTML5, CSS3, JavaScript
- Database: SQLite (Development) / PostgreSQL (Production)
- Cache & Message Broker: Redis
- Task Queue: Celery
- API: Django REST Framework
- Security: Django Security Middleware, CSRF Protection, Rate Limiting

---

## 📋 جدول المحتويات

1. [نظرة عامة على المشروع](#1-نظرة-عامة-على-المشروع)
2. [الهيكل المعماري للنظام](#2-الهيكل-المعماري-للنظام)
3. [دورة حياة البيانات (Data Lifecycle)](#3-دورة-حياة-البيانات-data-lifecycle)
4. [قاعدة البيانات والنماذج](#4-قاعدة-البيانات-والنماذج)
5. [التطبيقات (Apps) والوظائف](#5-التطبيقات-apps-والوظائف)
6. [نظام الأمان والحماية](#6-نظام-الأمان-والحماية)
7. [واجهات برمجة التطبيقات (APIs)](#7-واجهات-برمجة-التطبيقات-apis)
8. [نظام المهام غير المتزامنة (Celery)](#8-نظام-المهام-غير-المتزامنة-celery)
9. [دليل الاستخدام](#9-دليل-الاستخدام)
10. [التحديات والحلول](#10-التحديات-والحلول)

---

## 1. نظرة عامة على المشروع

### 1.1 فكرة المشروع

منصة **Coriza OSINT** هي نظام ويب متكامل مصمم لتسهيل عمليات جمع وتحليل المعلومات الاستخباراتية من المصادر المفتوحة (Open Source Intelligence). 

**الهدف الرئيسي:** توفير بيئة آمنة ومنظمة للمحللين الأمنيين والباحثين لتنفيذ عمليات OSINT بكفاءة عالية.

### 1.2 المشكلة التي يحلها المشروع

1. **تشتت الأدوات:** أدوات OSINT متفرقة ويصعب إدارتها
2. **عدم التنظيم:** صعوبة تتبع التحقيقات والنتائج
3. **نقص الأمان:** عدم وجود نظام صلاحيات محكم
4. **غياب التوثيق:** صعوبة توليد تقارير احترافية

### 1.3 الحل المقترح

منصة موحدة تجمع:
- ✅ إدارة مركزية لأدوات OSINT
- ✅ نظام قضايا تحقيقية (Case Management)
- ✅ تتبع دقيق لدورة حياة البيانات
- ✅ نظام صلاحيات متعدد المستويات (L1-L4)
- ✅ توليد تقارير احترافية تلقائياً
- ✅ واجهات برمجية (REST APIs) للتكامل

---

## 2. الهيكل المعماري للنظام

### 2.1 معمارية النظام (System Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface Layer                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │Dashboard │  │  OSINT   │  │   API    │   │
│  │  Portal  │  │   Panel  │  │  Tools   │  │ Clients  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer (Django)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │   Main   │  │Dashboard │  │   API    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            OSINT Tools Engine                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Models  │  │  Views   │  │Serializer│  │  Utils   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Celery  │  │  Files   │   │
│  │ /SQLite  │  │  Cache   │  │  Queue   │  │ Storage  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 مكونات النظام الرئيسية

| المكون | الوصف | التقنية |
|--------|-------|---------|
| **Web Server** | خادم الويب الرئيسي | Django 5.2.6 + Gunicorn |
| **Database** | قاعدة البيانات | PostgreSQL / SQLite |
| **Cache** | التخزين المؤقت | Redis |
| **Task Queue** | معالجة المهام غير المتزامنة | Celery + Redis |
| **Static Files** | الملفات الثابتة | Django Static Files |
| **Media Storage** | تخزين الملفات المرفوعة | File System / S3 |

---

## 3. دورة حياة البيانات (Data Lifecycle)

### 3.1 مراحل دورة حياة البيانات في النظام

```
┌──────────────────────────────────────────────────────────────┐
│                  DATA LIFECYCLE IN CORIZA                     │
└──────────────────────────────────────────────────────────────┘

1. DATA CREATION (إنشاء البيانات)
   ↓
2. DATA VALIDATION (التحقق من صحة البيانات)
   ↓
3. DATA STORAGE (تخزين البيانات)
   ↓
4. DATA PROCESSING (معالجة البيانات)
   ↓
5. DATA ANALYSIS (تحليل البيانات)
   ↓
6. DATA PRESENTATION (عرض البيانات)
   ↓
7. DATA ARCHIVING (أرشفة البيانات)
   ↓
8. DATA DELETION (حذف البيانات)
```

### 3.2 دورة حياة بيانات جلسة OSINT (تفصيلية)

#### المرحلة 1: إنشاء البيانات (Data Creation)

**الخطوة 1.1: طلب المستخدم**
```python
# المستخدم يطلب تشغيل أداة OSINT
POST /osint/tools/sherlock/run/
{
    "target": "john_doe",
    "case_id": 5,
    "config_id": 2,
    "options": {"timeout": 60}
}
```

**الخطوة 1.2: إنشاء سجل الجلسة**
```python
# في views.py - run_tool()
session = OSINTSession.objects.create(
    user=request.user,              # المستخدم المنفذ
    tool=tool,                      # الأداة المستخدمة
    target="john_doe",              # الهدف
    investigation_case=case,        # القضية المرتبطة
    config=config_data,             # الإعدادات
    options=options,                # الخيارات
    status='pending'                # الحالة الأولية
)
```

**البيانات المُنشأة:**
- `OSINTSession` (الجلسة الرئيسية)
- `OSINTActivityLog` (سجل النشاط)

#### المرحلة 2: التحقق من صحة البيانات (Data Validation)

**الخطوة 2.1: التحقق على مستوى النموذج**
```python
# في models.py - JSONValidationMixin
def clean(self):
    super().clean()
    errors = {}
    for field_name, allowed_types in self.json_fields.items():
        value = getattr(self, field_name, None)
        if value not in (None, ''):
            if not isinstance(value, allowed_types):
                errors[field_name] = ValidationError("قيمة JSON غير صالحة.")
    if errors:
        raise ValidationError(errors)
```

**الخطوة 2.2: التحقق من الصلاحيات**
```python
# التحقق من مستوى التصريح الأمني
user_clearance = request.user.profile.clearance_level  # مثال: 'L2'
tool_clearance = tool.required_clearance               # مثال: 'L3'

if user_clearance < tool_clearance:
    return JsonResponse({'error': 'صلاحيات غير كافية'}, status=403)
```

**الخطوة 2.3: التحقق من معدل الطلبات (Rate Limiting)**
```python
# في middleware.py - RateLimitMiddleware
cache_key = f'rate_limit:{ip_address}'
request_count = cache.get(cache_key, 0)

if request_count >= LIMIT:
    return HttpResponseForbidden('تم تجاوز حد الطلبات')
```

#### المرحلة 3: تخزين البيانات (Data Storage)

**الخطوة 3.1: حفظ في قاعدة البيانات**
```python
# حفظ الجلسة
session.save()  # يُنشئ سجل في جدول osint_tools_osintsession

# البيانات المخزنة:
# - id: معرف فريد
# - user_id: معرف المستخدم
# - tool_id: معرف الأداة
# - target: الهدف
# - status: 'pending'
# - created_at: وقت الإنشاء
# - config: JSON
# - options: JSON
```

**الخطوة 3.2: جدولة المهمة في Celery**
```python
# جدولة المهمة غير المتزامنة
task = run_osint_tool.delay(session.id)
session.celery_task_id = task.id
session.save(update_fields=['celery_task_id', 'updated_at'])
```

**الخطوة 3.3: تسجيل النشاط**
```python
OSINTActivityLog.objects.create(
    user=request.user,
    session=session,
    action='tool_run',
    description=f'تم جدولة تشغيل أداة {tool.name}',
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT'),
    details={'session_id': session.id}
)
```

#### المرحلة 4: معالجة البيانات (Data Processing)

**الخطوة 4.1: تنفيذ المهمة في Celery Worker**
```python
# في tasks.py - run_osint_tool()
@shared_task(bind=True)
def run_osint_tool(self, session_id):
    session = OSINTSession.objects.get(pk=session_id)
    
    # تحديث الحالة إلى "running"
    session.mark_running(task_id=self.request.id)
    
    # تشغيل الأداة
    runner = OSINTToolRunner(session)
    runner.run()
```

**الخطوة 4.2: تنفيذ الأداة الخارجية**
```python
# في utils.py - OSINTToolRunner.run()
def run(self):
    # بناء الأمر
    command = self._build_command()  # ['python', 'sherlock.py', 'john_doe']
    
    # تنفيذ الأمر
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=self.tool.timeout
    )
    
    # معالجة المخرجات
    self._process_results(result)
```

**الخطوة 4.3: استخراج النتائج**
```python
# معالجة مخرجات JSON
data = json.loads(result.stdout)

# إنشاء سجلات النتائج
for item in data['results']:
    OSINTResult.objects.create(
        session=self.session,
        result_type='social_media',
        title=item['platform'],
        url=item['url'],
        confidence='high' if item['found'] else 'low',
        raw_data=item,
        source=self.tool.name
    )
```

**تحديث البيانات:**
- `OSINTSession.status` → 'running' → 'completed'
- `OSINTSession.progress` → 0% → 100%
- `OSINTSession.results_count` → عدد النتائج
- إنشاء سجلات `OSINTResult` متعددة

#### المرحلة 5: تحليل البيانات (Data Analysis)

**الخطوة 5.1: حساب الإحصائيات**
```python
# حساب ملخص النتائج
results_summary = {
    'total': results.count(),
    'by_type': results.values('result_type').annotate(count=Count('id')),
    'by_confidence': results.values('confidence').annotate(count=Count('id')),
    'high_confidence_count': results.filter(confidence='high').count()
}

session.results_summary = results_summary
session.save()
```

**الخطوة 5.2: تصنيف النتائج**
```python
# تصنيف حسب مستوى الثقة
high_confidence = results.filter(confidence='high')
medium_confidence = results.filter(confidence='medium')
low_confidence = results.filter(confidence='low')
```

#### المرحلة 6: عرض البيانات (Data Presentation)

**الخطوة 6.1: عرض في واجهة الويب**
```python
# في views.py - session_detail()
def session_detail(request, session_id):
    session = get_object_or_404(OSINTSession, id=session_id, user=request.user)
    results = OSINTResult.objects.filter(session=session)
    
    context = {
        'session': session,
        'results': results,
        'stats': session.results_summary
    }
    return render(request, 'osint_tools/session_detail.html', context)
```

**الخطوة 6.2: توفير عبر API**
```python
# REST API Endpoint
GET /osint/api/sessions/123/
Response:
{
    "id": 123,
    "tool_name": "Sherlock",
    "target": "john_doe",
    "status": "completed",
    "results_count": 45,
    "progress": 100
}
```

**الخطوة 6.3: توليد التقارير**
```python
# إنشاء تقرير
report = OSINTReport.objects.create(
    user=request.user,
    session=session,
    title=f"تقرير {session.tool.name}",
    report_type='detailed',
    format='html'
)

# جدولة توليد التقرير
task = generate_osint_report.delay(report.id)
```

#### المرحلة 7: أرشفة البيانات (Data Archiving)

**الخطوة 7.1: تصدير البيانات**
```python
# تصدير إلى JSON
GET /osint/ajax/export-results/123/?format=json

# تصدير إلى CSV
GET /osint/ajax/export-results/123/?format=csv
```

**الخطوة 7.2: حفظ التقارير**
```python
# حفظ التقرير كملف
report.file.save(
    f"report_{report.id}.html",
    ContentFile(html_content.encode('utf-8'))
)
```

#### المرحلة 8: حذف البيانات (Data Deletion)

**الخطوة 8.1: الحذف المتسلسل (Cascade Delete)**
```python
# عند حذف جلسة، يتم حذف:
# - جميع النتائج المرتبطة (OSINTResult)
# - جميع التقارير المرتبطة (OSINTReport)
# - سجلات الأنشطة (OSINTActivityLog)

session.delete()  # CASCADE DELETE
```

**الخطوة 8.2: حذف الملفات**
```python
# حذف ملفات التقارير
if report.file:
    report.file.delete()  # حذف الملف من النظام

# حذف ملفات السجلات
if session.log_file:
    session.log_file.delete()
```

### 3.3 مخطط تدفق البيانات (Data Flow Diagram)

```
[User Request] 
    ↓
[Django View: run_tool()]
    ↓
[Create OSINTSession] → [Database: INSERT]
    ↓
[Queue Celery Task] → [Redis: LPUSH]
    ↓
[Celery Worker: run_osint_tool()]
    ↓
[OSINTToolRunner.run()]
    ↓
[Execute External Tool] → [subprocess]
    ↓
[Parse Output]
    ↓
[Create OSINTResult(s)] → [Database: INSERT × N]
    ↓
[Update OSINTSession] → [Database: UPDATE]
    ↓
[Generate Report (Optional)]
    ↓
[OSINTReport] → [File System: WRITE]
    ↓
[Display to User] → [HTTP Response]
```

---


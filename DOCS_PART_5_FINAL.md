## 7. واجهات برمجة التطبيقات (REST APIs)

### 7.1 نظرة عامة على API

```
API Structure:
/api/v1/
├── users/              # إدارة المستخدمين
├── posts/              # المنشورات
├── categories/         # الفئات
├── comments/           # التعليقات
├── keys/               # مفاتيح API
├── webhooks/           # Webhooks
├── versions/           # إصدارات API
└── endpoints/          # نقاط النهاية

/osint/api/
├── tools/              # أدوات OSINT
├── sessions/           # الجلسات
├── results/            # النتائج
├── reports/            # التقارير
├── configurations/     # الإعدادات
└── stats/              # الإحصائيات
```

### 7.2 Authentication

```python
# في settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

**استخدام Token Authentication:**
```bash
# الحصول على Token
POST /api/v1/auth/token/
{
    "email": "user@example.com",
    "password": "password123"
}

Response:
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}

# استخدام Token
GET /osint/api/tools/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 7.3 أمثلة على API Endpoints

#### 7.3.1 OSINT Tools API

```bash
# قائمة الأدوات
GET /osint/api/tools/
Response:
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Sherlock",
            "slug": "sherlock",
            "description": "أداة للبحث عن أسماء المستخدمين",
            "tool_type": "username",
            "status": "active",
            "icon": "fas fa-user-secret",
            "usage_count": 150,
            "success_rate": 85.5
        }
    ]
}

# تفاصيل أداة
GET /osint/api/tools/sherlock/
Response:
{
    "id": 1,
    "name": "Sherlock",
    "slug": "sherlock",
    "description": "أداة للبحث عن أسماء المستخدمين في مواقع التواصل",
    "tool_type": "username",
    "source_type": "open",
    "required_clearance": "L1",
    "status": "active",
    "usage_count": 150,
    "success_rate": 85.5
}
```

#### 7.3.2 Sessions API

```bash
# إنشاء جلسة جديدة
POST /osint/api/sessions/
{
    "tool": 1,
    "target": "john_doe",
    "config": {},
    "options": {"timeout": 60}
}

Response:
{
    "id": 123,
    "tool": 1,
    "tool_name": "Sherlock",
    "target": "john_doe",
    "status": "pending",
    "progress": 0,
    "created_at": "2026-04-17T10:30:00Z"
}

# تتبع حالة الجلسة
GET /osint/api/sessions/123/
Response:
{
    "id": 123,
    "tool_name": "Sherlock",
    "target": "john_doe",
    "status": "running",
    "progress": 45,
    "current_step": "جاري البحث في Twitter...",
    "results_count": 12,
    "started_at": "2026-04-17T10:30:05Z"
}
```

#### 7.3.3 Results API

```bash
# قائمة النتائج
GET /osint/api/results/?session=123
Response:
{
    "count": 45,
    "results": [
        {
            "id": 1001,
            "session": 123,
            "session_tool": "Sherlock",
            "result_type": "social_media",
            "title": "حساب Twitter: john_doe",
            "url": "https://twitter.com/john_doe",
            "confidence": "high",
            "confidence_score": 0.95,
            "source": "Sherlock",
            "discovered_at": "2026-04-17T10:31:15Z"
        }
    ]
}
```

---

## 8. نظام المهام غير المتزامنة (Celery)

### 8.1 معمارية Celery

```
┌──────────────┐
│ Django App   │
│              │
│ run_tool()   │ ──┐
└──────────────┘   │
                   │ task.delay()
                   ↓
┌──────────────────────────────┐
│        Redis Broker          │
│  (Message Queue)             │
│                              │
│  Queue: osint_tools          │
│  Queue: osint_reports        │
└──────────────────────────────┘
                   │
                   │ LPOP
                   ↓
┌──────────────────────────────┐
│      Celery Worker           │
│                              │
│  run_osint_tool()            │
│  generate_osint_report()     │
└──────────────────────────────┘
                   │
                   │ Result
                   ↓
┌──────────────────────────────┐
│     Redis Backend            │
│  (Results Storage)           │
└──────────────────────────────┘
```

### 8.2 إعدادات Celery

```python
# في coriza/celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coriza.settings')

app = Celery('coriza')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# في settings.py
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/1')
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 1800  # 30 دقيقة
CELERY_TASK_SOFT_TIME_LIMIT = 1200  # 20 دقيقة
CELERY_TASK_DEFAULT_QUEUE = 'osint_tools'
CELERY_TASK_ROUTES = {
    'osint_tools.tasks.run_osint_tool': {'queue': 'osint_tools'},
    'osint_tools.tasks.generate_osint_report': {'queue': 'osint_reports'},
}
```

### 8.3 تشغيل Celery Worker

```bash
# تشغيل Worker
celery -A coriza worker -l info

# تشغيل Worker مع صف محدد
celery -A coriza worker -Q osint_tools -l info

# تشغيل Worker مع Concurrency
celery -A coriza worker -l info --concurrency=4

# تشغيل Beat (للمهام المجدولة)
celery -A coriza beat -l info
```

### 8.4 مراقبة المهام

```bash
# Flower - واجهة مراقبة Celery
pip install flower
celery -A coriza flower

# الوصول عبر: http://localhost:5555
```

---

## 9. دليل الاستخدام (User Guide)

### 9.1 التسجيل وتسجيل الدخول

**الخطوة 1: التسجيل**
1. اذهب إلى `/auth/register/`
2. املأ النموذج:
   - البريد الإلكتروني
   - اسم المستخدم
   - الاسم الأول والأخير
   - كلمة المرور
3. اضغط "تسجيل"
4. ستصلك رسالة تحقق على البريد

**الخطوة 2: تفعيل الحساب**
1. افتح البريد الإلكتروني
2. اضغط على رابط التفعيل
3. سيتم تفعيل حسابك

**الخطوة 3: تسجيل الدخول**
1. اذهب إلى `/auth/login/`
2. أدخل البريد وكلمة المرور
3. اضغط "تسجيل الدخول"

### 9.2 إنشاء قضية تحقيقية

**الخطوة 1: إنشاء القضية**
1. اذهب إلى `/osint/cases/`
2. اضغط "قضية جديدة"
3. املأ البيانات:
   - عنوان القضية
   - وصف القضية
   - العلامات (Tags)
4. اضغط "إنشاء"

**الخطوة 2: ربط الجلسات بالقضية**
- عند تشغيل أي أداة، اختر القضية من القائمة المنسدلة

### 9.3 تشغيل أداة OSINT

**الخطوة 1: اختيار الأداة**
1. اذهب إلى `/osint/tools/`
2. تصفح الأدوات المتاحة
3. اضغط على الأداة المطلوبة

**الخطوة 2: إعداد الأداة**
1. أدخل الهدف (Target):
   - اسم مستخدم
   - بريد إلكتروني
   - نطاق
   - عنوان IP
2. اختر القضية (اختياري)
3. اختر الإعدادات (اختياري)

**الخطوة 3: تشغيل الأداة**
1. اضغط "تشغيل الأداة"
2. ستُنشأ جلسة جديدة
3. تابع التقدم في الوقت الفعلي

**الخطوة 4: عرض النتائج**
1. بعد اكتمال الجلسة
2. اذهب إلى صفحة الجلسة
3. تصفح النتائج المكتشفة

### 9.4 توليد تقرير

**الخطوة 1: طلب التقرير**
1. من صفحة الجلسة
2. اضغط "إنشاء تقرير"
3. اختر:
   - نوع التقرير (ملخص/مفصل/تنفيذي/تقني)
   - الصيغة (HTML/PDF/JSON/CSV)
   - الخيارات (تضمين البيانات الخام، الرسوم البيانية)

**الخطوة 2: تحميل التقرير**
1. انتظر حتى يكتمل التوليد
2. اذهب إلى `/osint/reports/`
3. اضغط "تحميل"

---

## 10. التحديات والحلول

### 10.1 التحديات التقنية

#### التحدي 1: معالجة المهام الطويلة
**المشكلة:** أدوات OSINT قد تستغرق وقتاً طويلاً (دقائق أو ساعات)

**الحل:**
- استخدام Celery للمعالجة غير المتزامنة
- تتبع التقدم في الوقت الفعلي
- إمكانية إلغاء المهام

#### التحدي 2: تنوع مخرجات الأدوات
**المشكلة:** كل أداة لها صيغة مخرجات مختلفة

**الحل:**
- نظام معالجة مرن (`_process_results()`)
- دوال معالجة متخصصة لكل نوع أداة
- حفظ البيانات الخام في `raw_data`

#### التحدي 3: أمان تنفيذ الأوامر الخارجية
**المشكلة:** تنفيذ أوامر خارجية قد يكون خطيراً

**الحل:**
- استخدام `subprocess.run()` مع `shell=False`
- تمرير الأوامر كقائمة وليس string
- تحديد timeout لمنع التعليق
- التحقق من المدخلات

#### التحدي 4: إدارة الصلاحيات
**المشكلة:** بعض الأدوات حساسة ولا يجب أن تكون متاحة للجميع

**الحل:**
- نظام Clearance Levels (L1-L4)
- التحقق من الصلاحيات قبل التنفيذ
- تسجيل كل العمليات

### 10.2 التحديات في دورة حياة البيانات

#### التحدي 1: تتبع البيانات عبر المراحل
**المشكلة:** البيانات تمر بمراحل متعددة

**الحل:**
- نموذج `OSINTActivityLog` لتسجيل كل مرحلة
- حقول `status` و `progress` في `OSINTSession`
- timestamps دقيقة (`created_at`, `started_at`, `completed_at`)

#### التحدي 2: سلامة البيانات
**المشكلة:** ضمان عدم فقدان البيانات

**الحل:**
- استخدام transactions في Django
- حفظ البيانات الخام (`raw_data`)
- نسخ احتياطية دورية

#### التحدي 3: أداء الاستعلامات
**المشكلة:** استعلامات بطيئة مع كثرة البيانات

**الحل:**
- استخدام `select_related()` و `prefetch_related()`
- إضافة indexes على الحقول المستخدمة في الاستعلامات
- Pagination للنتائج

---

## 11. الخلاصة والتوصيات

### 11.1 ما تم إنجازه

✅ **نظام متكامل لإدارة عمليات OSINT:**
- 5 تطبيقات Django متكاملة
- 30+ نموذج قاعدة بيانات
- 100+ view و endpoint
- نظام مصادقة وتفويض محكم
- معالجة غير متزامنة للمهام
- توليد تقارير احترافية

✅ **دورة حياة بيانات محكمة:**
- تتبع كامل من الإنشاء إلى الحذف
- تسجيل شامل لكل العمليات
- حفظ البيانات الخام والمعالجة
- أرشفة وتصدير

✅ **أمان متعدد الطبقات:**
- 6 طبقات أمان
- نظام صلاحيات متقدم
- Rate limiting
- Input validation
- Audit trail

### 11.2 التوصيات للتطوير المستقبلي

#### قصيرة المدى (1-3 أشهر):
1. إضافة المزيد من أدوات OSINT
2. تحسين واجهة المستخدم
3. إضافة إشعارات فورية (WebSockets)
4. تحسين نظام التقارير (PDF generation)

#### متوسطة المدى (3-6 أشهر):
1. نظام تعاون بين المستخدمين
2. API متقدمة مع GraphQL
3. تحليلات متقدمة (AI/ML)
4. تكامل مع أدوات خارجية

#### طويلة المدى (6-12 شهر):
1. نظام موزع (Distributed System)
2. تحليل البيانات الضخمة (Big Data)
3. تطبيق موبايل
4. نظام تنبيهات ذكي

### 11.3 الدروس المستفادة

1. **أهمية التخطيط:** تصميم قاعدة البيانات جيداً من البداية يوفر الكثير من الوقت
2. **الأمان أولاً:** تطبيق الأمان من البداية أسهل من إضافته لاحقاً
3. **التوثيق مهم:** توثيق الكود يسهل الصيانة والتطوير
4. **الاختبار ضروري:** الاختبارات تكشف المشاكل مبكراً
5. **المرونة مطلوبة:** النظام يجب أن يكون قابلاً للتوسع

---

## 12. المراجع والمصادر

### 12.1 التوثيق الرسمي
- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Celery Documentation: https://docs.celeryproject.org/
- Redis Documentation: https://redis.io/documentation

### 12.2 أدوات OSINT
- Sherlock: https://github.com/sherlock-project/sherlock
- theHarvester: https://github.com/laramies/theHarvester
- SpiderFoot: https://github.com/smicallef/spiderfoot

### 12.3 الأمان
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/

---

## 13. الملاحق

### 13.1 مخطط قاعدة البيانات الكامل
(انظر DOCS_PART_2_DATABASE.md)

### 13.2 قائمة API Endpoints الكاملة
(انظر docs/ROUTES.md)

### 13.3 أمثلة على الاستخدام
(انظر QUICK_START_GUIDE.md)

---

**تم إعداد هذا التوثيق بواسطة:** فريق تطوير Coriza OSINT Platform
**التاريخ:** 17 أبريل 2026
**الإصدار:** 1.0.0

---


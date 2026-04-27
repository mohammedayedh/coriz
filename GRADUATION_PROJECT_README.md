# 🎓 مشروع التخرج: منصة Coriza OSINT

## 📚 دليل التوثيق الشامل

هذا المشروع عبارة عن منصة متكاملة لجمع وتحليل المعلومات الاستخباراتية مفتوحة المصدر (OSINT Platform).

---

## 📂 ملفات التوثيق

تم تقسيم التوثيق إلى 5 أجزاء رئيسية لسهولة القراءة:

### 1️⃣ التوثيق الرئيسي
📄 **GRADUATION_PROJECT_DOCUMENTATION.md**
- نظرة عامة على المشروع
- الهيكل المعماري
- دورة حياة البيانات (Data Lifecycle) - مفصلة جداً
- مخططات تدفق البيانات

### 2️⃣ قاعدة البيانات والنماذج
📄 **DOCS_PART_2_DATABASE.md**
- مخطط قاعدة البيانات (ERD)
- شرح تفصيلي لكل نموذج (Model)
- العلاقات بين الجداول
- أمثلة على الاستعلامات

### 3️⃣ التطبيقات والوظائف
📄 **DOCS_PART_3_APPS.md**
- شرح تفصيلي لكل تطبيق (App)
- تدفق تنفيذ أدوات OSINT
- نظام التقارير
- أمثلة على الكود

### 4️⃣ الأمان والحماية
📄 **DOCS_PART_4_SECURITY.md**
- طبقات الأمان (6 طبقات)
- نظام الصلاحيات (Clearance Levels)
- حماية CSRF
- Rate Limiting
- Input Validation
- Command Injection Prevention

### 5️⃣ APIs والخلاصة
📄 **DOCS_PART_5_FINAL.md**
- واجهات REST API
- نظام Celery
- دليل الاستخدام
- التحديات والحلول
- التوصيات المستقبلية

---

## 🎯 النقاط الرئيسية للمشروع

### ✨ المزايا الأساسية

1. **نظام إدارة قضايا تحقيقية (Case Management)**
   - إنشاء وتتبع القضايا
   - ربط الجلسات بالقضايا
   - تنظيم العمل

2. **محرك أدوات OSINT قابل للتوسع**
   - دعم أدوات متعددة
   - تنفيذ غير متزامن (Celery)
   - تتبع التقدم في الوقت الفعلي

3. **نظام صلاحيات متعدد المستويات**
   - L1: مصادر عامة
   - L2: واجهات تجارية
   - L3: بيانات خاصة
   - L4: جهات حكومية

4. **توليد تقارير احترافية**
   - HTML, PDF, JSON, CSV
   - تقارير ملخصة ومفصلة
   - تخصيص المحتوى

5. **واجهات برمجية (REST APIs)**
   - Token Authentication
   - Pagination
   - Filtering & Search

---

## 🔄 دورة حياة البيانات (مختصرة)

```
1. إنشاء البيانات (Data Creation)
   ↓
2. التحقق من الصحة (Data Validation)
   ↓
3. التخزين (Data Storage)
   ↓
4. المعالجة (Data Processing)
   ↓
5. التحليل (Data Analysis)
   ↓
6. العرض (Data Presentation)
   ↓
7. الأرشفة (Data Archiving)
   ↓
8. الحذف (Data Deletion)
```

**للتفاصيل الكاملة:** انظر القسم 3 في GRADUATION_PROJECT_DOCUMENTATION.md

---

## 🏗️ الهيكل المعماري

```
┌─────────────────────────────────────────┐
│         User Interface Layer            │
│  (Web Portal + Dashboard + API)         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Application Layer (Django)         │
│  (Auth + Main + Dashboard + OSINT + API)│
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│       Business Logic Layer              │
│  (Models + Views + Serializers + Utils) │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│           Data Layer                    │
│  (PostgreSQL + Redis + Celery + Files)  │
└─────────────────────────────────────────┘
```

---

## 📊 إحصائيات المشروع

| المكون | العدد |
|--------|-------|
| **التطبيقات (Apps)** | 5 |
| **النماذج (Models)** | 30+ |
| **العروض (Views)** | 100+ |
| **API Endpoints** | 50+ |
| **Celery Tasks** | 2 |
| **Middleware** | 4 |
| **أسطر الكود** | ~10,000 |

---

## 🔐 الأمان

### طبقات الأمان المطبقة:

1. **Network Security**
   - HTTPS Enforcement
   - HSTS Headers

2. **Application Security**
   - CSRF Protection
   - XSS Protection
   - Clickjacking Protection

3. **Authentication & Authorization**
   - Email-based Auth
   - Clearance Levels (L1-L4)
   - Session Management

4. **Rate Limiting**
   - Login Attempts
   - API Requests

5. **Data Security**
   - Input Validation
   - SQL Injection Prevention
   - Command Injection Prevention

6. **Monitoring & Logging**
   - Activity Logs
   - Login Attempts Tracking
   - Error Monitoring (Sentry)

---

## 🚀 التقنيات المستخدمة

### Backend
- **Framework:** Django 5.2.6
- **Language:** Python 3.11+
- **Database:** PostgreSQL / SQLite
- **Cache:** Redis
- **Task Queue:** Celery
- **API:** Django REST Framework

### Frontend
- **HTML5** + **CSS3** + **JavaScript**
- **Bootstrap** (للتصميم)
- **AJAX** (للتفاعل)

### DevOps
- **Web Server:** Gunicorn
- **Reverse Proxy:** Nginx (Production)
- **Monitoring:** Sentry
- **Logging:** Python Logging

---

## 📈 مخطط تدفق البيانات الرئيسي

```
[User Request]
    ↓
[Django View]
    ↓
[Create OSINTSession] → [Database]
    ↓
[Queue Celery Task] → [Redis]
    ↓
[Celery Worker]
    ↓
[Execute OSINT Tool] → [subprocess]
    ↓
[Parse Results]
    ↓
[Create OSINTResult(s)] → [Database]
    ↓
[Update OSINTSession] → [Database]
    ↓
[Generate Report (Optional)]
    ↓
[Display to User]
```

---

## 🎓 للمقيّمين والأساتذة

### النقاط المهمة للتقييم:

1. **التصميم المعماري:**
   - معمارية متعددة الطبقات (Multi-tier Architecture)
   - فصل واضح بين المكونات (Separation of Concerns)
   - قابلية التوسع (Scalability)

2. **دورة حياة البيانات:**
   - تتبع كامل من الإنشاء إلى الحذف
   - تسجيل شامل (Audit Trail)
   - سلامة البيانات (Data Integrity)

3. **الأمان:**
   - 6 طبقات أمان
   - Best Practices مطبقة
   - OWASP Top 10 معالجة

4. **جودة الكود:**
   - Clean Code Principles
   - DRY (Don't Repeat Yourself)
   - SOLID Principles
   - توثيق شامل

5. **الابتكار:**
   - نظام Clearance Levels فريد
   - معالجة غير متزامنة
   - تتبع التقدم في الوقت الفعلي

---

## 📖 كيفية قراءة التوثيق

### للمبتدئين:
1. ابدأ بـ **GRADUATION_PROJECT_DOCUMENTATION.md** (القسم 1 و 2)
2. ثم **DOCS_PART_2_DATABASE.md** (لفهم البيانات)
3. ثم **DOCS_PART_5_FINAL.md** (دليل الاستخدام)

### للمتقدمين:
1. **DOCS_PART_3_APPS.md** (تفاصيل التطبيقات)
2. **DOCS_PART_4_SECURITY.md** (الأمان)
3. **DOCS_PART_5_FINAL.md** (APIs والتحديات)

### للمقيّمين:
1. **GRADUATION_PROJECT_DOCUMENTATION.md** (القسم 3: دورة حياة البيانات)
2. **DOCS_PART_4_SECURITY.md** (نظام الأمان)
3. **DOCS_PART_5_FINAL.md** (الخلاصة والتوصيات)

---

## 🎯 أهداف المشروع (تم تحقيقها)

✅ بناء منصة متكاملة لعمليات OSINT
✅ تطبيق دورة حياة بيانات محكمة
✅ نظام أمان متعدد الطبقات
✅ معالجة غير متزامنة للمهام
✅ واجهات برمجية (REST APIs)
✅ توليد تقارير احترافية
✅ نظام صلاحيات متقدم
✅ تسجيل شامل للأنشطة

---

## 📞 معلومات الاتصال

**اسم المشروع:** Coriza OSINT Platform
**النوع:** مشروع تخرج
**التاريخ:** 2026
**الإصدار:** 1.0.0

---

## 📝 ملاحظات مهمة

1. **هذا المشروع تعليمي:** مصمم لأغراض التعلم والتقييم الأكاديمي
2. **الأمان:** تم تطبيق أفضل الممارسات الأمنية
3. **التوثيق:** شامل ومفصل لتسهيل الفهم والتقييم
4. **الكود:** نظيف ومنظم ومُعلّق
5. **قابل للتوسع:** يمكن إضافة المزيد من الأدوات والميزات

---

## 🏆 الإنجازات الرئيسية

1. ✅ نظام متكامل يعمل بكفاءة
2. ✅ دورة حياة بيانات موثقة بالتفصيل
3. ✅ أمان متعدد الطبقات
4. ✅ معمارية قابلة للتوسع
5. ✅ توثيق شامل ومفصل

---

**🎓 نتمنى لكم قراءة ممتعة ومفيدة!**


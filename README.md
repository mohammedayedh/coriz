# 🔍 Coriza OSINT Platform

<div align="center">

![Coriza Logo](https://img.shields.io/badge/Coriza-OSINT%20Platform-6366f1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.2-green?style=for-the-badge&logo=django)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**منصة استخبارات مفتوحة المصدر (OSINT) متكاملة للمحققين والباحثين الأمنيين**

[المميزات](#-المميزات) • [التثبيت](#-التثبيت) • [الاستخدام](#-الاستخدام) • [التوثيق](#-التوثيق) • [المساهمة](#-المساهمة)

</div>

---

## 📖 نظرة عامة

**Coriza** هي منصة OSINT شاملة مبنية بـ Django توفر مجموعة متكاملة من الأدوات لجمع وتحليل المعلومات من مصادر مفتوحة. تم تصميمها خصيصاً للمحققين الرقميين، باحثي الأمن السيبراني، وفرق الاستخبارات.

### ✨ المميزات الرئيسية

#### 🛠️ أدوات OSINT المتكاملة
- **Social Media Intelligence**: البحث عن الحسابات الاجتماعية عبر 50+ منصة
- **Email OSINT**: تحليل البريد الإلكتروني، Gravatar، والتسريبات
- **IP Geolocation**: تحديد الموقع الجغرافي مع خرائط تفاعلية
- **Domain Intelligence**: فحص النطاقات، DNS، WHOIS، والنطاقات الفرعية
- **GitHub OSINT**: تحليل الملفات الشخصية والمستودعات
- **Google Dorks**: البحث المتقدم عن الملفات المكشوفة
- **Reverse Image Search**: البحث العكسي عن الصور
- **Certificate Transparency**: اكتشاف النطاقات الفرعية
- **Breach Detection**: فحص التسريبات الأمنية

#### 📊 إدارة التحقيقات
- **Case Management**: إدارة القضايا والتحقيقات
- **Session Tracking**: تتبع جلسات البحث والنتائج
- **Smart Results**: عرض ذكي للنتائج مع تصنيف تلقائي
- **Confidence Scoring**: تقييم موثوقية المعلومات
- **Timeline Analysis**: تحليل زمني للأحداث

#### 📈 التقارير والتحليلات
- **Automated Reports**: تقارير تلقائية بصيغ متعددة (PDF, HTML, JSON, CSV)
- **Visual Intelligence**: عرض مرئي ذكي للبيانات
- **Analytics Dashboard**: لوحة تحليلات متقدمة
- **Export Options**: تصدير النتائج بصيغ متعددة

#### 🎨 واجهة مستخدم حديثة
- **Dark Theme**: ثيم داكن احترافي
- **RTL Support**: دعم كامل للغة العربية
- **Responsive Design**: متوافق مع جميع الأجهزة
- **Interactive UI**: واجهة تفاعلية سلسة

#### 🔧 أدوات مساعدة
- **Hash Generator**: توليد الهاش بأنواع متعددة
- **Encoder/Decoder**: تشفير وفك تشفير البيانات
- **Timestamp Converter**: تحويل الطوابع الزمنية
- **JSON Formatter**: تنسيق ومدقق JSON
- **Text Diff**: مقارنة النصوص
- **Password Generator**: توليد كلمات مرور آمنة

---

## 🚀 التثبيت

### المتطلبات الأساسية

- Python 3.10 أو أحدث
- pip (مدير حزم Python)
- Git
- Redis (اختياري - للمهام غير المتزامنة)

### خطوات التثبيت

1. **استنساخ المستودع**
```bash
git clone https://github.com/YOUR_USERNAME/coriza-osint.git
cd coriza-osint
```

2. **إنشاء بيئة افتراضية**
```bash
python -m venv venv

# تفعيل البيئة الافتراضية
# على Windows:
venv\Scripts\activate
# على macOS/Linux:
source venv/bin/activate
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد ملف البيئة**
```bash
cp .env.example .env
# قم بتعديل .env وإضافة المفاتيح السرية
```

5. **تهيئة قاعدة البيانات**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **جمع الملفات الثابتة**
```bash
python manage.py collectstatic --noinput
```

7. **تشغيل الخادم**
```bash
python manage.py runserver
```

8. **الوصول للمنصة**
افتح المتصفح على: `http://127.0.0.1:8000`

---

## 📚 الاستخدام

### البدء السريع

1. **إنشاء حساب**: سجل دخول باستخدام حساب المدير
2. **إنشاء قضية**: ابدأ قضية تحقيق جديدة
3. **اختيار أداة**: اختر أداة OSINT مناسبة
4. **إدخال الهدف**: أدخل البريد الإلكتروني، اسم المستخدم، أو النطاق
5. **تشغيل البحث**: انقر على "بدء البحث"
6. **تحليل النتائج**: استعرض النتائج مع الذكاء المرئي
7. **إنشاء تقرير**: صدّر النتائج كتقرير احترافي

### أمثلة الاستخدام

#### البحث عن بريد إلكتروني
```python
# من واجهة الويب
1. اختر أداة "Email OSINT"
2. أدخل: example@domain.com
3. شاهد: Gravatar، معلومات النطاق، الحسابات المحتملة
```

#### فحص نطاق
```python
# من واجهة الويب
1. اختر أداة "Certificate Transparency"
2. أدخل: example.com
3. احصل على: جميع النطاقات الفرعية
```

---

## 🏗️ البنية التقنية

### التقنيات المستخدمة

- **Backend**: Django 5.2, Python 3.10+
- **Database**: SQLite (قابل للترقية لـ PostgreSQL)
- **Task Queue**: Celery + Redis
- **Frontend**: Bootstrap 5, JavaScript ES6+
- **Styling**: Custom CSS with Dark Theme
- **APIs**: RESTful API with Django REST Framework

### هيكل المشروع

```
coriza/
├── coriza/              # إعدادات المشروع الرئيسية
├── osint_tools/         # تطبيق أدوات OSINT
│   ├── models.py        # نماذج قاعدة البيانات
│   ├── views.py         # المنطق والعرض
│   ├── scrapers/        # أدوات جمع البيانات
│   ├── tasks.py         # مهام Celery
│   └── management/      # أوامر إدارية
├── templates/           # قوالب HTML
├── static/              # ملفات CSS/JS/Images
├── media/               # ملفات المستخدمين
└── requirements.txt     # المتطلبات
```

---

## 🔒 الأمان

### أفضل الممارسات

- ✅ جميع كلمات المرور مشفرة
- ✅ حماية CSRF مفعلة
- ✅ التحقق من الصلاحيات
- ✅ تسجيل جميع الأنشطة
- ✅ معدل محدود للطلبات

### ملاحظات أمنية

⚠️ **مهم**: 
- لا تشارك ملف `.env` أبداً
- غيّر `SECRET_KEY` في الإنتاج
- استخدم HTTPS في الإنتاج
- فعّل جدار الحماية

---

## 📖 التوثيق

للتوثيق الكامل، راجع:

- [دليل المستخدم](GRADUATION_PROJECT_README.md)
- [التوثيق التقني](GRADUATION_PROJECT_DOCUMENTATION.md)
- [دليل النشر](DEPLOYMENT_CHECKLIST.md)
- [كتالوج الأدوات](OSINT_TOOLS_CATALOG.md)

---

## 🤝 المساهمة

نرحب بالمساهمات! إليك كيفية المساهمة:

1. Fork المستودع
2. أنشئ فرع للميزة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push للفرع (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

### إرشادات المساهمة

- اتبع معايير PEP 8 للكود
- أضف اختبارات للميزات الجديدة
- حدّث التوثيق
- اكتب رسائل commit واضحة

---

## 📝 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

---

## 👥 الفريق

- **المطور الرئيسي**: [اسمك]
- **المشرف الأكاديمي**: [اسم المشرف]
- **الجامعة**: [اسم الجامعة]

---

## 🙏 شكر وتقدير

- [Django](https://www.djangoproject.com/) - إطار العمل الرئيسي
- [Bootstrap](https://getbootstrap.com/) - إطار عمل CSS
- [Font Awesome](https://fontawesome.com/) - الأيقونات
- جميع مساهمي المصادر المفتوحة

---

## 📞 التواصل

- **البريد الإلكتروني**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **LinkedIn**: [Your Name](https://linkedin.com/in/yourprofile)

---

## 🌟 النجوم والمتابعة

إذا أعجبك المشروع، لا تنسَ إعطاءه ⭐ على GitHub!

---

<div align="center">

**صُنع بـ ❤️ لمجتمع OSINT**

[⬆ العودة للأعلى](#-coriza-osint-platform)

</div>

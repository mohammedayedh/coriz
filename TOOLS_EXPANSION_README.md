# 🚀 توسيع منصة Coriza OSINT - إضافة 150+ أداة

## 📊 المشكلة الحالية

المنصة تحتوي على **6 أدوات فقط**:
1. Sherlock
2. Maigret  
3. theHarvester
4. Infoga
5. GHunt
6. SpiderFoot

بينما مهمة المنصة الأساسية هي جمع أكبر قدر ممكن من أدوات ومصادر OSINT.

---

## ✅ الحل المقترح

تم إنشاء نظام متكامل لإضافة **157 أداة إضافية** بسهولة:

### 📦 الملفات المنشأة

1. **OSINT_TOOLS_EXPANSION_PLAN.md**
   - خطة شاملة لإضافة 157 أداة
   - تصنيف حسب النوع (Username, Email, Domain, IP, Phone, Social, etc.)
   - تصنيف حسب مستوى الصلاحية (L1-L4)
   - جدول زمني للتنفيذ

2. **osint_tools/management/commands/bulk_add_tools.py**
   - أمر Django لإضافة أدوات بشكل جماعي
   - يقرأ من ملفات JSON
   - يدعم التحديث والتخطي

3. **osint_tools_data.json**
   - 30 أداة جاهزة للإضافة فوراً
   - بيانات كاملة لكل أداة
   - تكوين جاهز للاستخدام

4. **scripts/install_osint_tools.sh**
   - سكريبت bash لتثبيت الأدوات تلقائياً
   - يثبت 25+ أداة من مصادر مختلفة
   - يدعم Python, Go, APT packages

5. **QUICK_ADD_TOOLS_GUIDE.md**
   - دليل سريع للاستخدام
   - أمثلة عملية
   - نصائح وإرشادات

---

## 🚀 البدء السريع (3 خطوات)

### الخطوة 1: تثبيت الأدوات على السيرفر

```bash
# منح صلاحيات التنفيذ
chmod +x scripts/install_osint_tools.sh

# تشغيل السكريبت (يحتاج sudo)
sudo bash scripts/install_osint_tools.sh
```

هذا سيثبت 25+ أداة تلقائياً في `/opt/osint-tools`

### الخطوة 2: إضافة الأدوات إلى قاعدة البيانات

```bash
# إضافة 30 أداة جاهزة
python manage.py bulk_add_tools osint_tools_data.json
```

### الخطوة 3: التحقق والاختبار

```bash
# التحقق من عدد الأدوات
python manage.py shell
>>> from osint_tools.models import OSINTTool
>>> print(f"Total tools: {OSINTTool.objects.count()}")
Total tools: 36  # 6 موجودة + 30 جديدة

# تشغيل السيرفر
python manage.py runserver

# زيارة: http://localhost:8000/osint/tools/
```

---

## 📋 الأدوات الجديدة (30 أداة)

### 🔤 أدوات اسم المستخدم (4 أدوات)
- **Blackbird** - بحث في 500+ موقع
- **Nexfil** - بحث متقدم مع تحليل
- **Snoop** - 2500+ موقع (دعم روسي قوي)

### 📧 أدوات البريد الإلكتروني (6 أدوات)
- **Holehe** - فحص التسجيلات في 120+ موقع
- **Mosint** - OSINT شامل للبريد
- **Hunter.io** - بحث بريد احترافي (L2)
- **HaveIBeenPwned** - فحص التسريبات
- **h8mail** - كلمات المرور المسربة (L3)
- **Dehashed** - قاعدة تسريبات ضخمة (L3)

### 🌐 أدوات النطاقات (8 أدوات)
- **Sublist3r** - اكتشاف النطاقات الفرعية
- **Amass** - تعداد شامل من OWASP
- **Subfinder** - سريع جداً
- **Assetfinder** - اكتشاف الأصول
- **DNSRecon** - استطلاع DNS شامل
- **WhatWeb** - بصمة التقنيات
- **Httprobe** - فحص المواقع النشطة

### 🌍 أدوات IP (4 أدوات)
- **IPinfo** - معلومات IP شاملة
- **AbuseIPDB** - سمعة IP
- **Robtex** - معلومات الشبكة

### 📱 أدوات الهاتف (1 أداة)
- **PhoneInfoga** - OSINT متقدم للهاتف

### 📱 أدوات وسائل التواصل (4 أدوات
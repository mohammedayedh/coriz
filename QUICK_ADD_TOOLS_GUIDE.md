# 🚀 دليل سريع لإضافة أدوات OSINT

## 📦 ما تم إنشاؤه

تم إنشاء 3 ملفات جديدة لتسهيل إضافة أدوات OSINT:

1. **OSINT_TOOLS_EXPANSION_PLAN.md** - خطة شاملة لإضافة 157 أداة
2. **osint_tools/management/commands/bulk_add_tools.py** - أمر Django لإضافة الأدوات
3. **osint_tools_data.json** - ملف JSON يحتوي على 30 أداة جاهزة

---

## ⚡ إضافة الأدوات بسرعة

### الخطوة 1: إضافة الأدوات من ملف JSON

```bash
# إضافة جميع الأدوات من الملف
python manage.py bulk_add_tools osint_tools_data.json

# تحديث الأدوات الموجودة
python manage.py bulk_add_tools osint_tools_data.json --update
```

### الخطوة 2: التحقق من الأدوات المضافة

```bash
# عرض جميع الأدوات
python manage.py shell
>>> from osint_tools.models import OSINTTool
>>> OSINTTool.objects.count()
36  # 6 موجودة + 30 جديدة

>>> OSINTTool.objects.values_list('name', flat=True)
```

---

## 📋 الأدوات الجديدة المضافة (30 أداة)

### أدوات اسم المستخدم (4)
- ✅ Blackbird - 500+ موقع
- ✅ Nexfil - بحث متقدم
- ✅ Snoop - 2500+ موقع (روسي)

### أدوات البريد الإلكتروني (6)
- ✅ Holehe - فحص التسجيلات في 120+ موقع
- ✅ Mosint - OSINT شامل للبريد
- ✅ Hunter.io - بحث بريد احترافي (L2)
- ✅ HaveIBeenPwned - فحص التسريبات
- ✅ h8mail - كلمات المرور المسربة (L3)
- ✅ Dehashed - قاعدة تسريبات ضخمة (L3)

### أدوات النطاقات (8)
- ✅ Sublist3r - اكتشاف النطاقات الفرعية
- ✅ Amass - تعداد شامل من OWASP
- ✅ Subfinder - سريع جداً
- ✅ Assetfinder - اكتشاف الأصول
- ✅ DNSRecon - استطلاع DNS
- ✅ WhatWeb - بصمة التقنيات
- ✅ Httprobe - فحص المواقع النشطة

### أدوات IP (4)
- ✅ IPinfo - معلومات IP
- ✅ AbuseIPDB - سمعة IP
- ✅ Robtex - معلومات الشبكة

### أدوات وسائل التواصل (4)
- ✅ Social-Analyzer - تحليل شامل
- ✅ Twint - Twitter OSINT
- ✅ Instaloader - Instagram data

### أدوات عامة (4)
- ✅ Recon-ng - إطار عمل كامل
- ✅ ExifTool - metadata للصور
- ✅ Metagoofil - metadata المستندات
- ✅ TinEye - بحث عكسي للصور
- ✅ Maltego - تحليل الروابط (L2)

### أدوات متقدمة (3)
- ✅ Shodan - محرك بحث IoT (L2)
- ✅ Censys - فحص الإنترنت (L2)
- ✅ VirusTotal - فحص الأمان (L2)
- ✅ PhoneInfoga - OSINT للهاتف

---

## 🎯 الخطوات التالية

### 1. تثبيت الأدوات الفعلية

معظم الأدوات تحتاج تثبيت على السيرفر:

```bash
# إنشاء مجلد الأدوات
sudo mkdir -p /opt/osint-tools
cd /opt/osint-tools

# تثبيت PhoneInfoga
git clone https://github.com/sundowndev/phoneinfoga
cd phoneinfoga && go build

# تثبيت Sublist3r
git clone https://github.com/aboul3la/Sublist3r
cd Sublist3r && pip install -r requirements.txt

# تثبيت Holehe
pip install holehe

# تثبيت Amass
sudo apt install amass
# أو
go install -v github.com/OWASP/Amass/v3/...@master

# تثبيت Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# تثبيت Recon-ng
pip install recon-ng

# تثبيت Blackbird
git clone https://github.com/p1ngul1n0/blackbird
cd blackbird && pip install -r requirements.txt

# تثبيت Twint
pip3 install twint

# تثبيت Instaloader
pip3 install instaloader

# تثبيت ExifTool
sudo apt install libimage-exiftool-perl

# تثبيت Shodan CLI
pip install shodan

# تثبيت h8mail
pip3 install h8mail
```

### 2. إضافة المزيد من الأدوات

يمكنك إنشاء ملفات JSON إضافية:

```json
[
  {
    "name": "أداة جديدة",
    "slug": "new-tool",
    "description": "وصف الأداة",
    "tool_type": "email",
    "source_type": "open",
    "required_clearance": "L1",
    "status": "active",
    "icon": "fas fa-search",
    "color": "#007bff",
    "tool_path": "/opt/osint-tools/newtool",
    "executable_name": "newtool",
    "command_template": "newtool {target}"
  }
]
```

ثم:
```bash
python manage.py bulk_add_tools my_new_tools.json
```

### 3. تفعيل الأدوات التجارية (L2)

للأدوات التي تحتاج API keys:

```bash
# في .env
SHODAN_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
HUNTER_API_KEY=your_key_here
CENSYS_API_ID=your_id_here
CENSYS_API_SECRET=your_secret_here
```

### 4. إضافة أدوات من الخطة الشاملة

راجع ملف `OSINT_TOOLS_EXPANSION_PLAN.md` للحصول على:
- 157 أداة إضافية مقترحة
- تصنيف حسب النوع والمستوى
- روابط التثبيت والتوثيق

---

## 🔧 إنشاء أداة مخصصة

### 1. إنشاء ملف JSON

```json
{
  "name": "MyCustomTool",
  "slug": "my-custom-tool",
  "description": "أداة مخصصة للبحث",
  "tool_type": "general",
  "source_type": "open",
  "required_clearance": "L1",
  "status": "active",
  "icon": "fas fa-cog",
  "color": "#6c757d",
  "tool_path": "/opt/my-tools",
  "executable_name": "mytool",
  "command_template": "mytool --search {target}",
  "config_schema": {
    "timeout": 30,
    "max_results": 100
  },
  "supported_formats": ["json", "csv"]
}
```

### 2. إضافتها

```bash
python manage.py bulk_add_tools my_custom_tool.json
```

---

## 📊 الإحصائيات الحالية

بعد إضافة الأدوات الجديدة:

| الفئة | العدد |
|-------|------|
| Username | 7 |
| Email | 7 |
| Domain | 9 |
| IP | 4 |
| Phone | 1 |
| Social Media | 4 |
| General | 8 |
| **الإجمالي** | **36** |

### التوزيع حسب المستوى

| المستوى | العدد |
|---------|------|
| L1 (Public) | 26 |
| L2 (Commercial) | 7 |
| L3 (Leaked) | 2 |
| L4 (Agency) | 0 |

---

## ⚠️ ملاحظات مهمة

### 1. التراخيص
تأكد من توافق تراخيص الأدوات مع استخدامك:
- معظم الأدوات مفتوحة المصدر (MIT, GPL)
- بعض الأدوات التجارية تحتاج ترخيص

### 2. الأمان
- فحص الأدوات قبل التثبيت
- تشغيل الأدوات في بيئة معزولة (sandbox)
- مراقبة استخدام الموارد

### 3. الصيانة
- تحديث الأدوات بشكل دوري
- مراقبة الأدوات المعطلة
- إزالة الأدوات غير المستخدمة

### 4. الأداء
- بعض الأدوات بطيئة (timeout عالي)
- استخدام Celery للمهام الطويلة
- تحديد rate limits مناسبة

---

## 🎓 موارد إضافية

### قوائم أدوات OSINT
- [Awesome OSINT](https://github.com/jivoi/awesome-osint)
- [OSINT Framework](https://osintframework.com/)
- [IntelTechniques Tools](https://inteltechniques.com/tools/)

### دورات تعليمية
- [OSINT Techniques](https://www.osintcombine.com/)
- [Bellingcat's Online Investigation Toolkit](https://bit.ly/bcattools)

---

## 🚀 البدء السريع

```bash
# 1. إضافة الأدوات
python manage.py bulk_add_tools osint_tools_data.json

# 2. التحقق
python manage.py shell
>>> from osint_tools.models import OSINTTool
>>> print(f"Total tools: {OSINTTool.objects.count()}")

# 3. تشغيل السيرفر
python manage.py runserver

# 4. زيارة المنصة
# http://localhost:8000/osint/tools/
```

---

**تم الإنشاء:** 2026-04-22
**الحالة:** جاهز للاستخدام ✅

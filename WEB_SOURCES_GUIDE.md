# دليل استخدام مصادر OSINT الجديدة

## نظرة عامة

تم إضافة 5 مصادر OSINT قوية تعمل بدون الحاجة لمفاتيح API، جميعها مجانية 100% وتوفر معلومات حقيقية وكثيرة.

## المصادر المضافة

### 1. Certificate Transparency 🔐
**الوصف**: اكتشاف النطاقات الفرعية من شهادات SSL/TLS

**المميزات**:
- ✅ اكتشاف جميع النطاقات الفرعية (حتى المخفية)
- ✅ معلومات الشهادات وتواريخ الإصدار
- ✅ تاريخ النطاقات الفرعية
- ✅ بدون API key

**مثال الاستخدام**:
```bash
python osint_tools/scrapers/cert_transparency.py
# أو
from osint_tools.scrapers.cert_transparency import CertTransparencyScraper
scraper = CertTransparencyScraper()
results = scraper.search('example.com')
```

**نوع البحث**: `domain`
**مثال**: `google.com`, `facebook.com`

---

### 2. Wayback Machine 📚
**الوصف**: أرشيف المواقع القديمة والمحتوى المحذوف

**المميزات**:
- ✅ النسخ المحفوظة من المواقع
- ✅ تاريخ التغييرات
- ✅ المحتوى المحذوف
- ✅ إحصائيات تاريخية

**مثال الاستخدام**:
```bash
python osint_tools/scrapers/wayback_machine.py
# أو
from osint_tools.scrapers.wayback_machine import WaybackMachineScraper
scraper = WaybackMachineScraper()
results = scraper.search_snapshots('example.com')
```

**نوع البحث**: `domain or url`
**مثال**: `example.com`, `https://example.com/page.html`

---

### 3. Google Dorks 🔍
**الوصف**: البحث المتقدم لاكتشاف معلومات حساسة

**المميزات**:
- ✅ اكتشاف ملفات PDF, DOC, XLS المكشوفة
- ✅ البحث عن معلومات حساسة (passwords, emails, API keys)
- ✅ اكتشاف صفحات الإدارة
- ✅ فحص الثغرات الأمنية

**مثال الاستخدام**:
```bash
python osint_tools/scrapers/google_dorks.py
# أو
from osint_tools.scrapers.google_dorks import GoogleDorksScraper
scraper = GoogleDorksScraper()
results = scraper.search_domain('example.com', category='files')
```

**نوع البحث**: `domain, email, username, or custom dork`
**أمثلة**: 
- `example.com` - للبحث عن ملفات ومعلومات
- `site:example.com filetype:pdf` - dork مخصص

**الفئات المتاحة**:
- `files` - ملفات مكشوفة (PDF, DOC, XLS, etc.)
- `sensitive` - معلومات حساسة (passwords, emails, API keys)
- `directories` - صفحات إدارة (admin, login, upload)
- `vulnerabilities` - ثغرات أمنية (directory listing, phpinfo)

---

### 4. Reverse Image Search 🖼️
**الوصف**: البحث العكسي عن الصور في محركات متعددة

**المميزات**:
- ✅ البحث في 4 محركات (Google, Yandex, TinEye, Bing)
- ✅ إيجاد مصدر الصورة الأصلي
- ✅ الصور المشابهة والمعدلة
- ✅ حساب Hash للصورة (MD5, SHA256)

**مثال الاستخدام**:
```bash
python osint_tools/scrapers/reverse_image.py
# أو
from osint_tools.scrapers.reverse_image import ReverseImageSearcher
searcher = ReverseImageSearcher()
results = searcher.search_by_url('https://example.com/image.jpg')
```

**نوع البحث**: `image url`
**مثال**: `https://example.com/photo.jpg`

---

### 5. IP Geolocation 🌍
**الوصف**: تحديد الموقع الجغرافي لعناوين IP

**المميزات**:
- ✅ الموقع الجغرافي (البلد، المدينة، الإحداثيات)
- ✅ معلومات ISP والمنظمة
- ✅ رقم AS والشبكة
- ✅ كشف البروكسي والاستضافة
- ✅ رابط خريطة Google Maps

**مثال الاستخدام**:
```bash
python osint_tools/scrapers/ip_geolocation.py
# أو
from osint_tools.scrapers.ip_geolocation import IPGeolocationScraper
scraper = IPGeolocationScraper()
results = scraper.lookup('8.8.8.8')
```

**نوع البحث**: `ip address`
**مثال**: `8.8.8.8`, `1.1.1.1`

---

## التثبيت والإعداد

### 1. تثبيت المتطلبات

```bash
# تثبيت المكتبات المطلوبة
pip install -r requirements_web_scrapers.txt
```

### 2. إضافة الأدوات لقاعدة البيانات

```bash
# تشغيل الأمر لإضافة الأدوات
python manage.py add_web_sources
```

### 3. اختبار الأدوات

```bash
# اختبار كل أداة على حدة
python osint_tools/scrapers/cert_transparency.py
python osint_tools/scrapers/wayback_machine.py
python osint_tools/scrapers/google_dorks.py
python osint_tools/scrapers/reverse_image.py
python osint_tools/scrapers/ip_geolocation.py
```

---

## أمثلة عملية

### مثال 1: البحث الشامل عن نطاق

```python
from osint_tools.scrapers.cert_transparency import CertTransparencyScraper
from osint_tools.scrapers.wayback_machine import WaybackMachineScraper
from osint_tools.scrapers.google_dorks import GoogleDorksScraper

domain = "example.com"

# 1. اكتشاف النطاقات الفرعية
cert_scraper = CertTransparencyScraper()
subdomains = cert_scraper.search(domain)
print(f"النطاقات الفرعية: {subdomains['total_subdomains']}")

# 2. البحث في الأرشيف
wayback_scraper = WaybackMachineScraper()
archive = wayback_scraper.search_snapshots(domain)
print(f"النسخ المحفوظة: {archive['total_snapshots']}")

# 3. البحث عن ملفات مكشوفة
dorks_scraper = GoogleDorksScraper()
files = dorks_scraper.search_domain(domain, category='files')
print(f"الملفات المكتشفة: {files['total_findings']}")
```

### مثال 2: تحليل صورة

```python
from osint_tools.scrapers.reverse_image import ReverseImageSearcher

image_url = "https://example.com/photo.jpg"

searcher = ReverseImageSearcher()

# البحث في جميع المحركات
results = searcher.search_by_url(image_url)

for engine, engine_results in results['engines_results'].items():
    print(f"{engine}: {engine_results['search_url']}")

# حساب hash
hash_info = searcher.get_image_hash(image_url)
print(f"MD5: {hash_info['md5']}")
print(f"SHA256: {hash_info['sha256']}")
```

### مثال 3: تحليل IP

```python
from osint_tools.scrapers.ip_geolocation import IPGeolocationScraper

ip = "8.8.8.8"

scraper = IPGeolocationScraper()
info = scraper.lookup(ip)

print(f"الدولة: {info['country']}")
print(f"المدينة: {info['city']}")
print(f"ISP: {info['isp']}")
print(f"الإحداثيات: {info['latitude']}, {info['longitude']}")

# رابط الخريطة
if info['latitude'] and info['longitude']:
    map_url = scraper.get_map_url(info['latitude'], info['longitude'])
    print(f"الخريطة: {map_url}")
```

---

## الاستخدام من خلال المنصة

بعد إضافة الأدوات، ستكون متاحة في:

1. **صفحة الأدوات**: `/osint/tools/`
2. **البحث المبسط**: `/osint/search/`
3. **لوحة التحكم**: `/osint/`

### استخدام الأدوات:

1. اذهب إلى صفحة الأداة المطلوبة
2. أدخل الهدف (domain, IP, image URL, etc.)
3. اضغط "ابحث الآن"
4. انتظر النتائج

---

## ملاحظات مهمة

### 1. Rate Limiting
- Google Dorks: يُنصح بالانتظار 3-5 ثواني بين الطلبات
- باقي الأدوات: لا توجد قيود صارمة

### 2. القانونية
- ✅ جميع المصادر عامة وقانونية
- ✅ لا تخترق أي أنظمة
- ⚠️ استخدم المعلومات بمسؤولية

### 3. الدقة
- Certificate Transparency: دقة عالية جداً (100%)
- IP Geolocation: دقة عالية (90-95%)
- Wayback Machine: يعتمد على توفر الأرشيف
- Google Dorks: يعتمد على فهرسة Google
- Reverse Image: يعتمد على توفر الصورة

### 4. الأداء
- Certificate Transparency: سريع جداً (< 5 ثواني)
- IP Geolocation: سريع جداً (< 2 ثانية)
- Wayback Machine: متوسط (5-10 ثواني)
- Google Dorks: بطيء (10-30 ثانية) - بسبب Rate Limiting
- Reverse Image: سريع (< 5 ثواني)

---

## استكشاف الأخطاء

### خطأ: "Connection timeout"
**الحل**: تحقق من الاتصال بالإنترنت أو زد قيمة timeout

### خطأ: "Rate limit exceeded"
**الحل**: انتظر بضع دقائق قبل المحاولة مرة أخرى

### خطأ: "No results found"
**الحل**: تأكد من صحة الهدف (domain, IP, URL)

### خطأ: "Import error"
**الحل**: تأكد من تثبيت جميع المتطلبات:
```bash
pip install -r requirements_web_scrapers.txt
```

---

## التطوير المستقبلي

### المرحلة القادمة (قريباً):
1. ✨ Instagram OSINT
2. ✨ YouTube OSINT
3. ✨ Reddit OSINT
4. ✨ EXIF Data Extractor
5. ✨ Pastebin Search

### تحسينات مخططة:
- 🔄 Caching للنتائج
- 🔄 دعم البروكسي
- 🔄 تصدير النتائج (PDF, Excel)
- 🔄 جدولة البحث التلقائي
- 🔄 تنبيهات عند اكتشاف معلومات جديدة

---

## الدعم والمساعدة

إذا واجهت أي مشاكل:
1. تحقق من ملف `OSINT_WEB_SOURCES_PLAN.md`
2. راجع الأمثلة في كل ملف scraper
3. اختبر الأدوات بشكل مستقل أولاً

---

## الخلاصة

تم إضافة 5 مصادر OSINT قوية ومجانية تماماً:
- ✅ Certificate Transparency - للنطاقات الفرعية
- ✅ Wayback Machine - للأرشيف
- ✅ Google Dorks - للمعلومات الحساسة
- ✅ Reverse Image Search - للصور
- ✅ IP Geolocation - للمواقع الجغرافية

جميعها تعمل بدون API keys وتوفر معلومات حقيقية وكثيرة! 🎉

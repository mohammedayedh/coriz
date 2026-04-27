# دليل اختبار واجهة البحث المبسط

## الخطوة 1: التأكد من إضافة الأدوات

```bash
# تشغيل أمر إضافة الأدوات
python3 manage.py add_web_sources
```

**النتيجة المتوقعة:**
```
🚀 بدء إضافة مصادر OSINT الجديدة...
✅ تم إضافة: Email OSINT
✅ تم تحديث: IP Geolocation
✅ تم تحديث: Reverse Image Search
✅ تم تحديث: Certificate Transparency
✅ تم تحديث: Wayback Machine
✅ تم تحديث: Google Dorks
✨ تم إضافة 1 أداة جديدة وتحديث 5 أدوات موجودة
```

## الخطوة 2: التحقق من الأدوات في قاعدة البيانات

```bash
python3 manage.py shell
```

```python
from osint_tools.models import OSINTTool

# عرض جميع الأدوات النشطة
tools = OSINTTool.objects.filter(status='active')
print(f"عدد الأدوات النشطة: {tools.count()}")

# عرض الأدوات الجديدة
new_tools = ['email-osint', 'ip-geolocation', 'wayback-machine', 
             'cert-transparency', 'google-dorks', 'reverse-image']

for slug in new_tools:
    tool = OSINTTool.objects.filter(slug=slug).first()
    if tool:
        print(f"✅ {tool.name} ({slug}) - {tool.status}")
    else:
        print(f"❌ {slug} - غير موجود")
```

## الخطوة 3: تشغيل الخادم

```bash
python3 manage.py runserver
```

## الخطوة 4: اختبار الواجهات

### 1. صفحة البحث المبسط
**الرابط:** http://127.0.0.1:8000/osint/search/

**الاختبارات:**
- [ ] الصفحة تفتح بدون أخطاء
- [ ] الثيم الداكن يظهر بشكل صحيح
- [ ] الإحصائيات تظهر في الأعلى
- [ ] أنواع البحث (6 أنواع) تظهر
- [ ] حقل البحث يعمل
- [ ] الأمثلة السريعة قابلة للنقر

### 2. صفحة التحليلات
**الرابط:** http://127.0.0.1:8000/osint/analytics/

**الاختبارات:**
- [ ] الصفحة تفتح بدون أخطاء
- [ ] إحصائيات الجلسات تظهر
- [ ] إحصائيات النتائج تظهر
- [ ] الأدوات الأكثر استخداماً تظهر
- [ ] النشاط الشهري يظهر

## الخطوة 5: اختبار البحث الفعلي

### اختبار 1: بحث بريد إلكتروني
```
الإدخال: test@gmail.com
الأدوات المتوقعة:
- Email OSINT
- Breach Detector
```

**الخطوات:**
1. اختر نوع "بريد إلكتروني" أو اترك "تلقائي"
2. أدخل `test@gmail.com`
3. اضغط "ابحث الآن"

**النتيجة المتوقعة:**
- يظهر مؤشر التحميل
- تظهر الأدوات قيد التشغيل
- تظهر أشرطة التقدم
- تظهر النتائج تدريجياً

### اختبار 2: بحث نطاق
```
الإدخال: example.com
الأدوات المتوقعة:
- Wayback Machine
- Certificate Transparency
- Subdomain Enumerator
- Google Dorks
- Company Intelligence
```

**الخطوات:**
1. اختر نوع "موقع/نطاق" أو اترك "تلقائي"
2. أدخل `example.com`
3. اضغط "ابحث الآن"

### اختبار 3: بحث IP
```
الإدخال: 8.8.8.8
الأدوات المتوقعة:
- IP Geolocation
```

**الخطوات:**
1. اختر نوع "عنوان IP" أو اترك "تلقائي"
2. أدخل `8.8.8.8`
3. اضغط "ابحث الآن"

**النتيجة المتوقعة:**
- معلومات جغرافية (البلد: الولايات المتحدة)
- ISP: Google LLC
- إحداثيات GPS
- رابط خريطة Google Maps

### اختبار 4: بحث اسم مستخدم
```
الإدخال: john_doe
الأدوات المتوقعة:
- GitHub OSINT
- Social Investigator
```

## الخطوة 6: فحص Console للأخطاء

افتح Developer Tools (F12) وتحقق من:
- [ ] لا توجد أخطاء JavaScript في Console
- [ ] جميع طلبات AJAX تنجح (200 OK)
- [ ] CSRF Token يُرسل مع الطلبات

## الخطوة 7: اختبار الأدوات يدوياً

### اختبار IP Geolocation
```bash
cd osint_tools/scrapers
python3 ip_geolocation.py --ip 8.8.8.8
```

**النتيجة المتوقعة:**
```json
{
  "ip": "8.8.8.8",
  "country": "United States",
  "city": "Mountain View",
  "isp": "Google LLC",
  "coordinates": {
    "lat": 37.386,
    "lon": -122.0838
  }
}
```

### اختبار Email OSINT
```bash
python3 email_osint.py --email test@gmail.com
```

### اختبار Wayback Machine
```bash
python3 wayback_machine.py --url example.com
```

## المشاكل الشائعة والحلول

### المشكلة 1: خطأ 404 عند تشغيل الأداة
**السبب:** الأداة غير موجودة في قاعدة البيانات
**الحل:**
```bash
python3 manage.py add_web_sources
```

### المشكلة 2: CSRF Token Error
**السبب:** دالة getCsrfToken() لا تعمل
**الحل:** تأكد من تحديث ملف `simple_search_interface.html`

### المشكلة 3: الأدوات لا تبدأ
**السبب:** Celery غير مشغل
**الحل:**
```bash
# في terminal منفصل
celery -A coriza worker --loglevel=info
```

### المشكلة 4: النتائج لا تظهر
**السبب:** endpoint النتائج غير صحيح
**الحل:** تحقق من وجود `/osint/ajax/session-results/<id>/` في urls.py

## التحقق النهائي

### Checklist
- [ ] صفحة البحث تفتح بدون أخطاء
- [ ] صفحة Analytics تفتح بدون أخطاء
- [ ] يمكن البحث عن بريد إلكتروني
- [ ] يمكن البحث عن نطاق
- [ ] يمكن البحث عن IP
- [ ] النتائج تظهر بشكل صحيح
- [ ] لا توجد أخطاء في Console
- [ ] CSRF Token يعمل
- [ ] الأدوات تظهر في قائمة التقدم

## الأداء المتوقع

| نوع البحث | عدد الأدوات | الوقت المتوقع |
|-----------|-------------|---------------|
| بريد إلكتروني | 2 | 5-10 ثواني |
| نطاق | 5 | 15-30 ثانية |
| IP | 1 | 2-5 ثواني |
| اسم مستخدم | 2 | 10-20 ثانية |

## ملاحظات مهمة

1. **Celery مطلوب:** تأكد من تشغيل Celery worker
2. **Redis مطلوب:** تأكد من تشغيل Redis server
3. **الاتصال بالإنترنت:** الأدوات تحتاج اتصال للوصول للمصادر الخارجية
4. **Rate Limiting:** بعض المصادر لها حدود على عدد الطلبات

## الدعم

إذا واجهت مشاكل:
1. تحقق من logs Django
2. تحقق من logs Celery
3. تحقق من Console في المتصفح
4. راجع ملف `SEARCH_INTERFACE_FIX_REPORT.md`

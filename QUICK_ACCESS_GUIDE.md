# 🚀 دليل الوصول السريع - أدوات OSINT

---

## ⚡ البدء السريع

### 1. شغّل الخادم
```cmd
run_server.bat
```

### 2. افتح المتصفح
```
http://127.0.0.1:8000/osint/
```

---

## 🎯 الأدوات الأكثر استخداماً

### 🔍 استعلام عن IP
```
http://127.0.0.1:8000/osint/intel/ip-lookup/
```
**مثال:** أدخل `8.8.8.8` واضغط "تحليل"

---

### 🌐 استطلاع النطاق
```
http://127.0.0.1:8000/osint/intel/domain-recon/
```
**مثال:** أدخل `google.com` واضغط "استطلاع"

---

### 📧 فحص البريد الإلكتروني
```
http://127.0.0.1:8000/osint/intel/email-scanner/
```
**مثال:** أدخل `test@example.com` واضغط "فحص"

---

### 🛡️ فحص الروابط (VirusTotal)
```
http://127.0.0.1:8000/osint/intel/virustotal/
```
**مثال:** أدخل `https://example.com` واضغط "فحص"

---

### ⚠️ استخبارات التهديدات
```
http://127.0.0.1:8000/osint/intel/threat-intel/
```
**الاستخدام:** اضغط "تحديث التغذية"

---

### #️⃣ مُولّد الهاش
```
http://127.0.0.1:8000/osint/utilities/hash-generator/
```
**الاستخدام:** أدخل نص واختر نوع الهاش

---

### 🔐 مُولّد كلمات المرور
```
http://127.0.0.1:8000/osint/utilities/password-generator/
```
**الاستخدام:** اختر الطول والخيارات واضغط "توليد"

---

### 🔓 تشفير/فك تشفير
```
http://127.0.0.1:8000/osint/utilities/coder-decoder/
```
**الاستخدام:** أدخل نص واختر نوع التشفير

---

### 🎫 مُفتش JWT
```
http://127.0.0.1:8000/osint/utilities/jwt-inspector/
```
**الاستخدام:** الصق JWT token

---

## 📊 الإدارة

### جلساتي
```
http://127.0.0.1:8000/osint/sessions/
```

### نتائجي
```
http://127.0.0.1:8000/osint/results/
```

### تقاريري
```
http://127.0.0.1:8000/osint/reports/
```

### قضاياي
```
http://127.0.0.1:8000/osint/cases/
```

---

## 🔑 تفعيل API Keys (اختياري)

### 1. أنشئ ملف `.env` في جذر المشروع
```env
VIRUSTOTAL_API_KEY=your-key-here
OTX_API_KEY=your-key-here
```

### 2. احصل على المفاتيح
- **VirusTotal:** https://www.virustotal.com/gui/join-us
- **AlienVault OTX:** https://otx.alienvault.com/

### 3. أعد تشغيل الخادم

---

## ✅ الحالة

- ✅ **9 أدوات عاملة** (5 خادمية + 4 عميلية)
- ✅ **جميع القوالب موجودة**
- ✅ **CSRF protection مفعّلة**
- ✅ **Authentication مطلوبة**

---

## 📖 المزيد من المعلومات

- `OSINT_TOOLS_FIX_REPORT.md` - تقرير شامل
- `OSINT_NAVIGATION_GUIDE.md` - دليل التنقل الكامل
- `README.md` - دليل المشروع

---

**آخر تحديث:** 15 أبريل 2026

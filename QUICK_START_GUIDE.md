# 🚀 دليل البدء السريع - Coriza OSINT

## 📋 المتطلبات

- ✅ Python 3.8+
- ✅ البيئة الافتراضية (venv)
- ✅ جميع المتطلبات مثبتة من requirements.txt

---

## 🎯 البدء السريع

### 1. تفعيل البيئة الافتراضية

```cmd
venv\Scripts\activate
```

---

### 2. تشغيل الاختبارات

#### الطريقة الأولى (موصى بها):
```cmd
run_tests.bat
```

#### الطريقة الثانية (يدوياً):
```cmd
set DEBUG=true
python test_core_system.py
```

---

### 3. تشغيل خادم التطوير

#### الطريقة الأولى (موصى بها):
```cmd
run_server.bat
```

#### الطريقة الثانية (يدوياً):
```cmd
set DEBUG=true
python manage.py runserver
```

ثم افتح المتصفح على: http://127.0.0.1:8000

---

## 🔧 الأوامر المفيدة

### فحص النظام:
```cmd
set DEBUG=true
python manage.py check
```

### فحص الأمان:
```cmd
set DEBUG=true
python manage.py check --deploy
```

### عرض Migrations:
```cmd
set DEBUG=true
python manage.py showmigrations
```

### إنشاء مستخدم مدير:
```cmd
set DEBUG=true
python manage.py createsuperuser
```

### الوصول إلى Django Shell:
```cmd
set DEBUG=true
python manage.py shell
```

---

## 📁 الملفات المهمة

### ملفات التشغيل:
- `run_tests.bat` - تشغيل الاختبارات
- `run_server.bat` - تشغيل خادم التطوير
- `test_core_system.py` - سكريبت الاختبار الشامل

### ملفات التوثيق:
- `CORE_SYSTEM_TEST_REPORT.md` - تقرير اختبار النظام
- `CRITICAL_FIXES_REPORT.md` - تقرير الإصلاحات الحرجة
- `SECURITY_UPDATES.md` - تحديثات الأمان
- `docs/CSRF_PROTECTION_GUIDE.md` - دليل حماية CSRF
- `FIXES_SUMMARY_AR.md` - ملخص الإصلاحات

---

## 🌐 الصفحات المتاحة

بعد تشغيل الخادم، يمكنك الوصول إلى:

| الصفحة | الرابط |
|--------|--------|
| الصفحة الرئيسية | http://127.0.0.1:8000/ |
| تسجيل الدخول | http://127.0.0.1:8000/auth/login/ |
| التسجيل | http://127.0.0.1:8000/auth/register/ |
| لوحة التحكم | http://127.0.0.1:8000/dashboard/ |
| أدوات OSINT | http://127.0.0.1:8000/osint/ |
| لوحة الإدارة | http://127.0.0.1:8000/admin/ |

---

## 🔑 إنشاء مستخدم مدير

```cmd
set DEBUG=true
python manage.py createsuperuser
```

ثم أدخل:
- اسم المستخدم
- البريد الإلكتروني
- كلمة المرور

---

## 🛠️ إضافة بيانات تجريبية

### إنشاء أدوات OSINT:
```cmd
set DEBUG=true
python manage.py create_osint_tools
```

---

## ⚠️ ملاحظات مهمة

### للتطوير المحلي:
- ✅ استخدم `DEBUG=true`
- ✅ SECRET_KEY سيتم توليده تلقائياً
- ✅ ستظهر تحذيرات (طبيعية في التطوير)

### للإنتاج:
- 🔴 يجب تعيين `DEBUG=false`
- 🔴 يجب تعيين `SECRET_KEY` جديد
- 🔴 يجب مراجعة `SECURITY_UPDATES.md`

---

## 🐛 حل المشاكل الشائعة

### المشكلة: SECRET_KEY error
```
ImproperlyConfigured: SECRET_KEY environment variable must be set
```

**الحل:**
```cmd
set DEBUG=true
```

---

### المشكلة: Module not found
```
ModuleNotFoundError: No module named 'django'
```

**الحل:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

---

### المشكلة: Database locked
```
OperationalError: database is locked
```

**الحل:**
```cmd
# أغلق جميع نوافذ Django
# ثم أعد التشغيل
```

---

### المشكلة: Port already in use
```
Error: That port is already in use
```

**الحل:**
```cmd
# استخدم port مختلف
python manage.py runserver 8001
```

---

## 📊 حالة النظام

### ✅ جاهز:
- [x] جميع الوحدات تعمل (100%)
- [x] قاعدة البيانات متزامنة
- [x] الأمان الأساسي مفعل
- [x] CSRF Protection مفعل
- [x] Celery جاهز (اختياري)

### 🎯 الخطوات التالية:
1. إنشاء مستخدم مدير
2. إضافة أدوات OSINT
3. اختبار الأدوات
4. تطوير ميزات جديدة

---

## 📞 المساعدة

إذا واجهت مشاكل:

1. **راجع التوثيق:**
   - CORE_SYSTEM_TEST_REPORT.md
   - CRITICAL_FIXES_REPORT.md
   - SECURITY_UPDATES.md

2. **تحقق من الإعدادات:**
   - هل DEBUG=true؟
   - هل البيئة الافتراضية مفعلة؟
   - هل جميع المتطلبات مثبتة؟

3. **شغل الاختبارات:**
   ```cmd
   run_tests.bat
   ```

---

## ✅ Checklist البدء

- [ ] تفعيل البيئة الافتراضية
- [ ] تشغيل الاختبارات (run_tests.bat)
- [ ] إنشاء مستخدم مدير
- [ ] تشغيل الخادم (run_server.bat)
- [ ] فتح المتصفح على http://127.0.0.1:8000
- [ ] تسجيل الدخول
- [ ] استكشاف النظام

---

**تم إنشاء هذا الدليل بواسطة:** Kiro AI Assistant  
**التاريخ:** 2026-04-15  
**الإصدار:** 1.0  
**الحالة:** ✅ جاهز للاستخدام

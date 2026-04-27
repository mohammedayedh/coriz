# 📤 دليل رفع Coriza على GitHub

## 🎯 الهدف
رفع مشروع Coriza OSINT Platform على GitHub بشكل آمن واحترافي.

---

## ✅ قائمة التحقق قبل الرفع

### 1. الأمان
- [ ] تأكد من وجود `.env` في `.gitignore`
- [ ] تأكد من عدم وجود `SECRET_KEY` في الكود
- [ ] تأكد من عدم وجود كلمات مرور في الكود
- [ ] تأكد من عدم وجود API keys في الكود
- [ ] راجع جميع الملفات للتأكد من عدم وجود معلومات حساسة

### 2. التنظيف
- [ ] حذف `db.sqlite3` (أو إضافته لـ .gitignore)
- [ ] حذف مجلد `media/` (أو إضافته لـ .gitignore)
- [ ] حذف مجلد `__pycache__/`
- [ ] حذف ملفات `.pyc`
- [ ] حذف ملفات `.log`
- [ ] حذف الملفات المضغوطة (`.zip`, `.tar.gz`)

### 3. التوثيق
- [ ] README.md موجود ومحدث
- [ ] LICENSE موجود
- [ ] CONTRIBUTING.md موجود
- [ ] .gitignore محدث
- [ ] requirements.txt محدث

---

## 🚀 خطوات الرفع

### الطريقة 1: باستخدام السكريبت التلقائي

```bash
# امنح صلاحيات التنفيذ
chmod +x prepare_for_github.sh

# شغل السكريبت
./prepare_for_github.sh
```

### الطريقة 2: يدوياً

#### الخطوة 1: تهيئة Git (إذا لم يكن موجوداً)

```bash
git init
```

#### الخطوة 2: إضافة الملفات

```bash
# إضافة جميع الملفات
git add .

# أو إضافة ملفات محددة
git add README.md
git add requirements.txt
git add coriza/
git add osint_tools/
# ... إلخ
```

#### الخطوة 3: التحقق من الملفات المضافة

```bash
# عرض الملفات التي سيتم رفعها
git status

# التأكد من عدم وجود ملفات حساسة
git status | grep -E "\.env|db\.sqlite3|\.pyc"
```

#### الخطوة 4: Commit الأول

```bash
git commit -m "Initial commit: Coriza OSINT Platform

- Complete Django OSINT platform
- 10+ OSINT tools integrated
- Dark theme UI with RTL support
- Case management system
- Automated reporting
- Analytics dashboard
"
```

#### الخطوة 5: إنشاء مستودع على GitHub

1. اذهب إلى https://github.com/new
2. اسم المستودع: `coriza-osint` (أو أي اسم تريده)
3. الوصف: "Advanced OSINT Platform for Intelligence Gathering"
4. اختر: Public أو Private
5. **لا تضف** README أو LICENSE أو .gitignore (موجودين بالفعل)
6. انقر "Create repository"

#### الخطوة 6: ربط المستودع المحلي بـ GitHub

```bash
# استبدل YOUR_USERNAME باسم المستخدم الخاص بك
git remote add origin https://github.com/YOUR_USERNAME/coriza-osint.git

# أو باستخدام SSH
git remote add origin git@github.com:YOUR_USERNAME/coriza-osint.git
```

#### الخطوة 7: رفع الكود

```bash
# تغيير اسم الفرع إلى main (إذا كان master)
git branch -M main

# رفع الكود
git push -u origin main
```

---

## 🎨 تحسينات إضافية على GitHub

### 1. إضافة Topics

في صفحة المستودع على GitHub:
- انقر على ⚙️ Settings
- أضف Topics: `osint`, `django`, `python`, `cybersecurity`, `intelligence`, `investigation`, `arabic`

### 2. إضافة Description

```
Advanced OSINT Platform for Intelligence Gathering | منصة استخبارات مفتوحة المصدر متكاملة
```

### 3. إضافة Website

إذا كان لديك demo:
```
https://coriza-demo.herokuapp.com
```

### 4. تفعيل GitHub Pages (اختياري)

لعرض التوثيق:
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main → /docs
4. Save

### 5. إضافة Badges في README

تم إضافتها بالفعل في README.md:
- Python version
- Django version
- License
- Build status (بعد إضافة CI/CD)

---

## 🔄 التحديثات المستقبلية

### إضافة تغييرات جديدة

```bash
# إضافة الملفات المعدلة
git add .

# Commit مع رسالة واضحة
git commit -m "Add: Email OSINT tool improvements"

# رفع التحديثات
git push origin main
```

### إنشاء Releases

1. اذهب إلى Releases على GitHub
2. انقر "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `Coriza v1.0.0 - Initial Release`
5. اكتب changelog
6. Publish release

---

## 🛡️ نصائح الأمان

### ما يجب عدم رفعه أبداً:

❌ ملف `.env`
❌ `SECRET_KEY` في الكود
❌ كلمات المرور
❌ API Keys
❌ قاعدة البيانات مع بيانات حقيقية
❌ ملفات المستخدمين الشخصية
❌ مفاتيح SSH
❌ Tokens

### ماذا لو رفعت ملف حساس بالخطأ؟

```bash
# حذف الملف من Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH_TO_FILE" \
  --prune-empty --tag-name-filter cat -- --all

# رفع التغييرات
git push origin --force --all

# ⚠️ مهم: غيّر جميع المفاتيح والكلمات السرية المكشوفة فوراً!
```

---

## 📊 إحصائيات المشروع

بعد الرفع، يمكنك إضافة:

### GitHub Actions (CI/CD)

ملف `.github/workflows/django.yml`:

```yaml
name: Django CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Tests
      run: |
        python manage.py test
```

### Code Coverage

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## 🎉 بعد الرفع

### شارك مشروعك:

1. **LinkedIn**: اكتب منشور عن المشروع
2. **Twitter**: شارك الرابط مع #OSINT #Django
3. **Reddit**: r/OSINT, r/django
4. **Dev.to**: اكتب مقال تقني
5. **Medium**: شارك تجربتك

### اطلب Feedback:

- شارك في مجموعات OSINT
- اطلب code review
- استمع للاقتراحات

---

## 📞 المساعدة

إذا واجهت مشاكل:

1. راجع [GitHub Docs](https://docs.github.com)
2. ابحث في Stack Overflow
3. اسأل في GitHub Discussions
4. راسلنا على البريد الإلكتروني

---

## ✅ Checklist النهائي

قبل الإعلان عن المشروع:

- [ ] الكود يعمل بدون أخطاء
- [ ] README واضح وشامل
- [ ] LICENSE موجود
- [ ] لا توجد معلومات حساسة
- [ ] Screenshots موجودة
- [ ] التوثيق كامل
- [ ] الكود منظم ونظيف
- [ ] Commits واضحة ومنظمة

---

**🎊 مبروك! مشروعك الآن على GitHub!**

لا تنسَ:
- ⭐ Star المشروع
- 👀 Watch للتحديثات
- 🍴 Fork للمساهمة

**حظاً موفقاً! 🚀**

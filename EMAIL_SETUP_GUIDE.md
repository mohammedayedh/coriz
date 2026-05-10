# 📧 دليل إعداد البريد الإلكتروني - كوريزا OSINT

## 📌 الوضع الحالي

**❌ البريد الإلكتروني لا يُرسل فعلياً حالياً**

النظام يستخدم `console.EmailBackend` وهذا يعني:
- رسائل البريد تُطبع في Console/Terminal فقط
- لا يتم إرسال بريد إلكتروني حقيقي للمستخدمين
- مناسب للتطوير فقط

## ✅ لتفعيل إرسال البريد الفعلي

### الخطوة 1: اختيار خدمة SMTP

لديك عدة خيارات:

#### 🔵 الخيار 1: Gmail (مجاني - الأسهل)

**المميزات:**
- مجاني تماماً
- سهل الإعداد
- موثوق

**العيوب:**
- حد أقصى 500 بريد/يوم
- يتطلب App Password

**الإعداد:**

1. **تفعيل المصادقة الثنائية (2FA)** في حساب Gmail
2. **إنشاء App Password:**
   - اذهب إلى: https://myaccount.google.com/apppasswords
   - اختر "Mail" و "Other (Custom name)"
   - سمّه "Coriza OSINT"
   - انسخ كلمة المرور المكونة من 16 حرف

3. **تحديث ملف `.env` على السيرفر:**

```bash
# على السيرفر
sudo nano /srv/coriza/.env
```

أضف/عدّل هذه الأسطر:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # App Password من الخطوة 2
DEFAULT_FROM_EMAIL=noreply@coriza.cloud
```

#### 🟢 الخيار 2: SendGrid (احترافي - موصى به للإنتاج)

**المميزات:**
- 100 بريد/يوم مجاناً
- احترافي وموثوق
- تقارير وإحصائيات مفصلة
- معدل توصيل عالي

**الإعداد:**

1. **إنشاء حساب:** https://signup.sendgrid.com/
2. **إنشاء API Key:**
   - Settings → API Keys → Create API Key
   - اختر "Full Access"
   - انسخ المفتاح

3. **تحديث `.env`:**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxxxxxx  # API Key من الخطوة 2
DEFAULT_FROM_EMAIL=noreply@coriza.cloud
```

#### 🟣 الخيار 3: Mailgun (احترافي)

**المميزات:**
- 5,000 بريد/شهر مجاناً
- موثوق جداً
- API قوي

**الإعداد:**

1. **إنشاء حساب:** https://signup.mailgun.com/
2. **الحصول على SMTP Credentials:**
   - Sending → Domain Settings → SMTP Credentials
3. **تحديث `.env`:**

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@coriza.cloud
```

---

### الخطوة 2: تطبيق التغييرات على السيرفر

بعد تحديث ملف `.env`:

```bash
# إعادة تشغيل الخدمة
sudo systemctl restart gunicorn-coriz

# التحقق من الحالة
sudo systemctl status gunicorn-coriz
```

---

### الخطوة 3: اختبار إرسال البريد

#### اختبار من Django Shell:

```bash
cd /srv/coriza/app
source /srv/coriza/venv/bin/activate
python manage.py shell
```

```python
from django.core.mail import send_mail

# اختبار إرسال بريد
send_mail(
    'اختبار البريد - كوريزا OSINT',
    'هذا بريد اختبار من منصة كوريزا.',
    'noreply@coriza.cloud',
    ['your-test-email@gmail.com'],
    fail_silently=False,
)

print("✅ تم إرسال البريد بنجاح!")
```

#### اختبار من الموقع:

1. اذهب إلى: https://coriza.cloud/auth/password-reset/
2. أدخل بريد إلكتروني مسجل
3. تحقق من وصول البريد

---

## 🔍 استكشاف الأخطاء

### المشكلة: "SMTPAuthenticationError"

**الحل:**
- تأكد من صحة `EMAIL_HOST_USER` و `EMAIL_HOST_PASSWORD`
- في Gmail: تأكد من استخدام App Password وليس كلمة المرور العادية
- تأكد من تفعيل "Less secure app access" (إن لزم)

### المشكلة: "Connection refused"

**الحل:**
- تأكد من صحة `EMAIL_HOST` و `EMAIL_PORT`
- تأكد من أن السيرفر يسمح بالاتصالات الخارجية على المنفذ 587

### المشكلة: "SMTPServerDisconnected"

**الحل:**
- جرب استخدام `EMAIL_USE_SSL=true` و `EMAIL_PORT=465` بدلاً من TLS

### المشكلة: البريد يذهب إلى Spam

**الحل:**
- استخدم خدمة احترافية مثل SendGrid أو Mailgun
- أضف SPF و DKIM records لدومينك
- استخدم بريد من نفس الدومين (noreply@coriza.cloud)

---

## 📊 مقارنة الخيارات

| الخدمة | مجاني | الحد اليومي | سهولة الإعداد | الموثوقية | للإنتاج |
|--------|-------|-------------|---------------|-----------|----------|
| Gmail | ✅ | 500/يوم | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ |
| SendGrid | ✅ | 100/يوم | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |
| Mailgun | ✅ | 5000/شهر | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |

---

## 🎯 التوصية

**للتطوير والاختبار:** استخدم Gmail (سريع وسهل)

**للإنتاج:** استخدم SendGrid أو Mailgun (احترافي وموثوق)

---

## 📝 ملاحظات مهمة

1. **لا تضع بيانات SMTP في Git:**
   - ملف `.env` مُستثنى من Git (موجود في `.gitignore`)
   - لا تشارك `EMAIL_HOST_PASSWORD` أبداً

2. **استخدم بريد من دومينك:**
   - بدلاً من `noreply@gmail.com`
   - استخدم `noreply@coriza.cloud`
   - هذا يزيد من الموثوقية ويقلل احتمالية Spam

3. **راقب حدود الإرسال:**
   - Gmail: 500 بريد/يوم
   - SendGrid Free: 100 بريد/يوم
   - إذا تجاوزت الحد، ستحتاج للترقية

4. **اختبر دائماً:**
   - اختبر إرسال البريد بعد أي تغيير
   - تحقق من logs: `sudo journalctl -u gunicorn-coriz -f`

---

## 🔗 روابط مفيدة

- [Gmail App Passwords](https://myaccount.google.com/apppasswords)
- [SendGrid Signup](https://signup.sendgrid.com/)
- [Mailgun Signup](https://signup.mailgun.com/)
- [Django Email Documentation](https://docs.djangoproject.com/en/5.2/topics/email/)

---

## ✅ قائمة التحقق

- [ ] اختيار خدمة SMTP
- [ ] إنشاء حساب والحصول على بيانات الاعتماد
- [ ] تحديث ملف `.env` على السيرفر
- [ ] إعادة تشغيل الخدمة
- [ ] اختبار إرسال بريد من Django Shell
- [ ] اختبار من الموقع (password reset)
- [ ] التحقق من وصول البريد
- [ ] التحقق من أن البريد لا يذهب إلى Spam

---

**آخر تحديث:** 2026-05-10

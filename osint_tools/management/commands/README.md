# أوامر إدارة OSINT

هذا المجلد يحتوي على أوامر Django الإدارية لصيانة نظام OSINT.

## الأوامر المتاحة

### 1. cleanup_stuck_sessions

تنظيف الجلسات العالقة في حالة "running" أو "pending" لفترة طويلة.

#### الاستخدام الأساسي
```bash
python manage.py cleanup_stuck_sessions
```

#### الخيارات

**--minutes**: عدد الدقائق لاعتبار الجلسة عالقة (افتراضي: 10)
```bash
python manage.py cleanup_stuck_sessions --minutes 15
```

**--dry-run**: عرض الجلسات التي سيتم تنظيفها بدون تنفيذ
```bash
python manage.py cleanup_stuck_sessions --dry-run
```

#### أمثلة

تنظيف الجلسات العالقة لأكثر من 5 دقائق:
```bash
python manage.py cleanup_stuck_sessions --minutes 5
```

معاينة الجلسات العالقة بدون حذف:
```bash
python manage.py cleanup_stuck_sessions --dry-run
```

#### جدولة تلقائية (Cron)

لتشغيل الأمر تلقائياً كل 15 دقيقة، أضف إلى crontab:
```bash
*/15 * * * * cd /path/to/coriza && python manage.py cleanup_stuck_sessions --minutes 10
```

---

## إضافة أوامر جديدة

لإنشاء أمر إداري جديد:

1. أنشئ ملف Python في هذا المجلد
2. استورد `BaseCommand` من `django.core.management.base`
3. أنشئ class يرث من `BaseCommand`
4. عرّف method `handle()`

### مثال:
```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'وصف الأمر'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('تم التنفيذ بنجاح'))
```

---

## ملاحظات

- جميع الأوامر تدعم `--help` لعرض المساعدة
- استخدم `self.stdout.write()` للطباعة
- استخدم `self.style.SUCCESS()` للرسائل الناجحة
- استخدم `self.style.ERROR()` لرسائل الخطأ
- استخدم `self.style.WARNING()` للتحذيرات

#!/bin/bash

# سكريبت تحضير المشروع للرفع على GitHub
# يقوم بتنظيف الملفات غير الضرورية والتأكد من الأمان

echo "🚀 تحضير مشروع Coriza للرفع على GitHub..."
echo ""

# 1. التحقق من وجود .env
if [ -f ".env" ]; then
    echo "✅ ملف .env موجود (لن يتم رفعه)"
else
    echo "⚠️  تحذير: ملف .env غير موجود"
    echo "   قم بإنشائه من .env.example"
fi

# 2. حذف ملفات Python المؤقتة
echo ""
echo "🧹 تنظيف ملفات Python المؤقتة..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null
find . -type f -name "*.log" -delete 2>/dev/null
echo "✅ تم تنظيف ملفات Python"

# 3. حذف قاعدة البيانات (اختياري)
echo ""
read -p "❓ هل تريد حذف db.sqlite3؟ (y/n): " delete_db
if [ "$delete_db" = "y" ]; then
    rm -f db.sqlite3
    echo "✅ تم حذف قاعدة البيانات"
else
    echo "⏭️  تم تخطي حذف قاعدة البيانات"
fi

# 4. حذف ملفات الوسائط
echo ""
read -p "❓ هل تريد حذف مجلد media/؟ (y/n): " delete_media
if [ "$delete_media" = "y" ]; then
    rm -rf media/*
    echo "✅ تم حذف ملفات الوسائط"
else
    echo "⏭️  تم تخطي حذف ملفات الوسائط"
fi

# 5. حذف ملفات الـ logs
echo ""
if [ -d "logs" ]; then
    rm -rf logs/*
    echo "✅ تم تنظيف مجلد logs"
fi

# 6. حذف الملفات المضغوطة
echo ""
echo "🗑️  حذف الملفات المضغوطة..."
find . -type f \( -name "*.zip" -o -name "*.tar.gz" -o -name "*.rar" \) -delete 2>/dev/null
echo "✅ تم حذف الملفات المضغوطة"

# 7. التحقق من SECRET_KEY
echo ""
echo "🔒 التحقق من الأمان..."
if grep -q "SECRET_KEY.*=.*'django-insecure" coriza/settings.py 2>/dev/null; then
    echo "⚠️  تحذير: SECRET_KEY غير آمن في settings.py"
    echo "   تأكد من استخدام متغير بيئي في الإنتاج"
else
    echo "✅ SECRET_KEY يبدو آمناً"
fi

# 8. التحقق من DEBUG
if grep -q "DEBUG.*=.*True" coriza/settings.py 2>/dev/null; then
    echo "⚠️  تحذير: DEBUG = True في settings.py"
    echo "   تأكد من تعطيله في الإنتاج"
else
    echo "✅ DEBUG مضبوط بشكل صحيح"
fi

# 9. إنشاء requirements.txt محدث
echo ""
echo "📦 تحديث requirements.txt..."
if [ -d "venv" ] || [ -d ".venv" ]; then
    source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null
    pip freeze > requirements.txt
    echo "✅ تم تحديث requirements.txt"
else
    echo "⚠️  لم يتم العثور على بيئة افتراضية"
fi

# 10. عرض ملخص
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ تم تحضير المشروع بنجاح!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 الخطوات التالية:"
echo "1. راجع ملف .gitignore"
echo "2. تأكد من عدم وجود معلومات حساسة"
echo "3. قم بتشغيل: git init (إذا لم يكن موجوداً)"
echo "4. قم بتشغيل: git add ."
echo "5. قم بتشغيل: git commit -m 'Initial commit'"
echo "6. أنشئ مستودع على GitHub"
echo "7. قم بتشغيل: git remote add origin YOUR_REPO_URL"
echo "8. قم بتشغيل: git push -u origin main"
echo ""
echo "🎉 حظاً موفقاً!"

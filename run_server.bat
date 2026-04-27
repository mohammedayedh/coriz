@echo off
REM سكريبت لتشغيل خادم التطوير

echo ========================================
echo تشغيل خادم Coriza OSINT للتطوير
echo ========================================
echo.

REM تعيين وضع التطوير
set DEBUG=true

REM عرض معلومات
echo وضع التطوير: مفعل
echo الخادم سيعمل على: http://127.0.0.1:8000
echo.
echo للإيقاف: اضغط Ctrl+C
echo ========================================
echo.

REM تشغيل الخادم
python manage.py runserver

pause

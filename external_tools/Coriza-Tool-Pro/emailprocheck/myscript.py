# استيراد ملف الأداة
import emailprocheck

# تحديد البريد الإلكتروني الذي تريد فحصه
target = "bill@microsoft.com"

# تحديد اسم ملف الحفظ
csv_filename = "email_report.csv"

# استدعاء الدالة لتشغيل الفحص التلقائي
emailprocheck.run_emailrep(email=target, output_file=csv_filename)
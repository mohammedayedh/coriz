import checkname

# تحديد اسم المستخدم الذي تريد فحصه
target = input("Please enter domain to search : ")

# تحديد اسم ملف حفظ النتائج
csv_filename = f"{target}_domains_report.csv"

# استدعاء الأداة برمجياً لتنفيذ الفحص
print(f"جاري الفحص التلقائي لاسم المستخدم: {target}...")
checkname.run_namechk(username=target, output_file=csv_filename)

print("تم الانتهاء من الفحص وحفظ الملف بنجاح!")
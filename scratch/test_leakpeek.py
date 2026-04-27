import sys
import os
import json

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'leakpeak'))

try:
    from emailscheck import run_leakpeek_scraper
    # الاختبار على بريد عشوائي لرؤية الاستجابة
    run_leakpeek_scraper("test@gmail.com", "scratch/leakpeek_test.json")
    
    if os.path.exists("scratch/leakpeek_test.json"):
        print("SUCCESS: LeakPeek results saved")
        with open("scratch/leakpeek_test.json", "r") as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("FAILED: No results file created")

except Exception as e:
    print(f"ERROR: {e}")

import sys
import os

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'cve-stalker'))

try:
    from cvestalker import search_cve
    import json
    
    # اختبار البحث عن ثغرات Apache
    results = search_cve(cve_input="", text_input="Apache", save_to_file=False, quiet_mode=True)
    
    if results:
        print(f"SUCCESS: Found {len(results)} results")
        # طباعة أول نتيجة كمثال
        print(json.dumps(results[0], indent=2))
    else:
        print("FAILED: No results found or API error")

except Exception as e:
    print(f"ERROR: {e}")

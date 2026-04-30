"""
CheckNames Adapter - فحص توفر أسماء النطاقات عبر DNS
يبحث في 21 امتداد شائع ويعيد JSON نظيف
"""
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXTERNAL_TOOL_DIR = os.path.join(PROJECT_ROOT, 'external_tools', 'Coriza-Tool-Pro', 'checknames')
sys.path.insert(0, EXTERNAL_TOOL_DIR)

import checkname

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Username/domain name not provided"}))
        sys.exit(1)

    target = sys.argv[1].strip()
    # إزالة امتدادات النطاق إن وجدت (نريد الاسم فقط)
    target = target.split('.')[0]

    # إعادة توجيه stdout لإخفاء مخرجات الأداة الأصلية الملونة
    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    try:
        raw_results = checkname.run_namechk(username=target)
        sys.stdout.close()
        sys.stdout = original_stdout

        # تحويل النتائج إلى صيغة كائنات مفصلة يفهمها النظام
        formatted_results = []
        for r in raw_results:
            domain = r.get("Domain")
            status = r.get("Status", "Unknown")
            is_registered = "Registered" in status
            
            formatted_results.append({
                "title": domain,
                "result_type": "domain",
                "status": status,
                "confidence": "high" if is_registered else "medium",
                "description": f"النطاق {domain} حالة توفره: {status}",
                "url": f"http://{domain}" if is_registered else ""
            })

        output = {
            "target": target,
            "success": True,
            "results": formatted_results,
            "total_checked": len(raw_results)
        }
        print(json.dumps(output))

    except Exception as e:
        sys.stdout.close()
        sys.stdout = original_stdout
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()

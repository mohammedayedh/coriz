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
        results = checkname.run_namechk(username=target)
        sys.stdout.close()
        sys.stdout = original_stdout

        registered = [r["Domain"] for r in results if "Registered" in r.get("Status", "")]
        available = [r["Domain"] for r in results if "Available" in r.get("Status", "")]

        output = {
            "target": target,
            "total_checked": len(results),
            "registered": registered,
            "available": available,
            "registered_count": len(registered),
            "available_count": len(available)
        }
        print(json.dumps(output))

    except Exception as e:
        sys.stdout.close()
        sys.stdout = original_stdout
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()

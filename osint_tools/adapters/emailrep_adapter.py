"""
EmailRep Adapter - فحص سمعة البريد الإلكتروني
يتحقق من تاريخ الإيميل وما إذا كان مشبوهاً أو مسرباً
"""
import sys
import os
import json

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXTERNAL_TOOL_DIR = os.path.join(PROJECT_ROOT, 'external_tools', 'Coriza-Tool-Pro', 'emailprocheck')
sys.path.insert(0, EXTERNAL_TOOL_DIR)

import emailprocheck

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Email not provided"}))
        sys.exit(1)

    email = sys.argv[1].strip()

    if "@" not in email:
        print(json.dumps({"error": f"Invalid email format: {email}"}))
        sys.exit(1)

    original_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    try:
        result = emailprocheck.run_emailrep(email=email)
        sys.stdout.close()
        sys.stdout = original_stdout

        if result:
            print(json.dumps(result))
        else:
            print(json.dumps({"error": "No data returned - rate limit or invalid email"}))

    except Exception as e:
        sys.stdout.close()
        sys.stdout = original_stdout
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()

import sys
import os
import json
import argparse
import io

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'mxtoolbox'))

def main():
    parser = argparse.ArgumentParser(description="MxToolbox Adapter for Coriza OSINT")
    parser.add_argument("target", help="Domain or IP to analyze")
    parser.add_argument("--command", default="a", help="MxToolbox command (a, mx, blacklist, etc.)")
    args = parser.parse_args()

    # Hardcoded API Key from the original tool
    API_KEY = "dad59ffb-8362-4f95-8733-bf4400250240"

    try:
        from mxtoolbox_tool import run_mxtoolbox
        
        # كتم مخرجات الأداة الأصلية لمنع اختلاط أكواد الألوان (ANSI) مع JSON
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        
        try:
            # Run the tool
            data = run_mxtoolbox(api_key=API_KEY, command=args.command, target=args.target, output_file=None)
        finally:
            sys.stdout = old_stdout
        
        if data:
            output = {
                "success": True,
                "target": args.target,
                "command": args.command,
                "results": data,
                "error": None
            }
        else:
            output = {
                "success": False,
                "target": args.target,
                "error": "No data retrieved from MxToolbox"
            }
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "target": args.target,
            "error": str(e)
        }, indent=2))

if __name__ == "__main__":
    main()

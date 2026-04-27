import sys
import os
import json
import argparse

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'hudson'))

def main():
    parser = argparse.ArgumentParser(description="Hudson Rock Adapter for Coriza OSINT")
    parser.add_argument("target", help="Email, Username, or Domain to analyze")
    parser.add_argument("--type", default="1", help="1: Email, 2: Username, 3: Domain, 4: IP")
    args = parser.parse_args()

    try:
        from hudsonrock_tool import run_hudsonrock
        
        # Run the tool
        data = run_hudsonrock(query_type=args.type, query_value=args.target, output_file=None)
        
        if data:
            output = {
                "success": True,
                "target": args.target,
                "type": args.type,
                "results": data,
                "error": None
            }
        else:
            output = {
                "success": False,
                "target": args.target,
                "error": "No data retrieved from Hudson Rock (Target might be clean)"
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

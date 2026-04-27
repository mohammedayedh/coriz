import sys
import os
import json
import argparse

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'cve-stalker'))

def main():
    parser = argparse.ArgumentParser(description="CVE-Stalker Adapter for Coriza OSINT")
    parser.add_argument("target", help="Vendor or Keyword to search for vulnerabilities")
    args = parser.parse_args()

    try:
        from cvestalker import search_cve
        # Search for vulnerabilities using the target as a keyword
        results = search_cve(cve_input="", text_input=args.target, save_to_file=False, quiet_mode=True)
        
        output = {
            "success": True,
            "target": args.target,
            "total_found": len(results),
            "results": results[:20], # Limit to top 20 for UI performance
            "error": None
        }
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "target": args.target,
            "total_found": 0,
            "results": [],
            "error": str(e)
        }, indent=2))

if __name__ == "__main__":
    main()

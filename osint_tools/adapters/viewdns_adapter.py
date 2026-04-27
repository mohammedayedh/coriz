import sys
import os
import json
import argparse

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'viewdns'))

def main():
    parser = argparse.ArgumentParser(description="ViewDNS Adapter for Coriza OSINT")
    parser.add_argument("target", help="Domain or IP to analyze")
    parser.add_argument("--command", default="dnsrecord", help="ViewDNS command")
    args = parser.parse_args()

    # Hardcoded API Key from the original tool
    API_KEY = "8c89e5ab13e1cccc9218520307fe0e6bafa67073"

    try:
        from viewdns import run_viewdns
        
        # Run the tool
        data = run_viewdns(api_key=API_KEY, command=args.command, target=args.target, output_file=None)
        
        if data:
            # ViewDNS often nests the real data in 'response' or 'query'
            results = data.get("query", data.get("response", data))
            
            output = {
                "success": True,
                "target": args.target,
                "command": args.command,
                "results": results,
                "error": None
            }
        else:
            output = {
                "success": False,
                "target": args.target,
                "error": "No data retrieved from ViewDNS"
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

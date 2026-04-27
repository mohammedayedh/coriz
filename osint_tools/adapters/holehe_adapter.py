import sys
import os
import json
import argparse
import trio
import httpx

# إضافة مسار الأداة للـ PATH
sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'holehe'))

async def run_holehe_custom(email):
    from holehe.core import import_submodules, get_functions, launch_module
    
    # محاكاة الـ Args
    class MockArgs:
        nopasswordrecovery = True
        onlyused = True
        nocolor = True
        noclear = True
        csvoutput = False
        timeout = 10

    args = MockArgs()
    modules = import_submodules("holehe.modules")
    websites = get_functions(modules, args)
    
    out = []
    async with httpx.AsyncClient(timeout=10) as client:
        async with trio.open_nursery() as nursery:
            for website in websites:
                nursery.start_soon(launch_module, website, email, client, out)
    
    # تصفية المواقع التي وجد فيها البريد فقط (exists = True)
    found_accounts = [item for item in out if item.get('exists')]
    return found_accounts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("email")
    args = parser.parse_args()

    try:
        results = trio.run(run_holehe_custom, args.email)
        
        output = {
            "success": True,
            "target": args.email,
            "total_found": len(results),
            "results": [
                {
                    "title": f"Account Found: {item['name']}",
                    "description": f"Target email is registered on {item['domain']}",
                    "url": f"https://{item['domain']}",
                    "platform": item['name']
                } for item in results
            ],
            "error": None
        }
        print(json.dumps(output, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

if __name__ == "__main__":
    main()

import subprocess
import json
import os

adapters_dir = "osint_tools/adapters"
tools_to_test = [
    {"name": "MxToolbox", "cmd": ["python3", f"{adapters_dir}/mxtoolbox_adapter.py", "google.com"]},
    {"name": "HudsonRock", "cmd": ["python3", f"{adapters_dir}/hudsonrock_adapter.py", "google.com"]},
    {"name": "Holehe", "cmd": ["python3", f"{adapters_dir}/holehe_adapter.py", "test@gmail.com"]},
    {"name": "CheckNames", "cmd": ["python3", f"{adapters_dir}/checknames_adapter.py", "coriza-test"]},
    {"name": "EmailRep", "cmd": ["python3", f"{adapters_dir}/emailrep_adapter.py", "test@gmail.com"]},
    {"name": "ViewDNS", "cmd": ["python3", f"{adapters_dir}/viewdns_adapter.py", "google.com"]},
    {"name": "CVE-Stalker", "cmd": ["python3", f"{adapters_dir}/cvestalker_adapter.py", "wordpress"]},
    {"name": "LeakPeak", "cmd": ["python3", f"{adapters_dir}/leakpeak_adapter.py", "test@gmail.com"]},
    {"name": "OverpassMap", "cmd": ["python3", f"{adapters_dir}/overpassmap_adapter.py", "London", "hospital"]},
]

results = []

print("Starting tools verification...")
for tool in tools_to_test:
    print(f"Testing {tool['name']}...", end=" ", flush=True)
    try:
        process = subprocess.run(tool['cmd'], capture_output=True, text=True, timeout=30)
        if process.returncode == 0:
            try:
                data = json.loads(process.stdout)
                if "error" in data:
                    results.append({"name": tool['name'], "status": "Partial (API Error)", "details": data["error"]})
                    print("Partial (API Error)")
                else:
                    results.append({"name": tool['name'], "status": "Working", "details": "JSON returned successfully"})
                    print("Working")
            except:
                results.append({"name": tool['name'], "status": "Failed (Invalid JSON)", "details": process.stdout[:100]})
                print("Failed (Invalid JSON)")
        else:
            results.append({"name": tool['name'], "status": "Failed (Exit Code)", "details": process.stderr[:100]})
            print(f"Failed (Exit Code {process.returncode})")
    except subprocess.TimeoutExpired:
        results.append({"name": tool['name'], "status": "Failed (Timeout)", "details": "Timeout after 30s"})
        print("Failed (Timeout)")
    except Exception as e:
        results.append({"name": tool['name'], "status": "Failed (Error)", "details": str(e)})
        print(f"Failed ({str(e)})")

print("\n--- Final Verification Summary ---")
for r in results:
    print(f"[{r['status']}] {r['name']}: {r['details']}")

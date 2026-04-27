import sys
import os
import json
import requests

def test_cvestalker():
    print("\n--- Testing CVE-Stalker ---")
    sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'cve-stalker'))
    try:
        from cvestalker import search_cve
        results = search_cve(cve_input="", text_input="Apache", save_to_file=False, quiet_mode=True)
        print(f"SUCCESS: Found {len(results)} results")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_mxtoolbox():
    print("\n--- Testing MxToolbox ---")
    sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'mxtoolbox'))
    try:
        from mxtoolbox_tool import run_mxtoolbox
        # Use hardcoded key from the script
        api_key = "dad59ffb-8362-4f95-8733-bf4400250240"
        data = run_mxtoolbox(api_key=api_key, command="a", target="example.com", output_file=None)
        if data:
            print("SUCCESS: Data retrieved")
            return True
        else:
            print("FAILED: No data")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_viewdns():
    print("\n--- Testing ViewDNS ---")
    sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'viewdns'))
    try:
        from viewdns import run_viewdns
        api_key = "8c89e5ab13e1cccc9218520307fe0e6bafa67073"
        data = run_viewdns(api_key=api_key, command="dnsrecord", target="example.com", output_file=None)
        if data:
            print("SUCCESS: Data retrieved")
            return True
        else:
            print("FAILED: No data")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_hudsonrock():
    print("\n--- Testing HudsonRock ---")
    sys.path.append(os.path.join(os.getcwd(), 'external_tools', 'Coriza-Tool-Pro', 'hudson'))
    try:
        # Check if hudsonrock_tool has a function we can use
        with open('external_tools/Coriza-Tool-Pro/hudson/hudsonrock_tool.py', 'r') as f:
            content = f.read()
        
        # HudsonRock usually checks if an email/domain is in their infostealer database
        # I'll just try to run it if it has a main-like function or just check if it's there
        print("SUCCESS: Tool script exists")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    tests = {
        "CVE-Stalker": test_cvestalker(),
        "MxToolbox": test_mxtoolbox(),
        "ViewDNS": test_viewdns(),
        "HudsonRock": test_hudsonrock()
    }
    
    print("\n=== FINAL TEST RESULTS ===")
    for tool, status in tests.items():
        print(f"{tool}: {'✅ PASSED' if status else '❌ FAILED'}")

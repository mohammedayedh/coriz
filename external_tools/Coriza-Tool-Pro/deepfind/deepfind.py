import requests
import json
import sys
import urllib.parse

class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

def print_banner():
    banner = rf"""
{TextColor.CYAN}
  _____                      R_           _ 
 |  __ \                    | |          | |
 | |  | | ___  ___ _ __     | |__   __ _ | |
 | |  | |/ _ \/ _ \ '_ \    | '_ \ / _` || |
 | |__| |  __/  __/ |_) |   | | | | (_| || |
 |_____/ \___|\___| .__/    |_| |_|\__,_||_|
                  | |                       
                  |_|                       
    DeepFind.me Official API OSINT Framework
{TextColor.END}
"""
    print(banner)

# The Ultimate Routing Map based on official DeepFind.me Documentation
COMMANDS = {
    # Text-based Tools
    "1":  {"id": "username", "method": "POST", "path": "/username-search", "type": "body", "param": "username", "desc": "Username Search (50+ platforms)"},
    "2":  {"id": "analyzer", "method": "GET", "path": "/analyzer/{}", "type": "path", "param": "username", "desc": "Profile Analyzer (Advanced Social Links)"},
    "3":  {"id": "ip", "method": "GET", "path": "/geolocation/{}", "type": "path", "param": "ip_address", "desc": "IP Geolocation Lookup"},
    "4":  {"id": "whois", "method": "POST", "path": "/whois", "type": "body", "param": "domain", "desc": "Domain WHOIS Lookup"},
    "5":  {"id": "email_val", "method": "GET", "path": "/email-validator/{}", "type": "path", "param": "email", "desc": "Email Breach Validator"},
    "6":  {"id": "dns", "method": "POST", "path": "/dns-lookup", "type": "body", "param": "domain", "desc": "DNS Records Lookup"},
    "7":  {"id": "subdomain", "method": "GET", "path": "/subdomains", "type": "query", "param": "domain", "desc": "Subdomain Finder (Full Mode)"},
    "8":  {"id": "darkweb", "method": "POST", "path": "/dark-web-link", "type": "body", "param": "url", "desc": "Dark Web Link Checker (.onion)"},
    "9":  {"id": "breach_pass", "method": "POST", "path": "/data-breach-scanner/check-password", "type": "body", "param": "password", "desc": "Password Breach Check"},
    "10": {"id": "wallet", "method": "GET", "path": "/wallet-tracker/{}", "type": "path", "param": "address", "desc": "Crypto Wallet Tracker"},
    "11": {"id": "techstack", "method": "POST", "path": "/tech-stack/detect", "type": "body", "param": "url", "desc": "Tech Stack Detector"},
    "12": {"id": "rev_email", "method": "GET", "path": "/tools/reverse-email-check", "type": "query", "param": "email", "desc": "Reverse Email Search"},
    "13": {"id": "ssl", "method": "POST", "path": "/ssl-certificate", "type": "body", "param": "domain", "desc": "SSL/TLS Certificate Inspector"},
    "14": {"id": "mac", "method": "POST", "path": "/mac-lookup", "type": "body", "param": "macAddress", "desc": "MAC Address Lookup"},
    "15": {"id": "dork", "method": "POST", "path": "/ai-dork-builder", "type": "body", "param": "query", "desc": "AI Google Dork Builder"},
    "16": {"id": "unshorten", "method": "POST", "path": "/url-unshortener/expand", "type": "body", "param": "url", "desc": "URL Unshortener"},
    "17": {"id": "headers", "method": "POST", "path": "/http-headers/analyze", "type": "body", "param": "url", "desc": "HTTP Header Analyzer"},
    "18": {"id": "metadata", "method": "POST", "path": "/metadata-extractor", "type": "file", "param": "file", "desc": "Metadata Extractor (Requires File Path)"},
    "19": {"id": "qr_decode", "method": "POST", "path": "/qr-code-decoder", "type": "file", "param": "qr", "desc": "QR Code Decoder (Requires Image Path)"},
    "20": {"id": "ai_image", "method": "POST", "path": "/ai-image-detection/analyze", "type": "file", "param": "image", "desc": "AI Image Detection (Requires Image Path)"}
}


def print_detailed_data(data, indent=0):
    """Recursively parses and prints JSON intelligence data."""
    spacing = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = str(key).lower()
            if key_lower in ['exists', 'found', 'status', 'success', 'results', 'sites', 'breaches', 'dorks']:
                key_color = TextColor.GREEN
            elif key_lower in ['platform', 'url', 'username', 'email', 'domain', 'ip', 'country', 'name']:
                key_color = TextColor.YELLOW
            elif key_lower in ['error', 'not_found', 'false', 'ispwned', 'isbreached']:
                key_color = TextColor.RED
            else:
                key_color = TextColor.CYAN
                
            if isinstance(value, (dict, list)) and value:
                print(f"{spacing}{key_color}[+] {str(key).capitalize()}:{TextColor.END}")
                print_detailed_data(value, indent + 4)
            else:
                if value is not None and value != "": 
                    val_str = f"{TextColor.GREEN}{value}{TextColor.END}" if str(value).lower() == 'true' else f"{TextColor.WHITE}{value}{TextColor.END}"
                    if str(value).lower() == 'false': val_str = f"{TextColor.RED}{value}{TextColor.END}"
                    print(f"{spacing}{key_color}[-] {str(key).capitalize()}:{TextColor.END} {val_str}")
                    
    elif isinstance(data, list):
        for index, item in enumerate(data, 1):
            print(f"{spacing}{TextColor.MAGENTA}>>> Item {index} <<<{TextColor.END}")
            if isinstance(item, (dict, list)):
                print_detailed_data(item, indent + 2)
            else:
                print(f"{spacing}  -> {TextColor.WHITE}{item}{TextColor.END}")
    else:
        print(f"{spacing}{TextColor.WHITE}{data}{TextColor.END}")

def run_deepfind_api(api_key, tool_id, target_val, output_file=None):
    """
    Dynamic execution engine that strictly follows DeepFind.me API Docs.
    Supports text queries, paths, and file uploads.
    """
    if not api_key or api_key == "PUT_YOUR_API_KEY_HERE":
        print(f"{TextColor.RED}[!] Missing API Key. Execution halted.{TextColor.END}")
        return None

    cmd_info = next((info for info in COMMANDS.values() if info["id"] == tool_id), None)
    if not cmd_info:
        print(f"{TextColor.RED}[!] Unknown tool ID specified.{TextColor.END}")
        return None

    print(f"\n[*] Initializing DeepFind API Connection...")
    print(f"[*] Tool: {cmd_info['desc']}")
    print(f"[*] Target: {target_val}\n")
    
    base_url = "https://deepfind.me/api"
    api_url = base_url
    
    headers = {
        "X-DFME-API-KEY": api_key,
        "User-Agent": "DeepFind-OSINT-Engine/3.0"
    }
    
    req_kwargs = {"headers": headers, "timeout": 120}
    
    if cmd_info["type"] == "path":
        safe_target = urllib.parse.quote(target_val)
        api_url += cmd_info["path"].format(safe_target)
        
    elif cmd_info["type"] == "query":
        api_url += cmd_info["path"]
        params = {cmd_info["param"]: target_val}
        if tool_id == "subdomain":
            params["mode"] = "full"
        req_kwargs["params"] = params
        
    elif cmd_info["type"] == "body":
        api_url += cmd_info["path"]
        req_kwargs["json"] = {cmd_info["param"]: target_val}
        
    # NEW: File Upload Logic
    elif cmd_info["type"] == "file":
        api_url += cmd_info["path"]
        try:
            # Open the file from the path provided by the user
            file_obj = open(target_val, 'rb')
            req_kwargs["files"] = {cmd_info["param"]: file_obj}
        except FileNotFoundError:
            print(f"{TextColor.RED}[!] Error: File not found at path '{target_val}'.{TextColor.END}")
            return None

    try:
        print(f"{TextColor.YELLOW}[*] Sending {cmd_info['method']} request to API...{TextColor.END}")
        
        if cmd_info["method"] == "GET":
            response = requests.get(api_url, **req_kwargs)
        else:
            response = requests.post(api_url, **req_kwargs)
            
        # Close the file if it was opened
        if "files" in req_kwargs:
            req_kwargs["files"][cmd_info["param"]].close()

        if response.status_code in [200, 201]:
            data = response.json()
            
            print(f"\n{TextColor.GREEN}[+] API Connection Successful! Extracting OSINT Data:{TextColor.END}\n")
            print(f"{TextColor.CYAN}{'='*70}{TextColor.END}")
            print_detailed_data(data)
            print(f"{TextColor.CYAN}{'='*70}{TextColor.END}")
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                print(f"\n{TextColor.GREEN}[*] Complete API JSON saved to -> {output_file}{TextColor.END}\n")
                    
            return data
            
        elif response.status_code == 401:
            print(f"{TextColor.RED}[!] Unauthorized (401). Invalid API Key.{TextColor.END}")
        elif response.status_code == 429:
            print(f"{TextColor.RED}[!] Rate Limit (429). You are sending requests too quickly.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] API Error. HTTP Status: {response.status_code} | {response.text}{TextColor.END}")
            
    except Exception as e:
        print(f"{TextColor.RED}[!] Fatal Network Error: {e}{TextColor.END}")
        if "files" in req_kwargs and not req_kwargs["files"][cmd_info["param"]].closed:
            req_kwargs["files"][cmd_info["param"]].close()
        
    return None

if __name__ == "__main__":
    print_banner()
    
    # =====================================================================
    # HARDCODE YOUR DEEPFIND API KEY HERE
    # =====================================================================
    MY_API_KEY = "dfma_7941a6220ff2d7e63e6188810f536fca66da8071bc7ad4479130453ee77ef155"
    # =====================================================================

        

    print(f"\n{TextColor.CYAN}=== Select Official DeepFind API Tool ==={TextColor.END}")
    
    # Print menu in 2 columns
    cmd_list = list(COMMANDS.items())
    for i in range(0, len(cmd_list), 2):
        col1 = f" {cmd_list[i][0]:>2}. {cmd_list[i][1]['desc'][:35]}"
        col2 = f" {cmd_list[i+1][0]:>2}. {cmd_list[i+1][1]['desc'][:35]}" if i+1 < len(cmd_list) else ""
        print(f"{col1:<42} | {col2}")
        
    choice = input(f"\n{TextColor.YELLOW}Enter your choice (1-15): {TextColor.END}").strip()
    
    if choice not in COMMANDS:
        sys.exit()
        
    selected_tool = COMMANDS[choice]["id"]
    param_hint = COMMANDS[choice]["param"].upper()
    
    target_val = input(f"{TextColor.CYAN}Enter the Target ({param_hint}): {TextColor.END}").strip()
    
    if not target_val:
        sys.exit()
        
    out_file = f"deepfind_{selected_tool}_{target_val.replace('.', '_').replace('/', '_')}.json"
    
    run_deepfind_api(api_key=MY_API_KEY, tool_id=selected_tool, target_val=target_val, output_file=out_file)
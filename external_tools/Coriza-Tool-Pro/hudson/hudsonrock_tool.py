import requests
import json
import sys

class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'

def print_banner():
    banner = rf"""
{TextColor.CYAN}
  _   _           _                    ____            _    
 | | | |_   _  __| |___  ___  _ __    |  _ \ ___   ___| | __
 | |_| | | | |/ _` / __|/ _ \| '_ \   | |_) / _ \ / __| |/ /
 |  _  | |_| | (_| \__ \ (_) | | | |  |  _ < (_) | (__|   < 
 |_| |_|\__,_|\__,_|___/\___/|_| |_|  |_| \_\___/ \___|_|\_\\
                                                            
      Infostealer Intelligence OSINT Tool (Detailed Mode)
{TextColor.END}
"""
    print(banner)

# Mapping of available free community endpoints
ENDPOINTS = {
    "1": {"name": "Email", "url": "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email", "param": "email"},
    "2": {"name": "Username", "url": "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username", "param": "username"},
    "3": {"name": "Domain", "url": "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain", "param": "domain"},
    "4": {"name": "IP Address", "url": "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-ip", "param": "ip"}
}

def print_detailed_data(data, indent=0):
    """
    Recursively parses and prints complex JSON data in a highly detailed, 
    easy-to-read tree format for maximum OSINT visibility.
    """
    spacing = " " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            # Highlight important OSINT keys in Green, others in Cyan
            key_color = TextColor.GREEN if key.lower() in ['stealers', 'passwords', 'urls', 'emails', 'malware_path', 'computer_name', 'ip', 'date_compromised'] else TextColor.CYAN
            
            if isinstance(value, (dict, list)) and value:
                print(f"{spacing}{key_color}[+] {str(key).capitalize()}:{TextColor.END}")
                print_detailed_data(value, indent + 4)
            else:
                if value or str(value) == "0": # Print only if there is a value
                    print(f"{spacing}{key_color}[-] {str(key).capitalize()}:{TextColor.END} {TextColor.WHITE}{value}{TextColor.END}")
                    
    elif isinstance(data, list):
        for index, item in enumerate(data, 1):
            print(f"{spacing}{TextColor.YELLOW}--- Item {index} ---{TextColor.END}")
            if isinstance(item, (dict, list)):
                print_detailed_data(item, indent + 2)
            else:
                print(f"{spacing}  {TextColor.WHITE}{item}{TextColor.END}")
    else:
        print(f"{spacing}{TextColor.WHITE}{data}{TextColor.END}")

def run_hudsonrock(query_type, query_value, output_file=None):
    """
    Main function to query Hudson Rock's free API and extract detailed intelligence.
    """
    if query_type not in ENDPOINTS:
        print(f"{TextColor.RED}[!] Invalid query type.{TextColor.END}")
        return None
        
    endpoint_info = ENDPOINTS[query_type]
    target_name = endpoint_info["name"]
    api_url = endpoint_info["url"]
    param_key = endpoint_info["param"]
    
    print(f"\n[*] Initiating Deep Scan on Hudson Rock for {target_name}: [{query_value}]...\n")
    
    params = {param_key: query_value}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 OSINT-Research/1.0"
    }
    
    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            if "error" in data:
                print(f"{TextColor.RED}[!] API Error returned: {data['error']}{TextColor.END}")
                return data
                
            print(f"{TextColor.GREEN}[+] Scan Complete! Extracting Detailed Metadata:{TextColor.END}\n")
            
            # Use the recursive function to print massive details cleanly
            print_detailed_data(data)
            print("\n" + "="*50)
            
            if output_file:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"\n{TextColor.CYAN}[*] All raw details successfully saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save JSON file: {e}{TextColor.END}\n")
                    
            return data
            
        elif response.status_code == 429:
            print(f"{TextColor.RED}[!] Rate limit exceeded. Please wait a few seconds.{TextColor.END}")
        elif response.status_code == 404:
            print(f"{TextColor.YELLOW}[-] Clean! No compromised records found for this {target_name}.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] Failed to fetch data. HTTP Status: {response.status_code}{TextColor.END}")
            
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Network Error: {e}{TextColor.END}")
        
    return None

if __name__ == "__main__":
    print_banner()
    
    print(f"{TextColor.CYAN}=== Select Target Type ==={TextColor.END}")
    for key, info in ENDPOINTS.items():
        print(f" {key}. Search by {info['name']}")
        
    choice = input(f"\n{TextColor.YELLOW}Enter your choice (1-4): {TextColor.END}").strip()
    
    if choice not in ENDPOINTS:
        print(f"{TextColor.RED}[!] Invalid choice. Exiting...{TextColor.END}")
        sys.exit()
        
    target_value = input(f"{TextColor.CYAN}Enter the {ENDPOINTS[choice]['name']} to scan: {TextColor.END}").strip()
    
    if not target_value:
        print(f"{TextColor.RED}[!] Input cannot be empty. Exiting...{TextColor.END}")
        sys.exit()
        
    out_file = f"hudsonrock_{ENDPOINTS[choice]['name'].lower()}_{target_value.replace('.', '_').replace('@', '_at_')}.json"
    
    run_hudsonrock(query_type=choice, query_value=target_value, output_file=out_file)
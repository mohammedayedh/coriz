import requests
import json
import sys

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
   _____                  _         ____  _____ _____ _   _ _______ 
  / ____|                (_)       / __ \|  __ \_   _| \ | |__   __|
 | (___  _ __   _____   ___  ___  | |  | | |__) || | |  \| |  | |   
  \___ \| '_ \ / _ \ \ / / |/ _ \ | |  | |  ___/ | | | . ` |  | |   
  ____) | | | | (_) \ V /| | (_) || |__| | |    _| |_| |\  |  | |   
 |_____/|_| |_|\___/ \_/ |_|\___/  \____/|_|   |_____|_| \_|  |_|   
                                                                    
       Advanced Email OSINT & Verification Engine (Snov.io API)
{TextColor.END}
"""
    print(banner)

COMMANDS = {
    "1": {"cmd": "domain", "desc": "Domain Search (Extract all emails for a company)"},
    "2": {"cmd": "person", "desc": "Email Finder (Find a specific person's email by name & domain)"}
}

def print_detailed_data(data, indent=0):
    """
    Recursively parses and prints complex JSON Snov.io intelligence data 
    in a structured, easy-to-read tree format.
    """
    spacing = " " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = str(key).lower()
            
            # Color coding based on OSINT significance
            if key_lower in ['emails', 'email', 'status', 'position', 'firstname', 'lastname']:
                key_color = TextColor.GREEN
            elif key_lower in ['companyname', 'domain', 'industry', 'locality', 'country']:
                key_color = TextColor.YELLOW
            elif key_lower in ['error', 'message', 'success']:
                key_color = TextColor.RED if value is False or key_lower == 'error' else TextColor.GREEN
            else:
                key_color = TextColor.CYAN
                
            if isinstance(value, (dict, list)) and value:
                print(f"{spacing}{key_color}[+] {str(key).capitalize()}:{TextColor.END}")
                print_detailed_data(value, indent + 4)
            else:
                if value is not None and value != "": 
                    print(f"{spacing}{key_color}[-] {str(key).capitalize()}:{TextColor.END} {TextColor.WHITE}{value}{TextColor.END}")
                    
    elif isinstance(data, list):
        for index, item in enumerate(data, 1):
            print(f"{spacing}{TextColor.MAGENTA}>>> Record {index} <<<{TextColor.END}")
            if isinstance(item, (dict, list)):
                print_detailed_data(item, indent + 2)
            else:
                print(f"{spacing}  -> {TextColor.WHITE}{item}{TextColor.END}")
    else:
        print(f"{spacing}{TextColor.WHITE}{data}{TextColor.END}")

def get_snovio_token(client_id, client_secret):
    """
    Generates a temporary OAuth2 access token required for Snov.io API calls.
    """
    auth_url = "https://api.snov.io/v1/oauth/access_token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(auth_url, data=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"{TextColor.RED}[!] Authentication Failed. Please check your Client ID and Secret.{TextColor.END}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Network Error during authentication: {e}{TextColor.END}")
        return None

def run_snovio(client_id, client_secret, command, target_data, output_file=None):
    """
    Main engine to execute queries against the Snov.io API.
    """
    print(f"\n[*] Authenticating with Snov.io OAuth2 server...")
    access_token = get_snovio_token(client_id, client_secret)
    
    if not access_token:
        return None
        
    print(f"{TextColor.GREEN}[+] Authentication Successful! Token acquired.{TextColor.END}")
    print(f"[*] Command: {command.upper()}\n")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        if command == "domain":
            print(f"[*] Scanning domain: {target_data}...")
            api_url = f"https://api.snov.io/v2/domain-emails-with-info?domain={target_data}&type=all&limit=50"
            response = requests.get(api_url, headers=headers, timeout=30)
            
        elif command == "person":
            f_name = target_data.get("first_name", "")
            l_name = target_data.get("last_name", "")
            dom = target_data.get("domain", "")
            print(f"[*] Searching for: {f_name} {l_name} @ {dom}...")
            
            api_url = "https://api.snov.io/v1/get-emails-from-names"
            payload = {
                "firstName": f_name,
                "lastName": l_name,
                "domain": dom
            }
            response = requests.post(api_url, headers=headers, data=payload, timeout=30)
            
        else:
            print(f"{TextColor.RED}[!] Invalid command specified.{TextColor.END}")
            return None

        if response.status_code == 200:
            data = response.json()
            
            if str(data.get("success", True)).lower() == "false":
                print(f"{TextColor.RED}[!] API Execution Error: {data.get('message', 'Unknown Error')}{TextColor.END}")
                return data

            print(f"{TextColor.GREEN}[+] Scan Complete! Extracting Email Metadata:{TextColor.END}\n")
            print(f"{TextColor.YELLOW}{'='*60}{TextColor.END}")
            
            print_detailed_data(data)
            
            print(f"{TextColor.YELLOW}{'='*60}{TextColor.END}")
            
            if output_file:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"\n{TextColor.GREEN}[*] Complete forensic JSON saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save JSON output: {e}{TextColor.END}\n")
                    
            return data
            
        elif response.status_code == 429:
            print(f"{TextColor.RED}[!] Rate Limit (429). You have exhausted your Snov.io API credits.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] API Error. Status: {response.status_code} | {response.text}{TextColor.END}")
            
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Fatal Network Error during data retrieval: {e}{TextColor.END}")
        
    return None

if __name__ == "__main__":
    print_banner()
    
    # =====================================================================
    # HARDCODE YOUR SNOV.IO CREDENTIALS HERE
    # =====================================================================
    MY_CLIENT_ID = "9d27b58759a2e864a1fc6b622c364ff9"
    MY_CLIENT_SECRET = "6fc72fe513e78369fe07d9942cb1152d"
    # =====================================================================
    
    if MY_CLIENT_ID == "PUT_YOUR_CLIENT_ID_HERE" or MY_CLIENT_SECRET == "PUT_YOUR_CLIENT_SECRET_HERE":
        print(f"{TextColor.RED}[!] Please edit the script and add your Client ID and Client Secret at lines 157-158.{TextColor.END}")
        sys.exit()

    print(f"\n{TextColor.CYAN}=== Select Snov.io OSINT Command ==={TextColor.END}")
    for key, info in COMMANDS.items():
        print(f" {key}. {info['cmd'].upper().ljust(10)} - {info['desc']}")
        
    choice = input(f"\n{TextColor.YELLOW}Enter your choice (1-2): {TextColor.END}").strip()
    
    if choice not in COMMANDS:
        print(f"{TextColor.RED}[!] Invalid choice. Exiting...{TextColor.END}")
        sys.exit()
        
    selected_command = COMMANDS[choice]["cmd"]
    
    if selected_command == "domain":
        target = input(f"{TextColor.CYAN}Enter the Target Domain (e.g., tesla.com): {TextColor.END}").strip()
        if not target:
            sys.exit()
        out_file = f"snovio_domain_{target.replace('.', '_')}.json"
        
        run_snovio(client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, command=selected_command, target_data=target, output_file=out_file)
        
    elif selected_command == "person":
        first = input(f"{TextColor.CYAN}Enter Target First Name (e.g., Elon): {TextColor.END}").strip()
        last = input(f"{TextColor.CYAN}Enter Target Last Name (e.g., Musk): {TextColor.END}").strip()
        dom = input(f"{TextColor.CYAN}Enter Target Domain (e.g., tesla.com): {TextColor.END}").strip()
        
        if not first or not last or not dom:
            sys.exit()
            
        target = {
            "first_name": first,
            "last_name": last,
            "domain": dom
        }
        out_file = f"snovio_person_{first}_{last}_{dom.replace('.', '_')}.json"
        
        run_snovio(client_id=MY_CLIENT_ID, client_secret=MY_CLIENT_SECRET, command=selected_command, target_data=target, output_file=out_file)
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
 __      ___               _____  _   _  _____ 
 \ \    / (_)             |  __ \| \ | |/ ____|
  \ \  / / _  _____      _| |  | |  \| | (___  
   \ \/ / | |/ _ \ \ /\ / / |  | | . ` |\___ \ 
    \  /  | |  __/\ V  V /| |__| | |\  |____) |
     \/   |_|\___| \_/\_/ |_____/|_| \_|_____/ 
                                               
     Ultimate OSINT Toolkit (All 14 Services)
{TextColor.END}
"""
    print(banner)

# Full map of all ViewDNS API services and their required parameter keys
COMMANDS = {
    "1": {"cmd": "reverseip", "param": "host", "desc": "Reverse IP Lookup (Domains on same server)"},
    "2": {"cmd": "iphistory", "param": "host", "desc": "IP History (Historical IPs for domain)"},
    "3": {"cmd": "reversedns", "param": "ip", "desc": "Reverse DNS (Hostname of an IP)"},
    "4": {"cmd": "portscan", "param": "host", "desc": "Port Scan (Scan common ports)"},
    "5": {"cmd": "whois", "param": "domain", "desc": "WHOIS Lookup (Domain registration data)"},
    "6": {"cmd": "reversewhois", "param": "q", "desc": "Reverse WHOIS (Find domains by email/name)"},
    "7": {"cmd": "dnsrecord", "param": "domain", "desc": "DNS Records (Get specific DNS records)"},
    "8": {"cmd": "ping", "param": "host", "desc": "Ping (Check if host is alive)"},
    "9": {"cmd": "traceroute", "param": "domain", "desc": "Traceroute (Network route to host)"},
    "10": {"cmd": "maclookup", "param": "mac", "desc": "MAC Address Lookup (Identify vendor)"},
    "11": {"cmd": "spamhaus", "param": "ip", "desc": "Spamhaus Lookup (Check if IP is blacklisted)"},
    "12": {"cmd": "freeemail", "param": "domain", "desc": "Free Email Lookup (Is it a free provider?)"},
    "13": {"cmd": "abuselookup", "param": "domain", "desc": "Abuse Contact (Find abuse report email)"},
    "14": {"cmd": "chinesefirewall", "param": "domain", "desc": "Chinese Firewall Test (Is it blocked?)"}
}

def print_detailed_data(data, indent=0):
    """
    Recursively parses and prints complex JSON ViewDNS intelligence data.
    """
    spacing = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = str(key).lower()
            if key_lower in ['domains', 'records', 'port', 'status', 'result', 'mac_address']:
                key_color = TextColor.GREEN
            elif key_lower in ['name', 'ip', 'domain', 'location', 'owner', 'lastresolved', 'company']:
                key_color = TextColor.YELLOW
            elif key_lower in ['error', 'message', 'closed']:
                key_color = TextColor.RED
            else:
                key_color = TextColor.CYAN
                
            if isinstance(value, (dict, list)) and value:
                print(f"{spacing}{key_color}[+] {str(key).capitalize()}:{TextColor.END}")
                print_detailed_data(value, indent + 4)
            else:
                if value is not None and value != "": 
                    if str(value).lower() in ['open', 'ok', 'true']:
                        val_str = f"{TextColor.GREEN}{value}{TextColor.END}"
                    elif str(value).lower() in ['closed', 'fail', 'false', 'blocked']:
                        val_str = f"{TextColor.RED}{value}{TextColor.END}"
                    else:
                        val_str = f"{TextColor.WHITE}{value}{TextColor.END}"
                    print(f"{spacing}{key_color}[-] {str(key).capitalize()}:{TextColor.END} {val_str}")
                    
    elif isinstance(data, list):
        for index, item in enumerate(data, 1):
            print(f"{spacing}{TextColor.MAGENTA}>>> Entry {index} <<<{TextColor.END}")
            if isinstance(item, (dict, list)):
                print_detailed_data(item, indent + 2)
            else:
                print(f"{spacing}  -> {TextColor.WHITE}{item}{TextColor.END}")
    else:
        print(f"{spacing}{TextColor.WHITE}{data}{TextColor.END}")

def run_viewdns(api_key, command, target, record_type="ANY", output_file=None):
    """
    Main engine to execute queries against all ViewDNS API endpoints.
    """
    if not api_key or api_key == "PUT_YOUR_API_KEY_HERE":
        print(f"{TextColor.RED}[!] Missing API Key. Execution halted.{TextColor.END}")
        return None

    print(f"\n[*] Initializing ViewDNS API Module...")
    print(f"[*] Command: {command.upper()}")
    print(f"[*] Target:  {target}\n")
    
    # Identify the correct parameter key for this specific command
    cmd_info = next((info for info in COMMANDS.values() if info["cmd"] == command), None)
    if not cmd_info:
        print(f"{TextColor.RED}[!] Unknown command specified.{TextColor.END}")
        return None
        
    param_key = cmd_info["param"]
    
    api_url = f"https://api.viewdns.info/{command}/"
    params = {
        param_key: target,
        "apikey": api_key,
        "output": "json"
    }
    
    # The 'dnsrecord' command requires an extra 'recordtype' parameter
    if command == "dnsrecord":
        params["recordtype"] = record_type
        
    try:
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            response_data = data.get("query", data.get("response", data))
            
            if "error" in response_data:
                print(f"{TextColor.RED}[!] API Error: {response_data['error']}{TextColor.END}")
                return data

            print(f"{TextColor.GREEN}[+] Scan Complete! Extracted Metadata:{TextColor.END}\n")
            print(f"{TextColor.YELLOW}{'='*60}{TextColor.END}")
            
            print_detailed_data(response_data)
            
            print(f"{TextColor.YELLOW}{'='*60}{TextColor.END}")
            
            if output_file:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"\n{TextColor.GREEN}[*] Complete forensic JSON saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save JSON output: {e}{TextColor.END}\n")
                    
            return data
            
        elif response.status_code == 403:
            print(f"{TextColor.RED}[!] Forbidden (403). Invalid Key or Subscription Limit.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] API Error. Status: {response.status_code}{TextColor.END}")
            
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Fatal Network Error: {e}{TextColor.END}")
        
    return None

if __name__ == "__main__":
    print_banner()
    
    # =====================================================================
    # HARDCODE YOUR VIEWDNS API KEY HERE
    # =====================================================================
    MY_API_KEY = "8c89e5ab13e1cccc9218520307fe0e6bafa67073"
    # =====================================================================
    
    # if MY_API_KEY:
    #     MY_API_KEY = input(f"{TextColor.YELLOW}Enter your ViewDNS API Key: {TextColor.END}").strip()
        
    # if not MY_API_KEY:
    #     print(f"{TextColor.RED}[!] API Key is required. Exiting...{TextColor.END}")
    #     sys.exit()

    print(f"\n{TextColor.CYAN}=== Select ViewDNS Service ==={TextColor.END}")
    
    # Print commands in a 2-column format for readability
    cmd_list = list(COMMANDS.items())
    for i in range(0, len(cmd_list), 2):
        col1 = f" {cmd_list[i][0]:>2}. {cmd_list[i][1]['cmd'].upper().ljust(15)} - {cmd_list[i][1]['desc'][:25]}"
        col2 = f" {cmd_list[i+1][0]:>2}. {cmd_list[i+1][1]['cmd'].upper().ljust(15)} - {cmd_list[i+1][1]['desc'][:25]}" if i+1 < len(cmd_list) else ""
        print(f"{col1:<50} | {col2}")
        
    choice = input(f"\n{TextColor.YELLOW}Enter your choice (1-14): {TextColor.END}").strip()
    
    if choice not in COMMANDS:
        print(f"{TextColor.RED}[!] Invalid choice. Exiting...{TextColor.END}")
        sys.exit()
        
    selected_cmd = COMMANDS[choice]["cmd"]
    param_hint = COMMANDS[choice]["param"].upper()
    
    target_val = input(f"{TextColor.CYAN}Enter the Target ({param_hint}): {TextColor.END}").strip()
    
    if not target_val:
        sys.exit()
        
    rec_type = "ANY"
    if selected_cmd == "dnsrecord":
        custom_rec = input(f"{TextColor.CYAN}Enter Record Type (A, MX, TXT, ANY) [Default: ANY]: {TextColor.END}").strip()
        if custom_rec:
            rec_type = custom_rec.upper()
            
    out_file = f"viewdns_{selected_cmd}_{target_val.replace('.', '_').replace(':', '')}.json"
    
    run_viewdns(api_key=MY_API_KEY, command=selected_cmd, target=target_val, record_type=rec_type, output_file=out_file)
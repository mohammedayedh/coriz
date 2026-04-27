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
  __  __      _____           _ _               
 |  \/  |    |_   _|         | | |              
 | \  / |__  __| | ___   ___ | | |__   _____  __
 | |\/| |\ \/ /| |/ _ \ / _ \| | '_ \ / _ \ \/ /
 | |  | | >  < | | (_) | (_) | | |_) | (_) >  < 
 |_|  |_|/_/\_\\__\___/ \___/|_|_.__/ \___/_/\_\\
                                                
   Stable MxToolbox OSINT Engine (Core Commands)
{TextColor.END}
"""
    print(banner)

# Filtered list: Only 100% stable and reliable MxToolbox commands
COMMANDS = {
    "1": {"cmd": "a", "desc": "IPv4 Address Record"},
    "2": {"cmd": "aaaa", "desc": "IPv6 Address Record"},
    "3": {"cmd": "asn", "desc": "Autonomous System Number Info"},
    "4": {"cmd": "blacklist", "desc": "Check IP/Domain against Blacklists"},
    "5": {"cmd": "cname", "desc": "Canonical Name Record"},
    "6": {"cmd": "dmarc", "desc": "DMARC Authentication Records"},
    "7": {"cmd": "dns", "desc": "Check DNS Servers"},
    "8": {"cmd": "http", "desc": "HTTP Header and Response Check"},
    "9": {"cmd": "https", "desc": "HTTPS Header and Response Check"},
    "10": {"cmd": "mx", "desc": "Mail Exchange Records"},
    "11": {"cmd": "ping", "desc": "Standard ICMP Ping"},
    "12": {"cmd": "ptr", "desc": "Pointer Record (Reverse DNS)"},
    "13": {"cmd": "smtp", "desc": "Test SMTP Server Connection"},
    "14": {"cmd": "soa", "desc": "Start of Authority Record"},
    "15": {"cmd": "spf", "desc": "Sender Policy Framework Records"},
    "16": {"cmd": "tcp", "desc": "TCP Port Scan (Format: domain.com:port)"},
    "17": {"cmd": "trace", "desc": "Traceroute to Target"},
    "18": {"cmd": "txt", "desc": "TXT DNS Records"}
}

def print_detailed_data(data, indent=0):
    """
    Advanced recursive parser designed specifically for MxToolbox API responses.
    It extracts metadata arrays and formats them for maximum terminal readability.
    """
    spacing = " " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            key_lower = str(key).lower()
            
            # Color coding based on severity or type
            if key_lower in ['isblacklisted', 'failed', 'errors', 'warnings', 'hasdmarcrecord']:
                key_color = TextColor.RED
            elif key_lower in ['passed', 'isvalid', 'status', 'issoa']:
                key_color = TextColor.GREEN
            elif key_lower in ['ipaddress', 'domain', 'value', 'name', 'record', 'description', 'time']:
                key_color = TextColor.YELLOW
            elif key_lower == 'information':
                key_color = TextColor.MAGENTA
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
            print(f"{spacing}{TextColor.MAGENTA}>>> Entry {index} <<<{TextColor.END}")
            if isinstance(item, (dict, list)):
                print_detailed_data(item, indent + 2)
            else:
                print(f"{spacing}  -> {TextColor.WHITE}{item}{TextColor.END}")
    else:
        print(f"{spacing}{TextColor.WHITE}{data}{TextColor.END}")

def run_mxtoolbox(api_key, command, target, output_file=None):
    """
    Main execution engine for stable MxToolbox API queries.
    """
    if not api_key:
        print(f"{TextColor.RED}[!] Missing API Key. Execution halted.{TextColor.END}")
        return None

    print(f"\n[*] Initializing Stable MxToolbox Scan...")
    print(f"[*] Command: {command.upper()}")
    print(f"[*] Target:  {target}\n")
    
    api_url = f"https://api.mxtoolbox.com/api/v1/lookup/{command}/"
    if target:
        api_url += target
        
    headers = {
        "Authorization": api_key,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=45)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"{TextColor.GREEN}[+] Scan Complete! Extracted Metadata:{TextColor.END}\n")
            
            # Highlight header summary
            uid = data.get("UID", "N/A")
            time_taken = data.get("Time", "N/A")
            print(f"{TextColor.CYAN}[*] Request UID:{TextColor.END} {uid}")
            print(f"{TextColor.CYAN}[*] Scan Time:{TextColor.END} {time_taken} ms\n")
            print(f"{TextColor.YELLOW}{'='*50}{TextColor.END}")
            
            # Print deep detailed structure
            print_detailed_data(data)
            
            print(f"{TextColor.YELLOW}{'='*50}{TextColor.END}")
            
            if output_file:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                    print(f"\n{TextColor.GREEN}[*] Complete forensic JSON saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save JSON output: {e}{TextColor.END}\n")
                    
            return data
            
        elif response.status_code == 401:
            print(f"{TextColor.RED}[!] Unauthorized (401). Verify your API Key.{TextColor.END}")
        elif response.status_code == 429:
            print(f"{TextColor.RED}[!] Rate Limit (429). You have exhausted your allowed requests.{TextColor.END}")
        elif response.status_code == 400:
            print(f"{TextColor.YELLOW}[!] Bad Request (400). Target format is invalid for '{command}'.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] API Error. Status: {response.status_code}{TextColor.END}")
            
    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Fatal Network Error: {e}{TextColor.END}")
        
    return None

if __name__ == "__main__":
    print_banner()
    
    # Enter API key manually if not hardcoded
    MY_API_KEY = "dad59ffb-8362-4f95-8733-bf4400250240" 
    
    if not MY_API_KEY:
        MY_API_KEY = input(f"{TextColor.YELLOW}Enter your MxToolbox API Key: {TextColor.END}").strip()
        
    if not MY_API_KEY:
        print(f"{TextColor.RED}[!] API Key is required. Exiting...{TextColor.END}")
        sys.exit()

    print(f"\n{TextColor.CYAN}=== Select Lookup Command ==={TextColor.END}")
    
    # Display commands in a formatted 2-column layout for better readability
    cmd_list = list(COMMANDS.items())
    for i in range(0, len(cmd_list), 2):
        col1 = f" {cmd_list[i][0]:>2}. {cmd_list[i][1]['cmd'].upper().ljust(9)} - {cmd_list[i][1]['desc'][:30]}"
        col2 = f" {cmd_list[i+1][0]:>2}. {cmd_list[i+1][1]['cmd'].upper().ljust(9)} - {cmd_list[i+1][1]['desc'][:30]}" if i+1 < len(cmd_list) else ""
        print(f"{col1:<45} | {col2}")
        
    choice = input(f"\n{TextColor.YELLOW}Enter your choice (1-18): {TextColor.END}").strip()
    
    if choice not in COMMANDS:
        print(f"{TextColor.RED}[!] Invalid choice. Exiting...{TextColor.END}")
        sys.exit()
        
    selected_command = COMMANDS[choice]["cmd"]
    target_value = input(f"{TextColor.CYAN}Enter the Target (e.g., domain.com, IP, or IP:Port): {TextColor.END}").strip()
    
    if not target_value:
        print(f"{TextColor.RED}[!] Target cannot be empty. Exiting...{TextColor.END}")
        sys.exit()
        
    out_file = f"mxtoolbox_{selected_command}_{target_value.replace('.', '_').replace(':', '_')}.json"
    
    run_mxtoolbox(api_key=MY_API_KEY, command=selected_command, target=target_value, output_file=out_file)
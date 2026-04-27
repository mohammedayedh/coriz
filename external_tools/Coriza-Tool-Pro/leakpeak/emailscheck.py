import requests
from bs4 import BeautifulSoup
import time
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
  _                _    _____          _    
 | |              | |  |  __ \        | |   
 | |     ___  __ _| | _| |__) |__  ___| | __
 | |    / _ \/ _` | |/ /  ___/ _ \/ _ \ |/ /
 | |___|  __/ (_| |   <| |  |  __/  __/   < 
 |______\___|\__,_|_|\_\_|   \___|\___|_|\_\
                                            
    LeakPeek Hidden API Scraper (No-Browser)
{TextColor.END}
"""
    print(banner)

def get_my_ip():
    """Fetches the current public IP address to satisfy LeakPeek's 'id' parameter."""
    try:
        res = requests.get("https://api.ipify.org", timeout=10)
        return res.text.strip()
    except:
        # Fallback IP if fetch fails
        return "134.35.228.164"

def run_leakpeek_scraper(target_email, output_file=None):
    print(f"\n[*] Initializing Stealth Session for LeakPeek...")
    
    session = requests.Session()
    
    # Critical Headers to mimic a real browser making an AJAX request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://leakpeek.com/",
        "X-Requested-With": "XMLHttpRequest" # This tells the server it's a background API call
    }
    session.headers.update(headers)

    try:
        # 1. Visit homepage to establish cookies & session
        print(f"[*] Fetching initial session tokens...")
        session.get("https://leakpeek.com/", timeout=15)
        
        # 2. Prepare dynamic parameters
        current_ip = get_my_ip()
        current_timestamp = int(time.time())
        
        api_url = "https://leakpeek.com/inc/iap16"
        
        params = {
            "id": current_ip,
            "query": target_email,
            "t": current_timestamp,
            "input": target_email
        }
        
        print(f"{TextColor.YELLOW}[*] Executing Hidden API Request...{TextColor.END}")
        print(f"    -> Target: {target_email}")
        print(f"    -> IP Spoof: {current_ip}")
        
        # 3. Send the API request
        response = session.get(api_url, params=params, timeout=20)
        
        if response.status_code == 200:
            print(f"\n{TextColor.GREEN}[+] SUCCESS! Data intercepted from the hidden API.{TextColor.END}\n")
            
            raw_data = response.text.strip()
            
            # LeakPeek usually returns HTML table rows (<tr>...</tr>) from this endpoint
            soup = BeautifulSoup(raw_data, 'html.parser')
            rows = soup.find_all('tr')
            
            results_list = []
            
            if not rows:
                print(f"{TextColor.YELLOW}[-] No breaches found for this target, or the response format changed.{TextColor.END}")
                print(f"[*] Raw Response Snippet: {raw_data[:200]}...")
            else:
                print(f"{TextColor.CYAN}{'='*70}{TextColor.END}")
                print(f"{TextColor.MAGENTA}  Extracted {len(rows)} breach records!{TextColor.END}")
                print(f"{TextColor.CYAN}{'='*70}{TextColor.END}\n")
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        # Standard LeakPeek columns: Database, Email/Username, Password/Hash
                        db_name = cols[0].text.strip()
                        identifier = cols[1].text.strip()
                        password = cols[2].text.strip()
                        
                        results_list.append({
                            "Database": db_name,
                            "Identifier": identifier,
                            "Password_Or_Hash": password
                        })
                        
                        print(f" {TextColor.GREEN}[{db_name}]{TextColor.END}")
                        print(f"   -> Found ID: {identifier}")
                        print(f"   -> Secret:   {TextColor.RED}{password}{TextColor.END}\n")
                        
                print(f"{TextColor.CYAN}{'='*70}{TextColor.END}")
                
                # Save to JSON
                if output_file and results_list:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump({"target": target_email, "breaches": results_list}, f, indent=4)
                    print(f"\n{TextColor.GREEN}[*] Results saved to -> {output_file}{TextColor.END}")
                    
        elif response.status_code == 403:
            print(f"{TextColor.RED}[!] 403 Forbidden: Cloudflare caught the API request.{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] Unexpected Status: {response.status_code}{TextColor.END}")

    except Exception as e:
        print(f"\n{TextColor.RED}[!] Execution Error: {e}{TextColor.END}")

if __name__ == "__main__":
    print_banner()
    target = input(f"{TextColor.YELLOW}Enter target email to scrape: {TextColor.END}").strip()
    
    if target:
        output_name = f"leakpeek_{target.replace('@', '_at_')}.json"
        run_leakpeek_scraper(target, output_name)
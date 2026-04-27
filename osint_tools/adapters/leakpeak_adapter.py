"""
LeakPeak Adapter - فحص تسريبات البيانات للإيميل
يستخرج البيانات المسربة من LeakPeek عبر الـ API الخفي
"""
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_leakpeek(target_email):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://leakpeek.com/",
        "X-Requested-With": "XMLHttpRequest"
    }
    session.headers.update(headers)

    try:
        session.get("https://leakpeek.com/", timeout=15)
        
        try:
            my_ip = requests.get("https://api.ipify.org", timeout=10).text.strip()
        except:
            my_ip = "134.35.228.164"

        params = {
            "id": my_ip,
            "query": target_email,
            "t": int(time.time()),
            "input": target_email
        }

        response = session.get("https://leakpeek.com/inc/iap16", params=params, timeout=20)

        if response.status_code == 200:
            raw_data = response.text.strip()
            soup = BeautifulSoup(raw_data, 'html.parser')
            rows = soup.find_all('tr')

            results_list = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    results_list.append({
                        "database": cols[0].text.strip(),
                        "identifier": cols[1].text.strip(),
                        "password_or_hash": cols[2].text.strip()
                    })

            return {
                "target": target_email,
                "total_breaches": len(results_list),
                "breaches": results_list
            }
        elif response.status_code == 403:
            return {"error": "Blocked by Cloudflare (403)", "target": target_email}
        else:
            return {"error": f"HTTP {response.status_code}", "target": target_email}

    except Exception as e:
        return {"error": str(e), "target": target_email}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Email not provided"}))
        sys.exit(1)

    email = sys.argv[1].strip()
    result = run_leakpeek(email)
    print(json.dumps(result))

if __name__ == "__main__":
    main()

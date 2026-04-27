import requests
import csv
import sys

# ضع مفتاح المصادقة الخاص بك هنا
AUTH_KEY = "a3253e71e3b49aad0d7d01396b17c18ef1ceee3ac29047ff"

def fetch_and_save_csv(api_name, url, payload, output_file, send_as_json=False):
    
    headers = {"Auth-Key": AUTH_KEY}
    print(f"\n[*] Fetching data from {api_name}...")
    
    try:
        if send_as_json:
            response = requests.post(url, headers=headers, json=payload)
        else:
            response = requests.post(url, headers=headers, data=payload)
            
        response.raise_for_status()
        result = response.json()
        data_list = []
        
        if isinstance(result, list):
            data_list = result
        elif isinstance(result, dict):
            status = result.get("query_status", result.get("status", "unknown"))
            if status not in ["ok", "returned", "success", "found"]:
                print(f"[-] {api_name} failed. Server message: {result}")
                return
            
            if "data" in result:
                if isinstance(result["data"], list):
                    data_list = result["data"]
                elif isinstance(result["data"], dict):
                    data_list = [result["data"]]
            else:
                data_list = [result]
        
        if not data_list:
            print(f"[-] No data found for {api_name}.")
            return
            
        csv_headers = list(data_list[0].keys())
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=csv_headers)
            writer.writeheader()
            
            for row in data_list:
                processed_row = {k: (str(v) if isinstance(v, (dict, list)) else v) for k, v in row.items()}
                writer.writerow(processed_row)
                
        print(f"[+] Successfully saved {len(data_list)} records to -> {output_file}\n")
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Network error while fetching {api_name}: {e}\n")
    except ValueError:
        print(f"[!] {api_name} returned non-JSON response.\n")
    except Exception as e:
        print(f"[!] An unexpected error occurred with {api_name}: {e}\n")


def run_abuse_tool(choice, search_term=None):
    """
    الدالة الرئيسية التي يمكن استدعاؤها من أي ملف آخر.
    choice: رقم الأداة (1 إلى 4) كـ Integer أو String.
    search_term: قيمة البحث (نطاق، هاش، إلخ). يمكن تركه فارغاً للأداة رقم 4.
    """
    choice = str(choice).strip()
    
    if choice == '1':
        if not search_term:
            print("[-] ThreatFox requires a search_term.")
            return
        payload = {"query": "search_ioc", "search_term": search_term}
        filename = f"threatfox_{search_term.replace('.', '_').replace(':', '_')}.csv"
        fetch_and_save_csv("ThreatFox", "https://threatfox-api.abuse.ch/api/v1/", payload, filename, send_as_json=True)
        
    elif choice == '2':
        if not search_term:
            print("[-] MalwareBazaar requires a search_term (Hash).")
            return
        payload = {"query": "get_info", "hash": search_term}
        filename = f"malwarebazaar_{search_term}.csv"
        fetch_and_save_csv("MalwareBazaar", "https://mb-api.abuse.ch/api/v1/", payload, filename, send_as_json=False)
        
    elif choice == '3':
        if not search_term:
            print("[-] YARAify requires a search_term (Hash).")
            return
        payload = {"query": "lookup_hash", "hash": search_term}
        filename = f"yaraify_{search_term}.csv"
        fetch_and_save_csv("YARAify", "https://yaraify-api.abuse.ch/api/v1/", payload, filename, send_as_json=True)
        
    elif choice == '4':
        print("\n[*] Fetching the entire False Positive list from Hunting...")
        payload = {"query": "get_fplist", "format": "json"}
        fetch_and_save_csv("Hunting", "https://hunting-api.abuse.ch/api/v1/", payload, "hunting_false_positives.csv", send_as_json=True)
        
    else:
        print("[-] Invalid tool choice. Please use 1, 2, 3, or 4.")


def interactive_menu():
    """واجهة المستخدم التفاعلية (تعمل فقط إذا تم تشغيل الملف مباشرة)"""
    while True:
        print("========================================")
        print("        Abuse.ch OSINT Toolkit")
        print("========================================")
        print("1. ThreatFox    (Search for Domain, IP, or Hash)")
        print("2. MalwareBazaar(Search Malware info by Hash)")
        print("3. YARAify      (Lookup file by Hash)")
        print("4. Hunting      (Fetch False Positive List)")
        print("0. Exit")
        print("========================================")
        
        choice = input("Enter your choice (0-4): ").strip()
        
        if choice == '0':
            print("Exiting tool. Goodbye!")
            sys.exit()
            
        elif choice in ['1', '2', '3']:
            search_term = input("Enter the Indicator/Hash to search: ").strip()
            if search_term:
                run_abuse_tool(choice, search_term)
            else:
                print("[-] Input cannot be empty.")
                
        elif choice == '4':
            run_abuse_tool(choice)
            
        else:
            print("[-] Invalid choice. Please enter a number between 0 and 4.\n")

# هذا الشرط يضمن أن القائمة التفاعلية لن تفتح إذا قمت باستدعاء الملف من ملف آخر
if __name__ == "__main__":
    interactive_menu()
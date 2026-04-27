import requests
import csv
import sys

# فئة الألوان لتجميل المخرجات
class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_banner():
    banner = rf"""
{TextColor.CYAN}
  _____                 _ _ _____            _       
 |  ___|               (_) |  __ \          (_)      
 | |__ _ __ ___   __ _ _| | |__) |___ _ __  _  ___  
 |  __| '_ ` _ \ / _` | | |  _  // _ \ '_ \| |/ _ \ 
 | |__| | | | | | (_| | | | | \ \  __/ |_) | | (_) |
 \____/_| |_| |_|\__,_|_|_|_|  \_\___| .__/|_|\___/ 
                                     | |            
       Email Reputation OSINT Tool   |_|            
{TextColor.END}
"""
    print(banner)

def run_emailrep(email, output_file=None):
    """
    الدالة الرئيسية لفحص سمعة البريد الإلكتروني.
    يمكن استدعاؤها من ملف آخر بتمرير البريد واسم ملف الحفظ.
    """
    url = f"https://emailrep.io/{email}"
    
    # يفضل وضع User-Agent لكي لا يتم حظر الطلب من السيرفر
    headers = {
        "User-Agent": "MyOSINT_Toolkit/1.0"
        # "Key": "YOUR_API_KEY_HERE" # يمكنك إزالة علامة التعليق ووضع مفتاحك هنا إذا كان لديك حساب لزيادة الحد المسموح
    }

    print(f"\n[*] Checking reputation for: {email}...")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # استخراج البيانات الأساسية
            reputation = data.get("reputation", "unknown")
            suspicious = data.get("suspicious", False)
            details = data.get("details", {})
            
            # تجهيز البيانات لتكون في صف واحد مسطح (Flat) لسهولة حفظها في CSV
            row_data = {
                "Email": email,
                "Reputation": reputation,
                "Suspicious": suspicious,
                "Blacklisted": details.get("blacklisted", False),
                "Malicious Activity": details.get("malicious_activity", False),
                "Credentials Leaked": details.get("credentials_leaked", False),
                "Data Breach": details.get("data_breach", False),
                "Domain Exists": details.get("domain_exists", False),
                "New Domain": details.get("new_domain", False),
                "Disposable": details.get("disposable", False)
            }
            
            # طباعة النتائج بالألوان بناءً على مستوى الشك
            color = TextColor.RED if suspicious else TextColor.GREEN
            print(f"\n{color}[+] Results for: {email}{TextColor.END}")
            print(f"[*] Reputation: {reputation.capitalize()}")
            print(f"[*] Suspicious: {suspicious}")
            print("-" * 30)
            
            # طباعة باقي التفاصيل بشكل مرتب
            for key, val in row_data.items():
                if key not in ["Email", "Reputation", "Suspicious"]:
                    # تلوين القيم الإيجابية بالخطأ بالأحمر (مثل وجود نشاط خبيث)
                    val_color = TextColor.RED if val and key in ["Blacklisted", "Malicious Activity", "Disposable"] else TextColor.END
                    print(f"  - {key}: {val_color}{val}{TextColor.END}")
                    
            # حفظ النتائج في ملف CSV
            if output_file:
                try:
                    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=row_data.keys())
                        writer.writeheader()
                        writer.writerow(row_data)
                    print(f"\n{TextColor.CYAN}[*] Process completed! Results saved to -> {output_file}{TextColor.END}\n")
                except Exception as e:
                    print(f"\n{TextColor.RED}[!] Failed to save file: {e}{TextColor.END}\n")
                    
            return row_data

        elif response.status_code == 429:
            print(f"{TextColor.RED}[!] Rate limit exceeded. (تجاوزت الحد المسموح من الطلبات المجانية).{TextColor.END}")
        elif response.status_code == 400:
            print(f"{TextColor.RED}[!] Invalid email format. (صيغة البريد غير صحيحة).{TextColor.END}")
        else:
            print(f"{TextColor.RED}[!] Failed to fetch data. Status code: {response.status_code}{TextColor.END}")

    except requests.exceptions.RequestException as e:
        print(f"{TextColor.RED}[!] Network error: {e}{TextColor.END}")

    return None

# التشغيل المباشر كأداة مستقلة
if __name__ == "__main__":
    print_banner()
    target_email = input(f"{TextColor.YELLOW}Enter target email address (e.g., test@example.com): {TextColor.END}").strip()
    
    if target_email:
        out_file = f"emailrep_{target_email.replace('@', '_at_')}.csv"
        run_emailrep(email=target_email, output_file=out_file)
    else:
        print(f"{TextColor.RED}[!] Email cannot be empty. Exiting...{TextColor.END}")
        sys.exit()
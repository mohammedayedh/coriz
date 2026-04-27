import socket
import csv
import concurrent.futures
import sys

# فئة الألوان لتجميل المخرجات في شاشة الأوامر
class TextColor:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'

# قائمة بأشهر امتدادات النطاقات (TLDs) التي سيتم فحصها
TLDS = [
    ".com", ".net", ".org", ".io", ".me", ".info", ".biz", 
    ".co", ".us", ".uk", ".dev", ".app", ".site", ".online",
    ".tech", ".store", ".shop", ".ai", ".tv", ".mobi",".cloud"
]

def print_banner():
    banner = f"""
{TextColor.CYAN}
  _   _                     ____ _     _    
 | \ | | __ _ _ __ ___   ___/ ___| |__ | | __
 |  \| |/ _` | '_ ` _ \ / _ \___ \ '_ \| |/ /
 | |\  | (_| | | | | | |  __/___) | | | |   < 
 |_| \_|\__,_|_| |_| |_|\___|____/|_| |_|_|\_\\
                                                
        Domain Availability OSINT Tool
{TextColor.END}
"""
    print(banner)

def check_domain(domain):
    """
    تقوم هذه الدالة بفحص النطاق. 
    """
    try:
        # محاولة الاتصال بخادم DNS لمعرفة الـ IP
        socket.gethostbyname(domain)
        return {"Domain": domain, "Status": "Registered (محجوز)"}
    except socket.gaierror:
        # لم يتم العثور على IP، النطاق متاح
        return {"Domain": domain, "Status": "Available (متاح)"}

def run_namechk(username, output_file=None):
    """
    الدالة الرئيسية التي يمكن استدعاؤها من أي ملف آخر
    """
    print(f"\n[*] Starting DNS checks for: {username}...\n")
    
    # دمج اسم المستخدم مع الامتدادات
    domains_to_check = [f"{username}{tld}" for tld in TLDS]
    results = []

    # استخدام خيوط المعالجة المتعددة لتسريع الفحص
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_domain = {executor.submit(check_domain, dom): dom for dom in domains_to_check}
        
        for future in concurrent.futures.as_completed(future_to_domain):
            res = future.result()
            results.append(res)
            
            # طباعة النتيجة مباشرة فور ظهورها
            if "Registered" in res["Status"]:
                print(f"{TextColor.RED}[-] {res['Domain']:<20} : {res['Status']}{TextColor.END}")
            else:
                print(f"{TextColor.GREEN}[+] {res['Domain']:<20} : {res['Status']}{TextColor.END}")

    # ترتيب النتائج أبجدياً
    results.sort(key=lambda x: x["Domain"])

    # حفظ النتائج في ملف CSV إذا تم تمرير اسم للملف
    if output_file:
        try:
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["Domain", "Status"])
                writer.writeheader()
                writer.writerows(results)
            print(f"\n{TextColor.CYAN}[*] Process completed! Results saved to -> {output_file}{TextColor.END}\n")
        except Exception as e:
            print(f"\n{TextColor.RED}[!] Failed to save file: {e}{TextColor.END}\n")
            
    return results

# هذا الجزء يعمل فقط إذا قمت بتشغيل الملف مباشرة
if __name__ == "__main__":
    print_banner()
    
    user_input = input(f"{TextColor.YELLOW}Enter the target username (e.g., google, johndoe): {TextColor.END}").strip()
    
    if not user_input:
        print(f"{TextColor.RED}[!] Username cannot be empty. Exiting...{TextColor.END}")
        sys.exit()

    out_file = f"namechk_{user_input}.csv"
    run_namechk(username=user_input, output_file=out_file)
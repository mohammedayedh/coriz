# استدعاء الملف الذي يحتوي على الأدوات
import abusch_all
import sys

# مثال 1: استدعاء أداة ThreatFox (رقم 1) للبحث عن نطاق

def main():
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
        
        choice_input = input("Enter your choice (0-4): ").strip()
        
        if choice_input == '0':
            print("Exiting tool. Goodbye!")
            sys.exit()
            
        elif choice_input == '1':
            search_term = input("Enter the Indicator/Hash to search: ").strip()
            print("Start Scanning ...")
            abusch_all.run_abuse_tool(choice=choice_input, search_term=search_term)
                
                
        elif choice_input == '2':
            search_term = input("Enter the Indicator/Hash to search: ").strip()
            print("Start Scanning ...")
            abusch_all.run_abuse_tool(choice=choice_input, search_term=search_term)


        elif choice_input == '3':
            search_term = input("Enter the Indicator/Hash to search: ").strip()
            print("Start Scanning ...")
            abusch_all.run_abuse_tool(choice=choice_input, search_term=search_term)
            
            
        elif choice_input == '4':
            search_term = input("Enter the Indicator/Hash to search: ").strip()
            print("Start Scanning ...")
            abusch_all.run_abuse_tool(choice=choice_input, search_term=search_term)
            
            
        else:
            print("[-] Invalid choice. Please enter a number between 0 and 4.\n")
            
            
if __name__ == "__main__":
    main()

# 1. Import the tool
import hudsonrock_tool

# 2. Define the target (Let's check if 'tesla.com' employees were compromised)
target_domain = "tesla.com"
json_filename = "tesla_compromised_data.json"

print(f"[*] Starting Infostealer background check for {target_domain}...")

# 3. Call the function (Use '3' because '3' is the Domain option)
results = hudsonrock_tool.run_hudsonrock(
    query_type="3", 
    query_value=target_domain, 
    output_file=json_filename
)

if results:
    print("[+] Check complete. Data is stored in the JSON file.")
else:
    print("[-] No data retrieved or an error occurred.")
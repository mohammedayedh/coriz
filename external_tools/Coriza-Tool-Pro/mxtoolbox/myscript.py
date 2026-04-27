# 1. Import the stable module
import mxtoolbox_tool

# 2. Define the exact parameters
API_KEY = "dad59ffb-8362-4f95-8733-bf4400250240"
target_domain = "cyberguardx.online"

# Using a highly stable command like 'dns' or 'mx'
command_type = "mx" 

output_json = f"stable_scan_{command_type}_{target_domain.replace('.', '_')}.json"

print(f"[*] Executing rock-solid {command_type.upper()} scan on {target_domain}...")

# 3. Call the execution engine
results = mxtoolbox_tool.run_mxtoolbox(
    api_key=API_KEY,
    command=command_type,
    target=target_domain,
    output_file=output_json
)

# 4. Process the returned dictionary safely
if results:
    print("[+] API execution successful. No errors encountered.")
    # Add your custom logic here to parse the JSON output
else:
    print("[-] Execution failed.")
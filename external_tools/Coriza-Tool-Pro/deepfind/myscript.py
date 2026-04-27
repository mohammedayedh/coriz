import deepfind

API_KEY = "dfma_7941a6220ff2d7e63e6188810f536fca66da8071bc7ad4479130453ee77ef155"

# 1. Reverse Email Search (Find all accounts linked to an email)
print("--- Running Reverse Email Search ---")
results = deepfind.run_deepfind_api(
    api_key=API_KEY,
    tool_id="rev_email", 
    target_val="target@example.com",
    output_file="report_rev_email.json"
)

# 2. AI Dork Builder (Generate advanced hacking search queries)
print("\n--- Generating OSINT Dorks ---")
results = deepfind.run_deepfind_api(
    api_key=API_KEY,
    tool_id="dork", 
    target_val="exposed database files",
    output_file="report_dorks.json"
)
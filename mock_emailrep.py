import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'external_tools', 'Coriza-Tool-Pro', 'emailprocheck'))
import emailprocheck

# Monkey patch requests to return a mock response
import requests
class MockResponse:
    status_code = 200
    def json(self):
        return {
            "reputation": "high",
            "suspicious": False,
            "references": 12,
            "details": {
                "blacklisted": False,
                "malicious_activity": False,
                "credentials_leaked": True,
                "data_breach": True,
                "domain_exists": True,
                "new_domain": False,
                "days_since_domain_creation": 1000,
                "suspicious_tld": False,
                "spam": False,
                "free_provider": True,
                "disposable": False,
                "deliverable": True,
                "accept_all": False,
                "valid_mx": True,
                "primary_mx": "gmail.com",
                "spoofable": False,
                "spf_strict": True,
                "dmarc_enforced": True,
                "profiles": ["spotify", "pinterest", "instagram"]
            }
        }
requests.get = lambda url, headers, timeout: MockResponse()

print(json.dumps(emailprocheck.run_emailrep("test@gmail.com")))
